"""Public API routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["Public API Endpoints"])

from .transit import router as transit_routes
router.include_router(transit_routes)