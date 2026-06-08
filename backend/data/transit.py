"""Models for transit management, including stops, routes, and route-stop associations."""

from enum import Enum
from typing import ClassVar
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid
from backend.data.equipment import VehicleType


class TransitStop(SQLModel, table=True):
    __tablename__: ClassVar[str] = "transit_stops"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, description="Public description of the stop")
    lat: float
    lon: float
    address: str | None = Field(default=None, max_length=255)


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
