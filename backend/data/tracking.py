"""Models for managing tracking of vehicles and their shifts/routes in the transit system."""

from datetime import datetime
from typing import ClassVar
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid


class VehicleLocationLog(SQLModel, table=True):
    __tablename__: ClassVar[str] = "vehicle_location_logs"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    timestamp: datetime = Field(max_length=26, description="Timestamp of the location log in ISO 8601 format")
    vehicle_id: str = Field(foreign_key="vehicles.id", index=True)
    lat: float
    lon: float
    speed_kmph: float | None = Field(default=None, description="Speed of the vehicle in kilometers per hour, 0 if stationary")
    heading_degrees: float | None = Field(default=None, description="Heading of the vehicle in degrees from north (0-360)")


class TransitShiftArrivalLog(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_shift_arrival_logs"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    timestamp: datetime = Field(max_length=26, description="Timestamp of the stop arrival log in ISO 8601 format")
    shift_id: str | None = Field(default=None, foreign_key="transit_shifts.id", index=True)
    stop_id: str = Field(foreign_key="transit_stops.id", index=True)