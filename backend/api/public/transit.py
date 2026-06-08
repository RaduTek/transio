"""Transit info routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

from backend.data.transit import TransitCategory, TransitRoute
from backend.database import get_session

router = APIRouter(prefix="/transit", tags=["Transit info routes"])

@router.get("/categories")
def get_categories(db_session: Session = Depends(get_session)) -> list[TransitCategory]:
    """Get transit categories"""

    stmt = select(TransitCategory).order_by(TransitCategory.code)

    return list(db_session.exec(stmt).all())

@router.get("/categories/{category_id_or_code}")
def get_category(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> TransitCategory | None:
    """Get a transit category by ID"""

    stmt = select(TransitCategory).where(or_(
        TransitCategory.id == category_id_or_code,
        TransitCategory.code == category_id_or_code
    )).limit(1)

    category = db_session.exec(stmt).first()

    if not category:
        raise HTTPException(404, "Transit category not found")

    return category

@router.get("/categories/{category_id_or_code}/routes")
def get_category_routes(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
) -> list[TransitRoute]:
    """Get all routes for a transit category"""

    category_stmt = select(TransitCategory).where(or_(
        TransitCategory.id == category_id_or_code,
        TransitCategory.code == category_id_or_code
    )).limit(1)

    category = db_session.exec(category_stmt).first()

    if not category:
        raise HTTPException(404, "Transit category not found")

    routes_stmt = select(TransitRoute) \
        .where(TransitRoute.category_id == category.id) \
        .order_by(TransitRoute.code)

    return list(db_session.exec(routes_stmt).all())
