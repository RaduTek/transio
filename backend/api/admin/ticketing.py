"""Admin ticketing routes for fare and wallet management."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from backend.data.ticketing import (
    CustomerWallet,
    CustomerWalletTransaction,
    IssuedTicket,
    TicketType,
    TicketValidation,
)
from backend.database import get_session

router = APIRouter(prefix="/ticketing", tags=["Admin Ticketing Routes"])


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


# region Ticket types

@router.get("/types")
def get_ticket_types(db_session: Session = Depends(get_session)) -> list[TicketType]:
    """Get all ticket types."""

    stmt = select(TicketType).order_by(TicketType.name)
    return list(db_session.exec(stmt).all())


@router.get("/types/{ticket_type_id}")
def get_ticket_type(
    ticket_type_id: str,
    db_session: Session = Depends(get_session),
) -> TicketType | None:
    """Get a ticket type by ID."""

    return _get_by_id_or_404(db_session, TicketType, ticket_type_id, "Ticket type not found")


@router.post("/types")
def create_ticket_type(
    ticket_type: TicketType,
    db_session: Session = Depends(get_session),
) -> TicketType:
    """Create a ticket type."""

    db_session.add(ticket_type)
    db_session.commit()
    db_session.refresh(ticket_type)

    return ticket_type


@router.patch("/types/{ticket_type_id}")
def update_ticket_type(
    ticket_type_id: str,
    ticket_type_data: TicketType,
    db_session: Session = Depends(get_session),
) -> TicketType | None:
    """Update a ticket type."""

    ticket_type = _get_by_id_or_404(db_session, TicketType, ticket_type_id, "Ticket type not found")

    for field, value in ticket_type_data.model_dump(exclude_unset=True).items():
        setattr(ticket_type, field, value)

    db_session.add(ticket_type)
    db_session.commit()
    db_session.refresh(ticket_type)

    return ticket_type


@router.delete("/types/{ticket_type_id}")
def delete_ticket_type(
    ticket_type_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete a ticket type."""

    ticket_type = _get_by_id_or_404(db_session, TicketType, ticket_type_id, "Ticket type not found")

    db_session.delete(ticket_type)
    db_session.commit()


# endregion


# region Issued tickets

@router.get("/issued")
def get_issued_tickets(db_session: Session = Depends(get_session)) -> list[IssuedTicket]:
    """Get all issued tickets."""

    stmt = select(IssuedTicket).order_by(IssuedTicket.issued_at.desc())
    return list(db_session.exec(stmt).all())


@router.get("/issued/{issued_ticket_id}")
def get_issued_ticket(
    issued_ticket_id: str,
    db_session: Session = Depends(get_session),
) -> IssuedTicket | None:
    """Get an issued ticket by ID."""

    return _get_by_id_or_404(db_session, IssuedTicket, issued_ticket_id, "Issued ticket not found")


@router.post("/issued")
def create_issued_ticket(
    issued_ticket: IssuedTicket,
    db_session: Session = Depends(get_session),
) -> IssuedTicket:
    """Create an issued ticket."""

    db_session.add(issued_ticket)
    db_session.commit()
    db_session.refresh(issued_ticket)

    return issued_ticket


@router.patch("/issued/{issued_ticket_id}")
def update_issued_ticket(
    issued_ticket_id: str,
    issued_ticket_data: IssuedTicket,
    db_session: Session = Depends(get_session),
) -> IssuedTicket | None:
    """Update an issued ticket."""

    issued_ticket = _get_by_id_or_404(db_session, IssuedTicket, issued_ticket_id, "Issued ticket not found")

    for field, value in issued_ticket_data.model_dump(exclude_unset=True).items():
        setattr(issued_ticket, field, value)

    db_session.add(issued_ticket)
    db_session.commit()
    db_session.refresh(issued_ticket)

    return issued_ticket


