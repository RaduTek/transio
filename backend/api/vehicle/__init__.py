"""Vehicle API endpoints, used by on-board equipment"""

from fastapi import APIRouter


router = APIRouter(prefix="/vehicle", tags=["Vehicle Equipment Endpoints"])
