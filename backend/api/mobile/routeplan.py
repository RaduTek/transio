"""Routes for route and journey planning in the mobile app"""

from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from backend.config import settings
from backend.database import get_session
from backend.data.transit import (
    TransitRoute,
    TransitStop,
    TransitSubRoute,
    TransitSubRouteStop,
)


router = APIRouter()


class PlanJourneyRequest(BaseModel):
    stop_ids: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="Ordered list of transit stop IDs the passenger wants to visit.",
    )


class JourneyLeg(BaseModel):
    route_id: str = Field(description="ID of the transit route to take for this leg.")
    board_stop_id: str = Field(description="Stop ID where the passenger boards.")
    alight_stop_id: str = Field(description="Stop ID where the passenger hops off.")


class PlanJourneyResponse(BaseModel):
    legs: list[JourneyLeg]


def _build_tools(db_session: Session) -> list:
    """Build Gemini tool callables bound to the current DB session."""

    def get_stop_details(stop_id: str) -> dict:
        """Get name, coordinates and address for a transit stop by its ID.

        Args:
            stop_id: The unique ID of the transit stop.
        """
        stop = db_session.exec(
            select(TransitStop).where(TransitStop.id == stop_id)
        ).first()
        if not stop:
            return {"error": f"Stop {stop_id} not found"}
        return {
            "id": stop.id,
            "name": stop.name,
            "description": stop.description,
            "lat": stop.lat,
            "lon": stop.lon,
            "address": stop.address,
        }

    def get_subroutes_serving_stop(stop_id: str) -> list[dict]:
        """List every subroute that calls at the given stop, with its parent route.

        Use this to discover which transit routes a passenger can board at a stop.

        Args:
            stop_id: The unique ID of the transit stop.
        """
        stmt = (
            select(TransitSubRoute, TransitRoute)
            .join(
                TransitSubRouteStop,
                TransitSubRouteStop.subroute_id == TransitSubRoute.id,
            )
            .join(TransitRoute, TransitRoute.id == TransitSubRoute.parent_route_id)
            .where(TransitSubRouteStop.stop_id == stop_id)
        )
        return [
            {
                "subroute_id": sr.id,
                "subroute_code": sr.code,
                "subroute_name": sr.name,
                "route_id": r.id,
                "route_code": r.code,
                "route_name": r.name,
            }
            for sr, r in db_session.exec(stmt).all()
        ]

    def get_stops_on_subroute(subroute_id: str) -> list[dict]:
        """Get the ordered list of stops served by a subroute.

        The `stop_order` value indicates the direction of travel along the
        subroute; a passenger can only board and alight in increasing order.

        Args:
            subroute_id: The unique ID of the subroute.
        """
        stmt = (
            select(TransitSubRouteStop, TransitStop)
            .join(TransitStop, TransitStop.id == TransitSubRouteStop.stop_id)
            .where(TransitSubRouteStop.subroute_id == subroute_id)
            .order_by(TransitSubRouteStop.stop_order)
        )
        return [
            {
                "stop_order": ss.stop_order,
                "stop_id": st.id,
                "stop_name": st.name,
                "lat": st.lat,
                "lon": st.lon,
            }
            for ss, st in db_session.exec(stmt).all()
        ]

    def get_subroutes_for_route(route_id: str) -> list[dict]:
        """List all subroutes belonging to a transit route.

        Args:
            route_id: The unique ID of the parent transit route.
        """
        stmt = select(TransitSubRoute).where(
            TransitSubRoute.parent_route_id == route_id
        )
        return [
            {"subroute_id": sr.id, "subroute_code": sr.code, "subroute_name": sr.name}
            for sr in db_session.exec(stmt).all()
        ]

    return [
        get_stop_details,
        get_subroutes_serving_stop,
        get_stops_on_subroute,
        get_subroutes_for_route,
    ]


@router.post("/plan_journey")
async def plan_journey(
    body: PlanJourneyRequest,
    db_session: Session = Depends(get_session),
) -> PlanJourneyResponse:
    """Plan a journey between up to 5 transit stops using public transportation."""

    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    stops = db_session.exec(
        select(TransitStop).where(TransitStop.id.in_(body.stop_ids))
    ).all()
    found_ids = {s.id for s in stops}
    missing = [sid for sid in body.stop_ids if sid not in found_ids]
    if missing:
        raise HTTPException(status_code=404, detail=f"Stops not found: {missing}")

    stops_by_id = {s.id: s for s in stops}
    stop_lines = [
        f"{i + 1}. {stops_by_id[sid].name} (id={sid})"
        for i, sid in enumerate(body.stop_ids)
    ]

    prompt = (
        "You are a public transit journey planner. The passenger wants to visit "
        "the following stops, in this exact order:\n"
        + "\n".join(stop_lines)
        + "\n\nUse the provided tools to discover which transit routes serve each "
        "stop and the order of stops along each subroute. Then produce a sequence "
        "of trip legs that takes the passenger from the first stop to the last.\n\n"
        "Rules:\n"
        "- Each leg uses a single transit route (the TransitRoute, not the subroute).\n"
        "- For a leg to be valid, the board stop and the alight stop must lie on "
        "the same subroute, with the alight stop having a strictly greater "
        "stop_order than the board stop.\n"
        "- Chain multiple legs to transfer between routes when no single route "
        "connects two consecutive requested stops.\n"
        "- The alight stop of one leg should be the board stop of the next leg "
        "(or the same physical stop, if a transfer is needed).\n"
        "- The first leg must board at the first requested stop; the last leg "
        "must alight at the last requested stop; every intermediate requested "
        "stop must appear as either a board or an alight stop along the way.\n"
        "- Use the route_id (not the subroute_id or any code) in the response.\n"
    )

    client = genai.Client(api_key=settings.gemini_api_key)

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=_build_tools(db_session),
            response_mime_type="application/json",
            response_schema=PlanJourneyResponse,
        ),
    )

    parsed = response.parsed
    if isinstance(parsed, PlanJourneyResponse):
        return parsed
    if isinstance(parsed, dict):
        return PlanJourneyResponse.model_validate(parsed)

    raise HTTPException(
        status_code=502,
        detail="AI did not return a valid journey plan",
    )