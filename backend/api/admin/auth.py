"""Authentication helpers for the admin API"""

import os
import jwt

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import Optional

from backend.database import get_session
from backend.data.auth import EmployeeAuth
from backend.data.users import Employee

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "admin-secret-key")
JWT_ALGO = "HS256"
JWT_EXP = 365 * 24 * 60 * 60  # 1 year in seconds


class UserTokenData(BaseModel):
    employee_id: str
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


def get_current_employee(
    token_data: UserTokenData = Depends(get_current_token),
    db_session: Session = Depends(get_session)
) -> Employee:
    stmt = select(Employee).where(Employee.id == token_data.employee_id).limit(1)

    employee = db_session.exec(stmt).first()

    if not employee:
        raise HTTPException(500, "Couldn't retrieve employee data")

    return employee


def get_current_employee_active(
    employee: Employee = Depends(get_current_employee)
) -> Employee:
    if not employee.active:
        raise HTTPException(401, "Employee account is inactive")

    return employee


def get_current_employee_auth(
    token_data: UserTokenData = Depends(get_current_token),
    db_session: Session = Depends(get_session)
) -> EmployeeAuth:
    stmt = select(EmployeeAuth).where(EmployeeAuth.id == token_data.auth_id).limit(1)

    employee_auth = db_session.exec(stmt).first()

    if not employee_auth:
        raise HTTPException(500, "Couldn't retrieve employee auth data")

    return employee_auth


def get_current_employee_auth_valid(
    employee_auth: EmployeeAuth = Depends(get_current_employee_auth)
) -> EmployeeAuth:
    if not employee_auth.valid:
        raise HTTPException(401, "Authentication method is invalid")

    exp_time = employee_auth.created_at + timedelta(seconds=employee_auth.ttl_seconds)

    if exp_time < datetime.now():
        raise HTTPException(401, "Authentication method has expired")

    return employee_auth


def get_current_employee_valid(
    employee: Employee = Depends(get_current_employee_active),
    employee_auth: EmployeeAuth = Depends(get_current_employee_auth_valid)
) -> Employee:
    return employee