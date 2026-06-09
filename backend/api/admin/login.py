"""Unauthenticated routes for admin app"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from sqlmodel import Session, select

from backend.database import get_session
from backend.data.users import Employee
from backend.data.auth import AuthMode, EmployeeAuth

from .auth import create_auth_token, UserTokenData


router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    employee: Employee
    token: str


@router.post("/login")
async def login(login_request: LoginRequest, db_session: Session = Depends(get_session)) -> LoginResponse:
    stmt = select(Employee).where(Employee.email == login_request.email).limit(1)

    employee = db_session.exec(stmt).first()

    if not employee:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    stmt = select(EmployeeAuth).where(
        EmployeeAuth.auth_mode == AuthMode.PASSWORD,
        EmployeeAuth.employee_id == employee.id
    ).limit(1)

    employee_auth = db_session.exec(stmt).first()

    if not employee_auth:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    password_hash = PasswordHash.recommended()
    if not password_hash.verify(login_request.password, employee_auth.auth_details):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_auth_token(
        UserTokenData(employee_id=employee.id, auth_id=employee_auth.id, exp=None)
    )

    return LoginResponse(
        employee=employee,
        token=token
    )