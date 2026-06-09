"""Admin dashboard API endpoints"""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin Dashboard Endpoints"])

@router.get("/alive")
def alive():
    return {"status": "ok"}

from .transit import router as transit_routes
router.include_router(transit_routes)

from .assets import router as assets_routes
router.include_router(assets_routes)

from .users import router as users_routes
router.include_router(users_routes)