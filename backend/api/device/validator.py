"""Device validator routes for ticket validation workflow."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from backend.data.assets import Device, Vehicle
from backend.data.auth import AuthMode, CustomerAuth
from backend.data.ticketing import IssuedTicket, TicketCategory, TicketType, TicketValidation
from backend.data.transit import TransitShift
from backend.database import get_session

from .auth import get_current_device, get_current_device_auth_valid


router = APIRouter(
	prefix="/validator",
	tags=["Device Validator Endpoints"],
	dependencies=[Depends(get_current_device_auth_valid)],
)


class ValidateCardRequest(BaseModel):
	card_id: str
	auth_mode: AuthMode

	@field_validator("auth_mode")
	@classmethod
	def validate_card_mode(cls, auth_mode: AuthMode) -> AuthMode:
		if auth_mode not in (AuthMode.PHYSICAL_CARD, AuthMode.DIGITAL_CARD):
			raise ValueError("auth_mode must be Physical Card or Digital Card")

		return auth_mode


class ValidateCardResponse(BaseModel):
	validation: TicketValidation
	ticket: IssuedTicket
	ticket_type: TicketType
	transit_shift: TransitShift


class ValidatorStateResponse(BaseModel):
	device: Device
	vehicle: Vehicle | None
	transit_shift: TransitShift | None


def _is_auth_valid(customer_auth: CustomerAuth, now: datetime) -> bool:
	if not customer_auth.valid:
		return False

	exp_time = customer_auth.created_at + timedelta(seconds=customer_auth.ttl_seconds)
	return exp_time >= now


def _ticket_route_match(ticket_type: TicketType, route_id: str) -> bool:
	if not ticket_type.valid_for_routes:
		return True

	route_ids = [route.strip() for route in ticket_type.valid_for_routes.split(",") if route.strip()]

	if not route_ids:
		return True

	return route_id in route_ids


def _is_ticket_currently_valid(
	issued_ticket: IssuedTicket,
	ticket_type: TicketType,
	now: datetime,
	rides_used: int,
) -> bool:
	if issued_ticket.expires_at <= now:
		return False

	if ticket_type.valid_for_minutes is not None and issued_ticket.validated_at is not None:
		minute_exp = issued_ticket.validated_at + timedelta(minutes=ticket_type.valid_for_minutes)
		if minute_exp < now:
			return False

	if ticket_type.valid_for_rides is not None and rides_used >= ticket_type.valid_for_rides:
		return False

	return True


def _get_active_shift_for_device(
	db_session: Session,
	device: Device,
) -> TransitShift:
	if not device.vehicle_id:
		raise HTTPException(status_code=403, detail="Device is not assigned to a vehicle")

	stmt = select(TransitShift).where(
		TransitShift.vehicle_id == device.vehicle_id,
		TransitShift.shift_end.is_(None),
	).limit(1)
	active_shift = db_session.exec(stmt).first()

	if not active_shift:
		raise HTTPException(status_code=403, detail="No active transit shift for this device")

	return active_shift


@router.get("/state")
def get_validator_state(
	device: Device = Depends(get_current_device),
	db_session: Session = Depends(get_session),
) -> ValidatorStateResponse:
	vehicle: Vehicle | None = None
	active_shift: TransitShift | None = None

	if device.vehicle_id:
		vehicle_stmt = select(Vehicle).where(Vehicle.id == device.vehicle_id).limit(1)
		vehicle = db_session.exec(vehicle_stmt).first()

		if vehicle:
			shift_stmt = select(TransitShift).where(
				TransitShift.vehicle_id == vehicle.id,
				TransitShift.shift_end.is_(None),
			).limit(1)
			active_shift = db_session.exec(shift_stmt).first()

	return ValidatorStateResponse(
		device=device,
		vehicle=vehicle,
		transit_shift=active_shift,
	)


@router.post("/validate")
def validate_card(
	payload: ValidateCardRequest,
	device: Device = Depends(get_current_device),
	db_session: Session = Depends(get_session),
) -> ValidateCardResponse:
	now = datetime.now()
	shift = _get_active_shift_for_device(db_session, device)

	stmt = select(CustomerAuth).where(
		CustomerAuth.auth_mode == payload.auth_mode,
		CustomerAuth.auth_details == payload.card_id,
	).limit(1)
	customer_auth = db_session.exec(stmt).first()

	if not customer_auth or not _is_auth_valid(customer_auth, now):
		raise HTTPException(status_code=404, detail="No active customer found for this card")

	issued_stmt = select(IssuedTicket).where(IssuedTicket.customer_id == customer_auth.customer_id)
	issued_tickets = list(db_session.exec(issued_stmt).all())

	if not issued_tickets:
		raise HTTPException(status_code=404, detail="No issued tickets found for customer")

	ticket_type_ids = {ticket.ticket_type_id for ticket in issued_tickets}
	ticket_type_stmt = select(TicketType).where(TicketType.id.in_(ticket_type_ids))
	ticket_types = {ticket_type.id: ticket_type for ticket_type in db_session.exec(ticket_type_stmt).all()}

	pass_candidates: list[tuple[IssuedTicket, TicketType]] = []
	fixed_candidates: list[tuple[IssuedTicket, TicketType]] = []

	for ticket in issued_tickets:
		ticket_type = ticket_types.get(ticket.ticket_type_id)
		if not ticket_type:
			continue

		if not _ticket_route_match(ticket_type, shift.route_id):
			continue

		ride_count_stmt = select(TicketValidation).where(TicketValidation.issued_ticket_id == ticket.id)
		rides_used = len(list(db_session.exec(ride_count_stmt).all()))

		if not _is_ticket_currently_valid(ticket, ticket_type, now, rides_used):
			continue

		if ticket_type.category == TicketCategory.PASS:
			pass_candidates.append((ticket, ticket_type))
		else:
			fixed_candidates.append((ticket, ticket_type))

	def _candidate_order(item: tuple[IssuedTicket, TicketType]) -> tuple[datetime, datetime]:
		issued_ticket, _ticket_type = item
		return issued_ticket.expires_at, issued_ticket.issued_at

	pass_candidates.sort(key=_candidate_order)
	fixed_candidates.sort(key=_candidate_order)

	chosen: tuple[IssuedTicket, TicketType] | None = None
	if pass_candidates:
		chosen = pass_candidates[0]
	elif fixed_candidates:
		chosen = fixed_candidates[0]

	if not chosen:
		raise HTTPException(status_code=404, detail="No valid ticket found for current route")

	chosen_ticket, chosen_ticket_type = chosen

	validation = TicketValidation(
		issued_ticket_id=chosen_ticket.id,
		device_id=device.id,
		vehicle_id=shift.vehicle_id,
		validated_at=now,
		validation_result="Valid",
	)

	if chosen_ticket.validated_at is None:
		chosen_ticket.validated_at = now
		db_session.add(chosen_ticket)

	db_session.add(validation)
	db_session.commit()
	db_session.refresh(validation)
	db_session.refresh(chosen_ticket)

	return ValidateCardResponse(
		validation=validation,
		ticket=chosen_ticket,
		ticket_type=chosen_ticket_type,
		transit_shift=shift,
	)
