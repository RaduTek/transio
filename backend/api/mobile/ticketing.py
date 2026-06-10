"""Ticketing routes for mobile app"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.database import get_session
from backend.data.ticketing import (
    IssuedTicket,
    TicketType,
    CustomerWallet,
    CustomerWalletTransaction,
    WalletTransactionType
)
from backend.data.users import Customer
from backend.data import generate_uuid

from .auth import get_current_customer

router = APIRouter(
    dependencies=[Depends(get_current_customer)],
    prefix="/ticketing"
)


class PurchaseTicketRequest(BaseModel):
    ticket_type_id: str
    payment_method: str  # "wallet" or "mock_card"
    mock_card_number: str | None = None


class PurchaseTicketResponse(BaseModel):
    issued_ticket: IssuedTicket
    message: str


@router.get("/my-tickets")
def get_my_tickets(
    customer: Customer = Depends(get_current_customer),
    db_session: Session = Depends(get_session)
) -> list[IssuedTicket]:
    """Get all tickets and passes owned by the current customer"""
    
    stmt = (
        select(IssuedTicket)
        .where(IssuedTicket.customer_id == customer.id)
        .order_by(IssuedTicket.issued_at.desc())
    )
    
    tickets = db_session.exec(stmt).all()
    
    return list(tickets)


@router.get("/available-tickets")
def get_available_tickets(
    db_session: Session = Depends(get_session)
) -> list[TicketType]:
    """Get all ticket types available for purchase"""
    
    stmt = (
        select(TicketType)
        .where(
            TicketType.published == True,
            TicketType.active == True
        )
        .order_by(TicketType.category, TicketType.name)
    )
    
    ticket_types = db_session.exec(stmt).all()
    
    return list(ticket_types)


@router.post("/purchase")
def purchase_ticket(
    request: PurchaseTicketRequest,
    customer: Customer = Depends(get_current_customer),
    db_session: Session = Depends(get_session)
) -> PurchaseTicketResponse:
    """Purchase a ticket using wallet or mock payment method"""
    
    # Fetch the ticket type
    stmt = select(TicketType).where(TicketType.id == request.ticket_type_id).limit(1)
    ticket_type = db_session.exec(stmt).first()
    
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    
    if not ticket_type.published or not ticket_type.active:
        raise HTTPException(status_code=400, detail="Ticket type is not available for purchase")
    
    final_price = ticket_type.unit_price
    
    # Handle payment
    if request.payment_method == "wallet":
        # Get customer wallet
        stmt = select(CustomerWallet).where(CustomerWallet.customer_id == customer.id).limit(1)
        wallet = db_session.exec(stmt).first()
        
        if not wallet:
            raise HTTPException(status_code=400, detail="Customer wallet not found")
        
        if not wallet.active:
            raise HTTPException(status_code=400, detail="Wallet is not active")
        
        if wallet.balance < final_price:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        
        # Deduct from wallet
        wallet.balance -= final_price
        db_session.add(wallet)
        
        # Create wallet transaction
        transaction = CustomerWalletTransaction(
            id=generate_uuid(),
            wallet_id=wallet.id,
            amount=-final_price,
            transaction_type=WalletTransactionType.PURCHASE,
            created_at=datetime.now(),
            flagged=False
        )
        db_session.add(transaction)
        
    elif request.payment_method == "mock_card":
        # Mock payment - simulate card payment
        if not request.mock_card_number:
            raise HTTPException(status_code=400, detail="Mock card number is required")
        
        # Simulate payment validation
        if len(request.mock_card_number) < 13:
            raise HTTPException(status_code=400, detail="Invalid card number")
        
        # Mock payment always succeeds if card number is valid
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    # Calculate expiry time
    issued_at = datetime.now()
    
    # Default expiry: 30 days from now
    expires_at = issued_at + timedelta(days=30)
    
    # If ticket has a validity period, adjust expiry
    if ticket_type.valid_for_minutes:
        # For time-limited tickets, expiry starts from first validation
        # But we set a reasonable purchase expiry
        expires_at = issued_at + timedelta(days=90)
    
    # Create issued ticket
    issued_ticket = IssuedTicket(
        id=generate_uuid(),
        ticket_type_id=ticket_type.id,
        customer_id=customer.id,
        issued_at=issued_at,
        expires_at=expires_at,
        fare_type=ticket_type.fare_type,
        final_price=final_price,
        validated_at=None,
        flagged=False
    )
    
    db_session.add(issued_ticket)
    db_session.commit()
    db_session.refresh(issued_ticket)
    
    return PurchaseTicketResponse(
        issued_ticket=issued_ticket,
        message="Ticket purchased successfully"
    )
