"""Admin assets routes for equipment management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, or_, select

from backend.data.auth import DeviceAuth
from backend.data.equipment import Device, Vehicle
from backend.database import get_session

router = APIRouter(prefix="/assets", tags=["Admin Asset Routes"])


def _get_by_id_or_404(
    db_session: Session,
    model: Any,
    entity_id: str,
    not_found_message: str,
):
    stmt = select(model).where(model.id == entity_id).limit(1)
    entity = db_session.exec(stmt).first()

    if not entity:
        raise HTTPException(404, not_found_message)

    return entity


def _get_by_id_or_code_or_404(
    db_session: Session,
    model: Any,
    entity_id_or_code: str,
    not_found_message: str,
):
    stmt = select(model).where(or_(
        model.id == entity_id_or_code,
        model.code == entity_id_or_code,
    )).limit(1)
    entity = db_session.exec(stmt).first()

    if not entity:
        raise HTTPException(404, not_found_message)

    return entity


def _redact_auth_details(auth_record: Any) -> dict[str, Any]:
    payload = auth_record.model_dump()
    payload["auth_details"] = "[REDACTED]"
    return payload


@router.get("/vehicles")
def get_vehicles(db_session: Session = Depends(get_session)) -> list[Vehicle]:
    """Get all vehicles."""

    stmt = select(Vehicle).order_by(Vehicle.code)
    return list(db_session.exec(stmt).all())


@router.get("/vehicles/{vehicle_id_or_code}")
def get_vehicle(
    vehicle_id_or_code: str,
    db_session: Session = Depends(get_session),
) -> Vehicle | None:
    """Get a vehicle by ID or code."""

    return _get_by_id_or_code_or_404(
        db_session,
        Vehicle,
        vehicle_id_or_code,
        "Vehicle not found",
    )


@router.post("/vehicles")
def create_vehicle(
    vehicle: Vehicle,
    db_session: Session = Depends(get_session),
) -> Vehicle:
    """Create a vehicle."""

    try:
        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Vehicle with this code or registration number already exists")

    return vehicle


@router.patch("/vehicles/{vehicle_id_or_code}")
def update_vehicle(
    vehicle_id_or_code: str,
    vehicle_data: Vehicle,
    db_session: Session = Depends(get_session),
) -> Vehicle | None:
    """Update a vehicle."""

    vehicle = _get_by_id_or_code_or_404(
        db_session,
        Vehicle,
        vehicle_id_or_code,
        "Vehicle not found",
    )

    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    try:
        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Vehicle with this code or registration number already exists")

    return vehicle


@router.delete("/vehicles/{vehicle_id_or_code}")
def delete_vehicle(
    vehicle_id_or_code: str,
    db_session: Session = Depends(get_session),
):
    """Delete a vehicle."""

    vehicle = _get_by_id_or_code_or_404(
        db_session,
        Vehicle,
        vehicle_id_or_code,
        "Vehicle not found",
    )

    db_session.delete(vehicle)
    db_session.commit()


@router.get("/devices")
def get_devices(db_session: Session = Depends(get_session)) -> list[Device]:
    """Get all devices."""

    stmt = select(Device).order_by(Device.code)
    return list(db_session.exec(stmt).all())


@router.get("/devices/{device_id_or_code}")
def get_device(
    device_id_or_code: str,
    db_session: Session = Depends(get_session),
) -> Device | None:
    """Get a device by ID or code."""

    return _get_by_id_or_code_or_404(
        db_session,
        Device,
        device_id_or_code,
        "Device not found",
    )


@router.get("/devices/{device_id_or_code}/auth")
def get_device_auth(
    device_id_or_code: str,
    db_session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Get auth data for a device with redacted auth_details."""

    device = _get_by_id_or_code_or_404(
        db_session,
        Device,
        device_id_or_code,
        "Device not found",
    )
    stmt = select(DeviceAuth).where(DeviceAuth.device_id == device.id).limit(1)
    device_auth = db_session.exec(stmt).first()

    if not device_auth:
        raise HTTPException(404, "Device auth not found")

    return _redact_auth_details(device_auth)


@router.post("/devices")
def create_device(
    device: Device,
    db_session: Session = Depends(get_session),
) -> Device:
    """Create a device."""

    try:
        db_session.add(device)
        db_session.commit()
        db_session.refresh(device)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Device with this code already exists")

    return device


@router.patch("/devices/{device_id_or_code}")
def update_device(
    device_id_or_code: str,
    device_data: Device,
    db_session: Session = Depends(get_session),
) -> Device | None:
    """Update a device."""

    device = _get_by_id_or_code_or_404(
        db_session,
        Device,
        device_id_or_code,
        "Device not found",
    )

    for field, value in device_data.model_dump(exclude_unset=True).items():
        setattr(device, field, value)

    try:
        db_session.add(device)
        db_session.commit()
        db_session.refresh(device)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Device with this code already exists")

    return device


@router.delete("/devices/{device_id_or_code}")
def delete_device(
    device_id_or_code: str,
    db_session: Session = Depends(get_session),
):
    """Delete a device."""

    device = _get_by_id_or_code_or_404(
        db_session,
        Device,
        device_id_or_code,
        "Device not found",
    )

    db_session.delete(device)
    db_session.commit()