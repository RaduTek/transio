"""Models for representing authorization details for users and equipment."""

from datetime import datetime
from enum import Enum
from typing import ClassVar
from sqlmodel import Field, SQLModel

from backend.data import generate_uuid
import backend.data.assets as assets
import backend.data.users as users


class AuthMode(str, Enum):
    """Modes of authorization for accessing the system."""

    PHYSICAL_CARD = "Physical Card"
    DIGITAL_CARD = "Digital Card"
    PASSWORD = "Password"
    KEY = "Key"
    KEYPAIR = "Key Pair"
    OTHER = "Other"


class CustomerAuth(SQLModel, table=True):
    """Model for representing customer authorization details."""

    __tablename__: ClassVar[str] = "customer_auths"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    customer_id: str = Field(foreign_key="customers.id", unique=True, index=True, description="Link to the customer profile")
    auth_mode: AuthMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., OAuth provider, SSO domain)")
    created_at: datetime = Field(max_length=26, description="Timestamp of when the authorization was created (ISO 8601 format)")
    ttl_seconds: int = Field(default=0, description="Time-to-live for the authorization in seconds, after which it expires")
    valid: bool = Field(default=True, description="Indicates whether the authorization is currently valid or has been revoked/expired")


class EmployeeAuth(SQLModel, table=True):
    """Model for representing employee authorization details."""

    __tablename__: ClassVar[str] = "employee_auths"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    employee_id: str = Field(foreign_key="employees.id", unique=True, index=True, description="Link to the employee profile")
    auth_mode: AuthMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., OAuth provider, SSO domain)")
    created_at: datetime = Field(max_length=26, description="Timestamp of when the authorization was created (ISO 8601 format)")
    ttl_seconds: int = Field(default=0, description="Time-to-live for the authorization in seconds, after which it expires")
    valid: bool = Field(default=True, description="Indicates whether the authorization is currently valid or has been revoked/expired")


class DeviceAuth(SQLModel, table=True):
    """Model for representing device authorization details."""

    __tablename__: ClassVar[str] = "device_auths"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True, max_length=36)
    device_id: str = Field(foreign_key="devices.id", unique=True, index=True, description="Link to the device profile")
    auth_mode: AuthMode = Field(max_length=32)
    auth_details: str = Field(max_length=255, description="Details about the authorization mode (e.g., physical card ID, digital token info)")
    created_at: datetime = Field(max_length=26, description="Timestamp of when the authorization was created (ISO 8601 format)")
    ttl_seconds: int = Field(default=0, description="Time-to-live for the authorization in seconds, after which it expires")
    valid: bool = Field(default=True, description="Indicates whether the authorization is currently valid or has been revoked/expired")
