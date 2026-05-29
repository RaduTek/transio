"""Models for representing authorization details for users and equipment."""

from enum import Enum
from typing import ClassVar, Optional
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid


class AuthorizationMode(str, Enum):
    """Modes of authorization for accessing the system."""

    PHYSICAL_CARD = "Physical Card"
    DIGITAL_CARD = "Digital Card"
    PASSWORD = "Password"
    KEYPAIR = "Key Pair"
    OTHER = "Other"


class CustomerAuthorization(SQLModel, table=True):
    """Model for representing customer authorization details."""

    __tablename__: ClassVar[str] = "customer_authorizations"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    customer_id: str = Field(foreign_key="customers.id", unique=True, index=True, description="Link to the customer profile")
    auth_mode: AuthorizationMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., OAuth provider, SSO domain)")


class EmployeeAuthorization(SQLModel, table=True):
    """Model for representing employee authorization details."""

    __tablename__: ClassVar[str] = "employee_authorizations"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    employee_id: str = Field(foreign_key="employees.id", unique=True, index=True, description="Link to the employee profile")
    auth_mode: AuthorizationMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., OAuth provider, SSO domain)")


class DeviceAuthorization(SQLModel, table=True):
    """Model for representing device authorization details."""

    __tablename__: ClassVar[str] = "device_authorizations"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    device_id: str = Field(foreign_key="devices.id", unique=True, index=True, description="Link to the device profile")
    auth_mode: AuthorizationMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., physical card ID, digital token info)")