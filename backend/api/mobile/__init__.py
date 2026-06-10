"""Mobile Application API routes"""

from fastapi import APIRouter

router = APIRouter(prefix="/mobile", tags=["Mobile App Endpoints"])

from .login import router as login_routes
router.include_router(login_routes)

from .profile import router as profile_routes
router.include_router(profile_routes)

from .ticketing import router as ticketing_routes
router.include_router(ticketing_routes)