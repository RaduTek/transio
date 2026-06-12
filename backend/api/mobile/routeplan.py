"""Routes for route and journey planning in the mobile app"""

from fastapi import APIRouter, HTTPException
from google import genai

from backend.config import settings


router = APIRouter()


@router.post("/plan_journey")
async def plan_journey():
    """Plan a journey between multiple stops using public transportation."""

    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured")

    client = genai.Client(api_key=settings.gemini_api_key)