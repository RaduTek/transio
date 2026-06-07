"""Test API endpoints"""

from fastapi import APIRouter


router = APIRouter(prefix="/test", tags=["Test Endpoints"])
