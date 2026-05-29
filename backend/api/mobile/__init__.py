from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/mobile", tags=["Mobile App Endpoints"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(login_request: LoginRequest):
    return {"message": "Login successful"}


@router.get("/profile")
async def get_profile():
    return {"message": "User profile data"}