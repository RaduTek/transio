"""Statistics endpoints for the admin dashboard"""

from datetime import date, datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.data.assets import Vehicle
from backend.data.ticketing import IssuedTicket, TicketValidation
from backend.data.users import Employee, Customer
from backend.data.transit import TransitShift


router = APIRouter(prefix="/stats")


class ShiftHistoryEntry(BaseModel):
    date: date
    count: int


class ValidationHistoryEntry(BaseModel):
    date: date
    count: int


class StatsOverview(BaseModel):
    vehicle_count: int
    employee_count: int
    customer_count: int
    active_issued_ticket_count: int
    shift_history: list[ShiftHistoryEntry]
    validation_history: list[ValidationHistoryEntry]


@router.get("/overview")
def get_stats_overview(db_session: Session = Depends(get_session)) -> StatsOverview:
    vehicle_count = db_session.exec(select(func.count(Vehicle.id))).one()
    employee_count = db_session.exec(select(func.count(Employee.id))).one()
    customer_count = db_session.exec(select(func.count(Customer.id))).one()
    active_issued_ticket_count = db_session.exec(
        select(func.count(IssuedTicket.id)).where(IssuedTicket.expires_at >= datetime.utcnow())
    ).one()

    shift_rows = db_session.exec(
        select(
            func.date(TransitShift.shift_start).label("shift_date"),
            func.count(TransitShift.id).label("count"),
        )
        .group_by(func.date(TransitShift.shift_start))
        .order_by(func.date(TransitShift.shift_start))
    ).all()

    shift_history = [
        ShiftHistoryEntry(date=row.shift_date, count=row.count)
        for row in shift_rows
    ]

    validation_rows = db_session.exec(
        select(
            func.date(TicketValidation.validated_at).label("validation_date"),
            func.count(TicketValidation.id).label("count"),
        )
        .group_by(func.date(TicketValidation.validated_at))
        .order_by(func.date(TicketValidation.validated_at))
    ).all()

    validation_history = [
        ValidationHistoryEntry(date=row.validation_date, count=row.count)
        for row in validation_rows
    ]

    return StatsOverview(
        vehicle_count=vehicle_count,
        employee_count=employee_count,
        customer_count=customer_count,
        active_issued_ticket_count=active_issued_ticket_count,
        shift_history=shift_history,
        validation_history=validation_history,
    )
