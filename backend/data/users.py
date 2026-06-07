"""Models for app users (customers) and employees."""

from datetime import date, datetime
from enum import Enum
from typing import ClassVar, Optional
from sqlmodel import Field, Relationship, SQLModel

from backend.data import generate_uuid


class EmployeeRole(str, Enum):
    """Roles that employees can have within the transit company."""

    DRIVER = "Driver"
    DISPATCHER = "Dispatcher"
    CONTROLLER = "Controller"
    MANAGER = "Manager"
    SALES = "Sales"
    SUPPORT = "Support"
    TECHNICIAN = "Technician"
    MECHANIC = "Mechanic"
    OTHER = "Other"


class Employee(SQLModel, table=True):
    """Model for representing employees within the transit company."""

    __tablename__: ClassVar[str] = "employees"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    email: str = Field(max_length=32, unique=True, index=True)
    phone: str = Field(max_length=32, unique=True, index=True)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    active: bool = Field(default=True, description="Indicates whether the account is active")
    role: EmployeeRole = Field(max_length=32)
    customer_id: str = Field(foreign_key="customers.id", unique=True, index=True, description="Link to the customer profile of the employee")
    employment_start_date: date = Field(max_length=10)  # YYYY-MM-DD

    customer: Optional["Customer"] = Relationship(back_populates="employee")


class Customer(SQLModel, table=True):
    """Model for representing customers who use the transit services."""

    __tablename__: ClassVar[str] = "customers"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    email: str = Field(max_length=32, unique=True, index=True)
    phone: str = Field(max_length=32, unique=True, index=True)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    registered_date: datetime = Field(max_length=26)
    active: bool = Field(default=True, description="Indicates whether the account is active")

    employee: Optional[Employee] = Relationship(back_populates="customer")

