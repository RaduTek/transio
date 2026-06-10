from fastapi.routing import APIRouter

router = APIRouter()

from .admin import router as admin_routes
router.include_router(admin_routes)

from .device import router as device_routes
router.include_router(device_routes)

from .mobile import router as mobile_routes
router.include_router(mobile_routes)

from .public import router as public_routes
router.include_router(public_routes)

from .test import router as test_routes
router.include_router(test_routes)
