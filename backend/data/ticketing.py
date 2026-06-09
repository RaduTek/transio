from datetime import date, datetime
from enum import Enum
from typing import ClassVar
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid


class FareType(str, Enum):
    """Types of fares that can be applied to tickets."""

    STANDARD = "Standard"
    STUDENT = "Student"
    SENIOR = "Senior"
    DISCOUNT = "Discount"
    SURCHARGE = "Surcharge"
    OTHER = "Other"


class TicketCategory(str, Enum):
    """Categories of tickets based on their usage and validity."""

    TICKET = "Ticket"
    PASS = "Pass"
    OTHER = "Other"


class TicketType(SQLModel, table=True):
    __tablename__: ClassVar[str] = "ticket_types"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    name: str = Field(max_length=64, description="Name of the ticket type (e.g., 'Single Ride', 'Day Pass')")
    category: TicketCategory = Field(default=TicketCategory.TICKET, max_length=32)
    unit_price: int = Field(description="Base price of the ticket type in cents (e.g., 250 for $2.50)")
    valid_for_routes: str | None = Field(default=None, description="Comma-separated list of route IDs that the ticket is valid for (empty means all routes)")
    valid_for_rides: int | None = Field(default=None, description="Number of rides the ticket is valid for (null means unlimited)")
    valid_for_minutes: int | None = Field(default=None, description="Number of minutes the ticket is valid for after first validation (null means unlimited)")
    fare_type: FareType = Field(max_length=32)
    published: bool = Field(default=False, description="Indicates whether the ticket type is published and visible to customers for purchase (this locks the ticket type to further modifications)")
    active: bool = Field(default=False, description="Indicates whether the ticket type is currently active and available for purchase")

    description: str | None = Field(default=None, description="Public description of the ticket type")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")


class IssuedTicket(SQLModel, table=True):
    __tablename__: ClassVar[str] = "tickets_issued"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    ticket_type_id: str = Field(foreign_key="ticket_types.id", index=True, description="Link to the ticket type")
    customer_id: str = Field(foreign_key="customers.id", index=True, description="Link to the customer who owns the ticket")
    issued_at: datetime = Field(max_length=26)
    expires_at: datetime = Field(max_length=26)

    fare_type: FareType = Field(max_length=32)
    final_price: int = Field(description="Final price paid by the customer for the ticket in cents (e.g., 250 for $2.50)")
    validated_at: datetime = Field(max_length=26, description="Timestamp of the first validation of the ticket (null if never validated)")
    flagged: bool = Field(default=False, description="Indicates whether the ticket has been flagged for review due to validation issues or suspected fraud")


class TicketValidation(SQLModel, table=True):
    __tablename__: ClassVar[str] = "ticket_validations"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    issued_ticket_id: str = Field(foreign_key="tickets_issued.id", index=True, description="Link to the issued ticket that was validated")
    device_id: str = Field(foreign_key="devices.id", index=True, description="Link to the device where the ticket was validated")
    vehicle_id: str = Field(foreign_key="vehicles.id", index=True, description="Link to the vehicle where the ticket was validated")
    validated_at: datetime = Field(max_length=26, description="Timestamp of the validation of the ticket")
    validation_result: str = Field(max_length=255, description="Result of the validation (e.g., 'Valid', 'Expired', 'Invalid')")
