from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import TransitRoute
from .schemas import TransitRouteRead


router = APIRouter(prefix="/routes", tags=["routes"])


@router.get("", response_model=list[TransitRouteRead])
def list_transit_routes(db: Session = Depends(get_db)):
    statement = select(TransitRoute).order_by(TransitRoute.id)
    return db.scalars(statement).all()
