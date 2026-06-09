"""Admin dashboard API endpoints"""

from fastapi import APIRouter, Depends

from .auth import get_current_token

router = APIRouter(prefix="/admin", tags=["Admin Dashboard Endpoints"])

@router.get("/alive")
def alive():
    return {"status": "ok"}

from .login import router as login_routes
router.include_router(login_routes)

from .transit import router as transit_routes
router.include_router(transit_routes, dependencies=[Depends(get_current_token)])

from .assets import router as assets_routes
router.include_router(assets_routes, dependencies=[Depends(get_current_token)])

from .users import router as users_routes
router.include_router(users_routes, dependencies=[Depends(get_current_token)])