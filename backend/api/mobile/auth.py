"""Authentication helpers for the mobile API"""

import os
import jwt

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional

from backend.database import get_session
from backend.data.auth import CustomerAuth
from backend.data.users import Customer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/mobile/login")


JWT_SECRET = os.getenv("MOBILE_JWT_SECRET", "mobile-secret-key")
JWT_ALGO = "HS256"
JWT_EXP = 365 * 24 * 60 * 60  # 1 year in seconds


class UserTokenData(BaseModel):
    customer_id: str
    auth_id: str
    exp: Optional[datetime]


def create_auth_token(data: UserTokenData) -> str:
    data.exp = datetime.now() + timedelta(seconds=JWT_EXP)

    return jwt.encode(data.model_dump(), JWT_SECRET, algorithm=JWT_ALGO)


def verify_auth_token(token: str) -> UserTokenData:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])

        return UserTokenData.model_validate(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_token(token: str = Depends(oauth2_scheme)) -> UserTokenData:
    return verify_auth_token(token)


def get_current_customer(
    token_data: UserTokenData = Depends(get_current_token),
    db_session: Session = Depends(get_session)
) -> Customer:
    stmt = select(Customer).where(Customer.id == token_data.customer_id).limit(1)

    customer = db_session.exec(stmt).first()

    if not customer:
        raise HTTPException(500, "Couldn't retrieve customer data")

    return customer


def get_current_customer_active(
    customer: Customer = Depends(get_current_customer)
) -> Customer:
    if not customer.active:
        raise HTTPException(401, "Customer account is inactive")

    return customer


def get_current_customer_auth(
    token_data: UserTokenData = Depends(get_current_token),
    db_session: Session = Depends(get_session)
) -> CustomerAuth:
    stmt = select(CustomerAuth).where(CustomerAuth.id == token_data.auth_id).limit(1)

    customer_auth = db_session.exec(stmt).first()

    if not customer_auth:
        raise HTTPException(500, "Couldn't retrieve customer auth data")
    
    return customer_auth


def get_current_customer_auth_valid(
    customer_auth: CustomerAuth = Depends(get_current_customer_auth)
) -> CustomerAuth:
    if not customer_auth.valid:
        raise HTTPException(401, "Authentication method is invalid")
    
    exp_time = customer_auth.created_at + timedelta(seconds=customer_auth.ttl_seconds)

    if exp_time < datetime.now():
        raise HTTPException(401, "Authentication method has expired")
    
    return customer_auth


def get_current_customer_valid(
    customer: Customer = Depends(get_current_customer_active),
    customer_auth: CustomerAuth = Depends(get_current_customer_auth_valid)
) -> Customer:
    return customer