"""Admin dashboard API endpoints"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin Dashboard Endpoints"])

@router.get("/alive")
def alive():
    return {"status": "ok"}