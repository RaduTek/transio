"""Transit info routes"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, or_
from sqlalchemy.exc import IntegrityError

from backend.data.transit import (
    TransitCategory,
    TransitRoute,
    TransitStop,
    TransitSubRoute,
    TransitSubRouteStop,
)
from backend.database import get_session

router = APIRouter(prefix="/transit", tags=["Admin Transit Routes"])


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


@router.post("/stops")
def create_stop(
    stop: TransitStop,
    db_session: Session = Depends(get_session)
) -> TransitStop:
    """Create a new transit stop."""

    db_session.add(stop)
    db_session.commit()
    db_session.refresh(stop)

    return stop


@router.patch("/stops/{stop_id}")
def update_stop(
    stop_id: str,
    stop_data: TransitStop,
    db_session: Session = Depends(get_session)
) -> TransitStop | None:
    """Update a transit stop."""

    stop = _get_by_id_or_404(db_session, TransitStop, stop_id, "Transit stop not found")

    for field, value in stop_data.model_dump(exclude_unset=True).items():
        setattr(stop, field, value)

    db_session.add(stop)
    db_session.commit()
    db_session.refresh(stop)

    return stop


@router.delete("/stops/{stop_id}")
def delete_stop(
    stop_id: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit stop."""

    stop = _get_by_id_or_404(db_session, TransitStop, stop_id, "Transit stop not found")

    db_session.delete(stop)
    db_session.commit()


# endregion


#region Transit categories

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

@router.post("/categories")
def create_category(
    category: TransitCategory,
    db_session: Session = Depends(get_session)
) -> TransitCategory:
    """Create a new transit category."""

    try:
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit category with this code already exists")

    return category

@router.patch("/categories/{category_id_or_code}")
def update_category(
    category_id_or_code: str,
    category_data: TransitCategory,
    db_session: Session = Depends(get_session)
) -> TransitCategory | None:
    """Update a transit category."""

    category = _get_by_id_or_code_or_404(
        db_session,
        TransitCategory,
        category_id_or_code,
        "Transit category not found",
    )

    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    return category

@router.delete("/categories/{category_id_or_code}")
def delete_category(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit category."""

    category = _get_by_id_or_code_or_404(
        db_session,
        TransitCategory,
        category_id_or_code,
        "Transit category not found",
    )

    db_session.delete(category)
    db_session.commit()

#endregion


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


@router.post("/routes")
def create_route(
    route: TransitRoute,
    db_session: Session = Depends(get_session)
) -> TransitRoute:
    """Create a new transit route."""

    try:
        db_session.add(route)
        db_session.commit()
        db_session.refresh(route)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit route with this code already exists")

    return route


@router.patch("/routes/{route_id_or_code}")
def update_route(
    route_id_or_code: str,
    route_data: TransitRoute,
    db_session: Session = Depends(get_session)
) -> TransitRoute | None:
    """Update a transit route."""

    route = _get_by_id_or_code_or_404(
        db_session,
        TransitRoute,
        route_id_or_code,
        "Transit route not found",
    )

    for field, value in route_data.model_dump(exclude_unset=True).items():
        setattr(route, field, value)

    try:
        db_session.add(route)
        db_session.commit()
        db_session.refresh(route)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit route with this code already exists")

    return route


@router.delete("/routes/{route_id_or_code}")
def delete_route(
    route_id_or_code: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit route."""

    route = _get_by_id_or_code_or_404(
        db_session,
        TransitRoute,
        route_id_or_code,
        "Transit route not found",
    )

    db_session.delete(route)
    db_session.commit()


# endregion


# region Transit subroutes

@router.get("/subroutes")
def get_subroutes(db_session: Session = Depends(get_session)) -> list[TransitSubRoute]:
    """Get transit subroutes."""

    stmt = select(TransitSubRoute).order_by(TransitSubRoute.code)

    return list(db_session.exec(stmt).all())


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
) -> list[TransitSubRouteStop]:
    """Get all stop mappings for a transit subroute."""

    subroute = _get_by_id_or_code_or_404(
        db_session,
        TransitSubRoute,
        subroute_id_or_code,
        "Transit subroute not found",
    )

    subroute_stops_stmt = select(TransitSubRouteStop) \
        .where(TransitSubRouteStop.subroute_id == subroute.id) \
        .order_by(TransitSubRouteStop.stop_order)

    return list(db_session.exec(subroute_stops_stmt).all())


@router.post("/subroutes")
def create_subroute(
    subroute: TransitSubRoute,
    db_session: Session = Depends(get_session)
) -> TransitSubRoute:
    """Create a new transit subroute."""

    try:
        db_session.add(subroute)
        db_session.commit()
        db_session.refresh(subroute)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit subroute with this code already exists")

    return subroute


@router.patch("/subroutes/{subroute_id_or_code}")
def update_subroute(
    subroute_id_or_code: str,
    subroute_data: TransitSubRoute,
    db_session: Session = Depends(get_session)
) -> TransitSubRoute | None:
    """Update a transit subroute."""

    subroute = _get_by_id_or_code_or_404(
        db_session,
        TransitSubRoute,
        subroute_id_or_code,
        "Transit subroute not found",
    )

    for field, value in subroute_data.model_dump(exclude_unset=True).items():
        setattr(subroute, field, value)

    try:
        db_session.add(subroute)
        db_session.commit()
        db_session.refresh(subroute)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit subroute with this code already exists")

    return subroute


@router.delete("/subroutes/{subroute_id_or_code}")
def delete_subroute(
    subroute_id_or_code: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit subroute."""

    subroute = _get_by_id_or_code_or_404(
        db_session,
        TransitSubRoute,
        subroute_id_or_code,
        "Transit subroute not found",
    )

    db_session.delete(subroute)
    db_session.commit()


# endregion


# region Transit subroute-stops

@router.get("/subroute-stops")
def get_all_subroute_stops(db_session: Session = Depends(get_session)) -> list[TransitSubRouteStop]:
    """Get transit subroute-stop mappings."""

    stmt = select(TransitSubRouteStop).order_by(TransitSubRouteStop.stop_order)

    return list(db_session.exec(stmt).all())


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


@router.post("/subroute-stops")
def create_subroute_stop(
    subroute_stop: TransitSubRouteStop,
    db_session: Session = Depends(get_session)
) -> TransitSubRouteStop:
    """Create a new transit subroute-stop mapping."""

    db_session.add(subroute_stop)
    db_session.commit()
    db_session.refresh(subroute_stop)

    return subroute_stop


@router.patch("/subroute-stops/{subroute_stop_id}")
def update_subroute_stop(
    subroute_stop_id: str,
    subroute_stop_data: TransitSubRouteStop,
    db_session: Session = Depends(get_session)
) -> TransitSubRouteStop | None:
    """Update a transit subroute-stop mapping."""

    subroute_stop = _get_by_id_or_404(
        db_session,
        TransitSubRouteStop,
        subroute_stop_id,
        "Transit subroute stop not found",
    )

    for field, value in subroute_stop_data.model_dump(exclude_unset=True).items():
        setattr(subroute_stop, field, value)

    db_session.add(subroute_stop)
    db_session.commit()
    db_session.refresh(subroute_stop)

    return subroute_stop


@router.delete("/subroute-stops/{subroute_stop_id}")
def delete_subroute_stop(
    subroute_stop_id: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit subroute-stop mapping."""

    subroute_stop = _get_by_id_or_404(
        db_session,
        TransitSubRouteStop,
        subroute_stop_id,
        "Transit subroute stop not found",
    )

    db_session.delete(subroute_stop)
    db_session.commit()


# endregion
