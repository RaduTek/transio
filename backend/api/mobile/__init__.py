"""Mobile Application API routes"""

from fastapi import APIRouter, Depends

from backend.api.mobile.auth import get_current_customer

router = APIRouter(prefix="/mobile", tags=["Mobile App Endpoints"])

from .login import router as login_routes
router.include_router(login_routes)

from .profile import router as profile_routes
router.include_router(profile_routes, dependencies=[Depends(get_current_customer)])

from .ticketing import router as ticketing_routes
router.include_router(ticketing_routes, dependencies=[Depends(get_current_customer)])

from .routeplan import router as routeplan_routes
router.include_router(routeplan_routes, dependencies=[Depends(get_current_customer)])