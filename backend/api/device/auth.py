"""Authentication helpers for the device API"""

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from backend.data.auth import AuthMode, DeviceAuth
from backend.data.equipment import Device
from backend.database import get_session


bearer_scheme = HTTPBearer()


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    return credentials.credentials


def get_current_device_auth(
    token: str = Depends(get_current_token),
    db_session: Session = Depends(get_session),
) -> DeviceAuth:
    stmt = select(DeviceAuth).where(
        DeviceAuth.auth_mode == AuthMode.KEY,
        DeviceAuth.auth_details == token,
    ).limit(1)

    device_auth = db_session.exec(stmt).first()

    if not device_auth:
        raise HTTPException(status_code=401, detail="Invalid device token")

    return device_auth


def get_current_device_auth_valid(
    device_auth: DeviceAuth = Depends(get_current_device_auth),
) -> DeviceAuth:
    if not device_auth.valid:
        raise HTTPException(status_code=401, detail="Authentication method is invalid")

    exp_time = device_auth.created_at + timedelta(seconds=device_auth.ttl_seconds)

    if exp_time < datetime.now():
        raise HTTPException(status_code=401, detail="Authentication method has expired")

    return device_auth


def get_current_device(
    device_auth: DeviceAuth = Depends(get_current_device_auth),
    db_session: Session = Depends(get_session),
) -> Device:
    stmt = select(Device).where(Device.id == device_auth.device_id).limit(1)

    device = db_session.exec(stmt).first()

    if not device:
        raise HTTPException(status_code=500, detail="Couldn't retrieve device data")

    return device