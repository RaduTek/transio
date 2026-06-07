"""Unauthenticated routes for mobile app"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlmodel import Session, select

from backend.database import get_session
from backend.data.users import Customer
from backend.data.auth import AuthMode, CustomerAuth

from .auth import create_auth_token, UserTokenData


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    customer: Customer
    token: str


@router.post("/login")
async def login(login_request: LoginRequest, db_session: Session = Depends(get_session)) -> LoginResponse:
    stmt = select(Customer).where(Customer.email == login_request.email).limit(1)

    customer = db_session.exec(stmt).first()

    if not customer:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    stmt = select(CustomerAuth).where(
        CustomerAuth.auth_mode == AuthMode.PASSWORD,
        CustomerAuth.customer_id == customer.id
    ).limit(1)

    customer_auth = db_session.exec(stmt).first()

    if not customer_auth:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    password_hash = PasswordHash.recommended()
    if not password_hash.verify(login_request.password, customer_auth.auth_details):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_auth_token(
        UserTokenData(customer_id=customer.id, auth_id=customer_auth.id, exp=None)
    )

    return LoginResponse(
        customer=customer,
        token=token
    )


class SignupRequest(BaseModel):
    email: str
    phone: str
    first_name: str
    last_name: str
    password: str


@router.post("/signup")
async def signup(signup_request: SignupRequest, db_session: Session = Depends(get_session)) -> LoginResponse:
    customer = Customer(
        email=signup_request.email,
        phone=signup_request.phone,
        first_name=signup_request.first_name,
        last_name=signup_request.last_name,
        registered_date=datetime.now()
    )

    password_hash = PasswordHash.recommended()

    customer_auth = CustomerAuth(
        customer_id=customer.id,
        auth_mode=AuthMode.PASSWORD,
        auth_details=password_hash.hash(signup_request.password),
        created_at=datetime.now()
    )

    try:
        db_session.add(customer)
        db_session.commit()
    except Exception as ex:
        raise HTTPException(500, f"Error encountered while creating customer account. (CreateCustomer)")

    try:
        db_session.add(customer_auth)
        db_session.commit()
    except Exception as ex:
        raise HTTPException(500, "Error encountered while creating customer account. (CreateCustomerAuth)")
    
    token = create_auth_token(
        UserTokenData(customer_id=customer.id, auth_id=customer_auth.id, exp=None)
    )

    return LoginResponse(
        customer=customer,
        token=token
    )