@router.delete("/issued/{issued_ticket_id}")
def delete_issued_ticket(
    issued_ticket_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete an issued ticket."""

    issued_ticket = _get_by_id_or_404(db_session, IssuedTicket, issued_ticket_id, "Issued ticket not found")

    db_session.delete(issued_ticket)
    db_session.commit()


# endregion


# region Ticket validations

@router.get("/validations")
def get_ticket_validations(db_session: Session = Depends(get_session)) -> list[TicketValidation]:
    """Get all ticket validations."""

    stmt = select(TicketValidation).order_by(TicketValidation.validated_at.desc())
    return list(db_session.exec(stmt).all())


@router.get("/validations/{validation_id}")
def get_ticket_validation(
    validation_id: str,
    db_session: Session = Depends(get_session),
) -> TicketValidation | None:
    """Get a ticket validation by ID."""

    return _get_by_id_or_404(db_session, TicketValidation, validation_id, "Ticket validation not found")


@router.post("/validations")
def create_ticket_validation(
    ticket_validation: TicketValidation,
    db_session: Session = Depends(get_session),
) -> TicketValidation:
    """Create a ticket validation."""

    db_session.add(ticket_validation)
    db_session.commit()
    db_session.refresh(ticket_validation)

    return ticket_validation


@router.patch("/validations/{validation_id}")
def update_ticket_validation(
    validation_id: str,
    ticket_validation_data: TicketValidation,
    db_session: Session = Depends(get_session),
) -> TicketValidation | None:
    """Update a ticket validation."""

    ticket_validation = _get_by_id_or_404(db_session, TicketValidation, validation_id, "Ticket validation not found")

    for field, value in ticket_validation_data.model_dump(exclude_unset=True).items():
        setattr(ticket_validation, field, value)

    db_session.add(ticket_validation)
    db_session.commit()
    db_session.refresh(ticket_validation)

    return ticket_validation


@router.delete("/validations/{validation_id}")
def delete_ticket_validation(
    validation_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete a ticket validation."""

    ticket_validation = _get_by_id_or_404(db_session, TicketValidation, validation_id, "Ticket validation not found")

    db_session.delete(ticket_validation)
    db_session.commit()


# endregion


# region Customer wallets

@router.get("/wallets")
def get_customer_wallets(db_session: Session = Depends(get_session)) -> list[CustomerWallet]:
    """Get all customer wallets."""

    stmt = select(CustomerWallet).order_by(CustomerWallet.customer_id)
    return list(db_session.exec(stmt).all())


@router.get("/wallets/{wallet_id}")
def get_customer_wallet(
    wallet_id: str,
    db_session: Session = Depends(get_session),
) -> CustomerWallet | None:
    """Get a customer wallet by ID."""

    return _get_by_id_or_404(db_session, CustomerWallet, wallet_id, "Customer wallet not found")


@router.post("/wallets")
def create_customer_wallet(
    customer_wallet: CustomerWallet,
    db_session: Session = Depends(get_session),
) -> CustomerWallet:
    """Create a customer wallet."""

    try:
        db_session.add(customer_wallet)
        db_session.commit()
        db_session.refresh(customer_wallet)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Customer wallet for this customer already exists")

    return customer_wallet


@router.patch("/wallets/{wallet_id}")
def update_customer_wallet(
    wallet_id: str,
    customer_wallet_data: CustomerWallet,
    db_session: Session = Depends(get_session),
) -> CustomerWallet | None:
    """Update a customer wallet."""

    customer_wallet = _get_by_id_or_404(db_session, CustomerWallet, wallet_id, "Customer wallet not found")

    for field, value in customer_wallet_data.model_dump(exclude_unset=True).items():
        setattr(customer_wallet, field, value)

    try:
        db_session.add(customer_wallet)
        db_session.commit()
        db_session.refresh(customer_wallet)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(400, "Customer wallet for this customer already exists")

    return customer_wallet


@router.delete("/wallets/{wallet_id}")
def delete_customer_wallet(
    wallet_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete a customer wallet."""

    customer_wallet = _get_by_id_or_404(db_session, CustomerWallet, wallet_id, "Customer wallet not found")

    db_session.delete(customer_wallet)
    db_session.commit()


# endregion


# region Customer wallet transactions

@router.get("/wallet-transactions")
def get_customer_wallet_transactions(db_session: Session = Depends(get_session)) -> list[CustomerWalletTransaction]:
    """Get all customer wallet transactions."""

    stmt = select(CustomerWalletTransaction).order_by(CustomerWalletTransaction.created_at.desc())
    return list(db_session.exec(stmt).all())


@router.get("/wallet-transactions/{transaction_id}")
def get_customer_wallet_transaction(
    transaction_id: str,
    db_session: Session = Depends(get_session),
) -> CustomerWalletTransaction | None:
    """Get a customer wallet transaction by ID."""

    return _get_by_id_or_404(
        db_session,
        CustomerWalletTransaction,
        transaction_id,
        "Customer wallet transaction not found",
    )


@router.post("/wallet-transactions")
def create_customer_wallet_transaction(
    customer_wallet_transaction: CustomerWalletTransaction,
    db_session: Session = Depends(get_session),
) -> CustomerWalletTransaction:
    """Create a customer wallet transaction."""

    db_session.add(customer_wallet_transaction)
    db_session.commit()
    db_session.refresh(customer_wallet_transaction)

    return customer_wallet_transaction


@router.patch("/wallet-transactions/{transaction_id}")
def update_customer_wallet_transaction(
    transaction_id: str,
    customer_wallet_transaction_data: CustomerWalletTransaction,
    db_session: Session = Depends(get_session),
) -> CustomerWalletTransaction | None:
    """Update a customer wallet transaction."""

    customer_wallet_transaction = _get_by_id_or_404(
        db_session,
        CustomerWalletTransaction,
        transaction_id,
        "Customer wallet transaction not found",
    )

    for field, value in customer_wallet_transaction_data.model_dump(exclude_unset=True).items():
        setattr(customer_wallet_transaction, field, value)

    db_session.add(customer_wallet_transaction)
    db_session.commit()
    db_session.refresh(customer_wallet_transaction)

    return customer_wallet_transaction


@router.delete("/wallet-transactions/{transaction_id}")
def delete_customer_wallet_transaction(
    transaction_id: str,
    db_session: Session = Depends(get_session),
):
    """Delete a customer wallet transaction."""

    customer_wallet_transaction = _get_by_id_or_404(
        db_session,
        CustomerWalletTransaction,
        transaction_id,
        "Customer wallet transaction not found",
    )

    db_session.delete(customer_wallet_transaction)
    db_session.commit()


# endregion