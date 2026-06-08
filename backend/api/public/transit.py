"""Transit info routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Sequence, Session, or_, select

from backend.data.transit import TransitCategory
from backend.database import get_session

router = APIRouter(prefix="/transit", tags=["Transit info routes"])

@router.get("/categories")
def get_categories(db_session: Session = Depends(get_session)) -> list[TransitCategory]:
    """Get transit categories"""

    stmt = select(TransitCategory).order_by(TransitCategory.name)

    return list(db_session.exec(stmt).all())

@router.get("/categories/{category_id}")
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