"""Transit info routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, or_
from sqlalchemy.exc import IntegrityError

from backend.data.transit import TransitCategory
from backend.database import get_session

router = APIRouter(prefix="/transit", tags=["Admin Transit Routes"])

#region Transit categories

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

@router.post("/categories")
def create_category(
    category: TransitCategory,
    db_session: Session = Depends(get_session)
) -> TransitCategory:
    """Create a new transit category"""

    try:
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Transit category with this code already exists")

    return category

@router.patch("/categories/{category_id}")
def update_category(
    category_id_or_code: str,
    category_data: TransitCategory,
    db_session: Session = Depends(get_session)
) -> TransitCategory | None:
    """Update a transit category"""

    stmt = select(TransitCategory).where(or_(
        TransitCategory.id == category_id_or_code,
        TransitCategory.code == category_id_or_code
    )).limit(1)

    category = db_session.exec(stmt).first()

    if not category:
        raise HTTPException(404, "Transit category not found")

    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    return category

@router.delete("/categories/{category_id}")
def delete_category(
    category_id_or_code: str,
    db_session: Session = Depends(get_session)
):
    """Delete a transit category"""

    stmt = select(TransitCategory).where(or_(
        TransitCategory.id == category_id_or_code,
        TransitCategory.code == category_id_or_code
    )).limit(1)

    category = db_session.exec(stmt).first()

    if not category:
        raise HTTPException(404, "Transit category not found")

    db_session.delete(category)
    db_session.commit()

#endregion
