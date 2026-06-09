"""Admin users routes for customer and employee management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.data.auth import CustomerAuth, EmployeeAuth
from backend.data.users import Customer, Employee
from backend.database import get_session

router = APIRouter(prefix="/users", tags=["Admin User Routes"])


def _get_by_id_or_404(
    db_session: Session,
    model: Any,
    entity_id: str,
    not_found_message: str,
):
    stmt = select(model).where(model.id == entity_id).limit(1)
    entity = db_session.exec(stmt).first()

    if not entity:
        raise HTTPException(404, not_found_message)

    return entity


def _redact_auth_details(auth_record: Any) -> dict[str, Any]:
    payload = auth_record.model_dump()
    payload["auth_details"] = "[REDACTED]"
    return payload


@router.get("/employees")
def get_employees(db_session: Session = Depends(get_session)) -> list[Employee]:
    """Get all employees."""

    stmt = select(Employee).order_by(Employee.last_name, Employee.first_name)
    return list(db_session.exec(stmt).all())


@router.get("/employees/{employee_id}")
def get_employee(
    employee_id: str,
    db_session: Session = Depends(get_session),
) -> Employee | None:
    """Get an employee by ID."""

    return _get_by_id_or_404(db_session, Employee, employee_id, "Employee not found")


@router.get("/employees/{employee_id}/auth")
def get_employee_auth(
    employee_id: str,
    db_session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Get auth data for an employee with redacted auth_details."""

    employee = _get_by_id_or_404(db_session, Employee, employee_id, "Employee not found")
    stmt = select(EmployeeAuth).where(EmployeeAuth.employee_id == employee.id).limit(1)
    employee_auth = db_session.exec(stmt).first()

    if not employee_auth:
        raise HTTPException(404, "Employee auth not found")

    return _redact_auth_details(employee_auth)


@router.post("/employees")
def create_employee(
    employee: Employee,
    db_session: Session = Depends(get_session),
) -> Employee:
    """Create an employee."""

    try:
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Employee with this email, phone, or customer assignment already exists")

    return employee


@router.patch("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    employee_data: Employee,
    db_session: Session = Depends(get_session),
) -> Employee | None:
    """Update an employee."""

    employee = _get_by_id_or_404(db_session, Employee, employee_id, "Employee not found")

    for field, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)

    try:
        db_session.add(employee)
        db_session.commit()
        db_session.refresh(employee)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Employee with this email, phone, or customer assignment already exists")

    return employee


@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete an employee."""

    employee = _get_by_id_or_404(db_session, Employee, employee_id, "Employee not found")

    db_session.delete(employee)
    db_session.commit()


@router.get("/customers")
def get_customers(db_session: Session = Depends(get_session)) -> list[Customer]:
    """Get all customers."""

    stmt = select(Customer).order_by(Customer.last_name, Customer.first_name)
    return list(db_session.exec(stmt).all())


@router.get("/customers/{customer_id}")
def get_customer(
    customer_id: str,
    db_session: Session = Depends(get_session),
) -> Customer | None:
    """Get a customer by ID."""

    return _get_by_id_or_404(db_session, Customer, customer_id, "Customer not found")


@router.get("/customers/{customer_id}/auth")
def get_customer_auth(
    customer_id: str,
    db_session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Get auth data for a customer with redacted auth_details."""

    customer = _get_by_id_or_404(db_session, Customer, customer_id, "Customer not found")
    stmt = select(CustomerAuth).where(CustomerAuth.customer_id == customer.id).limit(1)
    customer_auth = db_session.exec(stmt).first()

    if not customer_auth:
        raise HTTPException(404, "Customer auth not found")

    return _redact_auth_details(customer_auth)


@router.post("/customers")
def create_customer(
    customer: Customer,
    db_session: Session = Depends(get_session),
) -> Customer:
    """Create a customer."""

    try:
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Customer with this email or phone already exists")

    return customer


@router.patch("/customers/{customer_id}")
def update_customer(
    customer_id: str,
    customer_data: Customer,
    db_session: Session = Depends(get_session),
) -> Customer | None:
    """Update a customer."""

    customer = _get_by_id_or_404(db_session, Customer, customer_id, "Customer not found")

    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    try:
        db_session.add(customer)
        db_session.commit()
        db_session.refresh(customer)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Customer with this email or phone already exists")

    return customer


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete a customer."""

    customer = _get_by_id_or_404(db_session, Customer, customer_id, "Customer not found")

    db_session.delete(customer)
    db_session.commit()