"""Models for transit management, including stops, routes, and route-stop associations."""

from datetime import datetime
from enum import Enum
from typing import ClassVar
from sqlmodel import Field, Relationship, SQLModel

from backend.data import generate_uuid
from backend.data.assets import VehicleType


class TransitStop(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_stops"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, description="Public description of the stop")
    lat: float
    lon: float
    address: str | None = Field(default=None, max_length=255)

    subroute_stops: list["TransitSubRouteStop"] = Relationship(back_populates="stop")


class TransitCategory(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_categories"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    code: str = Field(max_length=32, unique=True)
    name: str = Field(max_length=255)
    vehicle_type: VehicleType = Field(max_length=32)

    description: str | None = Field(default=None, description="Public description of the category")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")


class TransitRoute(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_routes"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    code: str = Field(max_length=32, unique=True)
    name: str = Field(max_length=255)
    category_id: str = Field(foreign_key="transit_categories.id", index=True)

    description: str | None = Field(default=None, description="Public description of the route")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")


class TransitSubRoute(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_subroutes"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    code: str = Field(max_length=32, unique=True)
    name: str = Field(max_length=255)
    parent_route_id: str = Field(foreign_key="transit_routes.id", index=True)

    description: str | None = Field(default=None, description="Public description of the subroute")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")


class TransitSubRouteStop(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_subroute_stops"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    subroute_id: str = Field(foreign_key="transit_subroutes.id", index=True)
    stop_id: str = Field(foreign_key="transit_stops.id", index=True)
    stop_order: int = Field(index=True, description="The order of the stop within the route")

    description: str | None = Field(default=None, description="Public description of the route-stop association")
    private_notes: str | None = Field(default=None, description="Internal notes not visible to customers")

    stop: TransitStop = Relationship(back_populates="subroute_stops")


class TransitShift(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_shifts"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    vehicle_id: str = Field(foreign_key="vehicles.id", index=True)
    employee_id: str | None = Field(default=None, foreign_key="employees.id", index=True)
    route_id: str = Field(foreign_key="transit_routes.id", index=True)
    subroute_id: str | None = Field(default=None, foreign_key="transit_subroutes.id", index=True)
    shift_start: datetime = Field(max_length=26, description="Start time of the shift in ISO 8601 format")
    shift_end: datetime | None = Field(default=None, max_length=26, description="End time of the shift in ISO 8601 format")
