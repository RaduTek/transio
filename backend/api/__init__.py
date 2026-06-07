from fastapi.routing import APIRouter

from .mobile import router as mobile_routes
from .admin import router as admin_routes
from .vehicle import router as vehicle_routes
from .test import router as test_routes

router = APIRouter()

router.include_router(mobile_routes)
router.include_router(admin_routes)
router.include_router(vehicle_routes)
router.include_router(test_routes)