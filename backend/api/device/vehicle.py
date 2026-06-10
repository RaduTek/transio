"""Device vehicle routes for OBC shift and telemetry workflows."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from backend.data.assets import Device, Vehicle
from backend.data.auth import AuthMode, EmployeeAuth
from backend.data.tracking import VehicleLocationLog
from backend.data.transit import TransitRoute, TransitShift, TransitSubRoute
from backend.data.users import Employee, EmployeeRole
from backend.database import get_session

from .auth import get_current_device, get_current_device_auth_valid


router = APIRouter(
    prefix="/vehicle",
    tags=["Device Vehicle Endpoints"],
    dependencies=[Depends(get_current_device_auth_valid)],
)


class VehicleTelemetryRequest(BaseModel):
    timestamp: datetime | None = None
    lat: float
    lon: float
    speed_kmph: float | None = None
    heading_degrees: float | None = None


class VehicleTelemetryResponse(BaseModel):
    location_log: VehicleLocationLog


class DriverLoginRequest(BaseModel):
    card_id: str
    auth_mode: AuthMode = AuthMode.PHYSICAL_CARD

    @field_validator("auth_mode")
    @classmethod
    def validate_auth_mode(cls, auth_mode: AuthMode) -> AuthMode:
        if auth_mode not in (AuthMode.PHYSICAL_CARD, AuthMode.DIGITAL_CARD):
            raise ValueError("auth_mode must be Physical Card or Digital Card")

        return auth_mode


class DriverLoginResponse(BaseModel):
    employee: Employee


class ShiftStartRequest(BaseModel):
    employee_id: str
    route_id: str
    subroute_id: str | None = None


class ShiftStartResponse(BaseModel):
    transit_shift: TransitShift


class ShiftEndResponse(BaseModel):
    transit_shift: TransitShift


class DriverLogoutResponse(BaseModel):
    ended_shift: TransitShift | None


class VehicleStateResponse(BaseModel):
    device: Device
    vehicle: Vehicle | None
    transit_shift: TransitShift | None
    driver: Employee | None


def _is_auth_valid(employee_auth: EmployeeAuth, now: datetime) -> bool:
    if not employee_auth.valid:
        return False

    exp_time = employee_auth.created_at + timedelta(seconds=employee_auth.ttl_seconds)
    return exp_time >= now


def _get_vehicle_for_device(db_session: Session, device: Device) -> Vehicle:
    if not device.vehicle_id:
        raise HTTPException(status_code=403, detail="Device is not assigned to a vehicle")

    stmt = select(Vehicle).where(Vehicle.id == device.vehicle_id).limit(1)
    vehicle = db_session.exec(stmt).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Assigned vehicle not found")

    return vehicle


def _get_active_shift_for_vehicle(db_session: Session, vehicle_id: str) -> TransitShift | None:
    stmt = select(TransitShift).where(
        TransitShift.vehicle_id == vehicle_id,
        TransitShift.shift_end.is_(None),
    ).limit(1)
    return db_session.exec(stmt).first()


def _get_driver_for_shift(db_session: Session, shift: TransitShift | None) -> Employee | None:
    if not shift or not shift.employee_id:
        return None

    stmt = select(Employee).where(Employee.id == shift.employee_id).limit(1)
    return db_session.exec(stmt).first()


def _validate_route_selection(
    db_session: Session,
    route_id: str,
    subroute_id: str | None,
) -> None:
    route_stmt = select(TransitRoute).where(TransitRoute.id == route_id).limit(1)
    route = db_session.exec(route_stmt).first()

    if not route:
        raise HTTPException(status_code=404, detail="Transit route not found")

    if not subroute_id:
        return

    subroute_stmt = select(TransitSubRoute).where(TransitSubRoute.id == subroute_id).limit(1)
    subroute = db_session.exec(subroute_stmt).first()

    if not subroute:
        raise HTTPException(status_code=404, detail="Transit subroute not found")

    if subroute.parent_route_id != route.id:
        raise HTTPException(status_code=400, detail="Transit subroute does not belong to selected route")


def _get_driver_by_badge(
    db_session: Session,
    card_id: str,
    auth_mode: AuthMode,
    now: datetime,
) -> Employee:
    auth_stmt = select(EmployeeAuth).where(
        EmployeeAuth.auth_mode == auth_mode,
        EmployeeAuth.auth_details == card_id,
    ).limit(1)
    employee_auth = db_session.exec(auth_stmt).first()

    if not employee_auth or not _is_auth_valid(employee_auth, now):
        raise HTTPException(status_code=404, detail="No active driver found for this card")

    employee_stmt = select(Employee).where(Employee.id == employee_auth.employee_id).limit(1)
    employee = db_session.exec(employee_stmt).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    if not employee.active:
        raise HTTPException(status_code=403, detail="Driver account is inactive")

    if employee.role != EmployeeRole.DRIVER:
        raise HTTPException(status_code=403, detail="Employee is not a driver")

    return employee


@router.get("/state")
def get_vehicle_state(
    device: Device = Depends(get_current_device),
    db_session: Session = Depends(get_session),
) -> VehicleStateResponse:
    vehicle: Vehicle | None = None
    active_shift: TransitShift | None = None
    driver: Employee | None = None

    if device.vehicle_id:
        vehicle = _get_vehicle_for_device(db_session, device)
        active_shift = _get_active_shift_for_vehicle(db_session, vehicle.id)
        driver = _get_driver_for_shift(db_session, active_shift)

    return VehicleStateResponse(
        device=device,
        vehicle=vehicle,
        transit_shift=active_shift,
        driver=driver,
    )


@router.post("/telemetry")
def submit_telemetry(
    payload: VehicleTelemetryRequest,
    device: Device = Depends(get_current_device),
    db_session: Session = Depends(get_session),
) -> VehicleTelemetryResponse:
    vehicle = _get_vehicle_for_device(db_session, device)

    location_log = VehicleLocationLog(
        timestamp=payload.timestamp or datetime.now(),
        vehicle_id=vehicle.id,
        lat=payload.lat,
        lon=payload.lon,
        speed_kmph=payload.speed_kmph,
        heading_degrees=payload.heading_degrees,
    )

    db_session.add(location_log)
    db_session.commit()
    db_session.refresh(location_log)

    return VehicleTelemetryResponse(location_log=location_log)


@router.post("/shift/login")
def login_driver(
    payload: DriverLoginRequest,
    db_session: Session = Depends(get_session),
) -> DriverLoginResponse:
    now = datetime.now()
    employee = _get_driver_by_badge(
        db_session=db_session,
        card_id=payload.card_id,
        auth_mode=payload.auth_mode,
        now=now,
    )

    return DriverLoginResponse(employee=employee)


@router.post("/shift/logout")
def logout_driver(
    device: Device = Depends(get_current_device),
    db_session: Session = Depends(get_session),
) -> DriverLogoutResponse:
    vehicle = _get_vehicle_for_device(db_session, device)

    active_shift = _get_active_shift_for_vehicle(db_session, vehicle.id)
    if not active_shift:
        return DriverLogoutResponse(ended_shift=None)

    if active_shift.shift_end is None:
        active_shift.shift_end = datetime.now()
        db_session.add(active_shift)
        db_session.commit()
        db_session.refresh(active_shift)

    return DriverLogoutResponse(ended_shift=active_shift)


@router.post("/shift/start")
def start_shift(
    payload: ShiftStartRequest,
    device: Device = Depends(get_current_device),
    db_session: Session = Depends(get_session),
) -> ShiftStartResponse:
    vehicle = _get_vehicle_for_device(db_session, device)

    active_shift = _get_active_shift_for_vehicle(db_session, vehicle.id)
    if active_shift:
        raise HTTPException(status_code=409, detail="A transit shift is already active for this vehicle")

    employee_stmt = select(Employee).where(Employee.id == payload.employee_id).limit(1)
    employee = db_session.exec(employee_stmt).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    if not employee.active:
        raise HTTPException(status_code=403, detail="Driver account is inactive")

    if employee.role != EmployeeRole.DRIVER:
        raise HTTPException(status_code=403, detail="Employee is not a driver")

    _validate_route_selection(
        db_session=db_session,
        route_id=payload.route_id,
        subroute_id=payload.subroute_id,
    )

    shift = TransitShift(
        vehicle_id=vehicle.id,
        employee_id=employee.id,
        route_id=payload.route_id,
        subroute_id=payload.subroute_id,
        shift_start=datetime.now(),
        shift_end=None,
    )

    db_session.add(shift)
    db_session.commit()
    db_session.refresh(shift)

    return ShiftStartResponse(transit_shift=shift)


@router.post("/shift/end")
def end_shift(
    device: Device = Depends(get_current_device),
    db_session: Session = Depends(get_session),
) -> ShiftEndResponse:
    vehicle = _get_vehicle_for_device(db_session, device)

    active_shift = _get_active_shift_for_vehicle(db_session, vehicle.id)
    if not active_shift:
        raise HTTPException(status_code=404, detail="No active transit shift for this vehicle")

    active_shift.shift_end = datetime.now()
    db_session.add(active_shift)
    db_session.commit()
    db_session.refresh(active_shift)

    return ShiftEndResponse(transit_shift=active_shift)
