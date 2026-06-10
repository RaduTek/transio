"""Transit info routes"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

from backend.data.transit import (
    TransitCategory,
    TransitRoute,
    TransitStop,
    TransitSubRoute,
    TransitSubRouteStop,
)
from backend.database import get_session

router = APIRouter(tags=["Transit info routes"])


def _get_by_id_or_404(
    db_session: Session,
    model: Any,
    entity_id: str,
    not_found_message: str,
):
    stmt = select(model).where(model.id == entity_id).limit(1)
    entity = db_session.exec(stmt).first()

    if not entity:
        raise HTTPException(404, not_found_message)

    return entity


def _get_by_id_or_code_or_404(
    db_session: Session,
    model: Any,
    entity_id_or_code: str,
    not_found_message: str,
):
    stmt = select(model).where(or_(
        model.id == entity_id_or_code,
        model.code == entity_id_or_code,
    )).limit(1)
    entity = db_session.exec(stmt).first()

    if not entity:
        raise HTTPException(404, not_found_message)

    return entity


# region Transit stops

@router.get("/stops")
def get_stops(db_session: Session = Depends(get_session)) -> list[TransitStop]:
    """Get transit stops."""

    stmt = select(TransitStop).order_by(TransitStop.name)

    return list(db_session.exec(stmt).all())


@router.get("/stops/{stop_id}")
def get_stop(
    stop_id: str,
    db_session: Session = Depends(get_session)
) -> TransitStop | None:
    """Get a transit stop by ID."""

    return _get_by_id_or_404(db_session, TransitStop, stop_id, "Transit stop not found")


# endregion


# region Transit categories

@router.get("/categories")
def get_categories(db_session: Session = Depends(get_session)) -> list[TransitCategory]:
    """Get transit categories."""

    stmt = select(TransitCategory).order_by(TransitCategory.code)

    return list(db_session.exec(stmt).all())


@router.get("/categories/{category_id_or_code}")
def get_category(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> TransitCategory | None:
    """Get a transit category by ID or code."""

    return _get_by_id_or_code_or_404(
        db_session,
        TransitCategory,
        category_id_or_code,
        "Transit category not found",
    )


@router.get("/categories/{category_id_or_code}/routes")
def get_category_routes(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> list[TransitRoute]:
    """Get all routes for a transit category."""

    category = _get_by_id_or_code_or_404(
        db_session,
        TransitCategory,
        category_id_or_code,
        "Transit category not found",
    )

    routes_stmt = select(TransitRoute) \
        .where(TransitRoute.category_id == category.id) \
        .order_by(TransitRoute.code)

    return list(db_session.exec(routes_stmt).all())


# endregion


# region Transit routes

@router.get("/routes")
def get_routes(db_session: Session = Depends(get_session)) -> list[TransitRoute]:
    """Get transit routes."""

    stmt = select(TransitRoute).order_by(TransitRoute.code)

    return list(db_session.exec(stmt).all())


@router.get("/routes/{route_id_or_code}")
def get_route(
    route_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> TransitRoute | None:
    """Get a transit route by ID or code."""

    return _get_by_id_or_code_or_404(
        db_session,
        TransitRoute,
        route_id_or_code,
        "Transit route not found",
    )


@router.get("/routes/{route_id_or_code}/subroutes")
def get_route_subroutes(
    route_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> list[TransitSubRoute]:
    """Get all subroutes for a transit route."""

    route = _get_by_id_or_code_or_404(
        db_session,
        TransitRoute,
        route_id_or_code,
        "Transit route not found",
    )

    subroutes_stmt = select(TransitSubRoute) \
        .where(TransitSubRoute.parent_route_id == route.id) \
        .order_by(TransitSubRoute.code)

    return list(db_session.exec(subroutes_stmt).all())


# endregion


# region Transit subroutes

@router.get("/subroutes/{subroute_id_or_code}")
def get_subroute(
    subroute_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> TransitSubRoute | None:
    """Get a transit subroute by ID or code."""

    return _get_by_id_or_code_or_404(
        db_session,
        TransitSubRoute,
        subroute_id_or_code,
        "Transit subroute not found",
    )


@router.get("/subroutes/{subroute_id_or_code}/stops")
def get_subroute_stops(
    subroute_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> list[dict]:
    """Get all stop mappings for a transit subroute."""

    subroute = _get_by_id_or_code_or_404(
        db_session,
        TransitSubRoute,
        subroute_id_or_code,
        "Transit subroute not found",
    )

    subroute_stops_stmt = select(TransitSubRouteStop, TransitStop) \
        .join(TransitStop, TransitSubRouteStop.stop_id == TransitStop.id) \
        .where(TransitSubRouteStop.subroute_id == subroute.id) \
        .order_by(TransitSubRouteStop.stop_order)

    results = db_session.exec(subroute_stops_stmt).all()

    return [
        {**subroute_stop.model_dump(), "stop": stop.model_dump()}
        for subroute_stop, stop in results
    ]


# endregion


# region Transit subroute-stops

@router.get("/subroute-stops/{subroute_stop_id}")
def get_subroute_stop(
    subroute_stop_id: str,
    db_session: Session = Depends(get_session)
) -> TransitSubRouteStop | None:
    """Get a transit subroute-stop mapping by ID."""

    return _get_by_id_or_404(
        db_session,
        TransitSubRouteStop,
        subroute_stop_id,
        "Transit subroute stop not found",
    )


# endregion
