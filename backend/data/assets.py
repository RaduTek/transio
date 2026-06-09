from datetime import date
from enum import Enum
from typing import ClassVar
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid


class VehicleType(str, Enum):
    """Types of vehicles used in transit routes."""
    
    BUS = "Bus"
    TRAIN = "Train"
    TRAM = "Tram"
    FERRY = "Ferry"
    SUBWAY = "Subway"
    TROLLEY = "Trolley"
    OTHER = "Other"


class Vehicle(SQLModel, table=True):
    __tablename__: ClassVar[str] = "vehicles"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    code: str = Field(max_length=32, unique=True)
    vehicle_type: VehicleType = Field(max_length=32)
    registration_number: str = Field(max_length=32, unique=True)

    description: str | None = Field(default=None, description="Public description of the vehicle")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")


class DeviceType(str, Enum):
    """Types of devices used for transit operations."""
    
    VEHICLE_OBC = "Vehicle OBC"
    VALIDATOR = "Validator"
    DISPLAY_SCREEN = "Display Screen"
    TICKET_MACHINE = "Ticket Vending Machine"
    OTHER = "Other"


class Device(SQLModel, table=True):
    __tablename__: ClassVar[str] = "devices"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    code: str = Field(max_length=32, unique=True)
    device_type: DeviceType = Field(max_length=32)
    vehicle_id: str | None = Field(default=None, foreign_key="vehicles.id", index=True, description="Link to the vehicle the device is installed on (null if not vehicle-specific)")

    description: str | None = Field(default=None, description="Public description of the device")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")