"""Unauthenticated routes for mobile app"""

from fastapi import APIRouter, Depends

from backend.database import get_session
from backend.data.users import Customer
from backend.data.auth import AuthMode, CustomerAuth

from .auth import get_current_token, get_current_customer

router = APIRouter(
    dependencies=[Depends(get_current_token)],
    prefix="/profile"
)

@router.get("/customerInfo")
def get_customer_info(customer: Customer = Depends(get_current_customer)) -> Customer:
    return customer