"""Profile routes for mobile app"""

from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.data.users import Customer
from backend.data.auth import AuthMode, CustomerAuth
from backend.data.ticketing import IssuedTicket, TicketType, TicketCategory, CustomerWallet

from .auth import get_current_token, get_current_customer

router = APIRouter(
    dependencies=[Depends(get_current_token)],
    prefix="/profile"
)


class ActivePassInfo(BaseModel):
    ticket_id: str
    ticket_type_name: str
    expires_at: str
    validated_at: str | None


class ProfileDataResponse(BaseModel):
    customer: Customer
    wallet_balance: int  # Balance in cents
    active_pass: ActivePassInfo | None
    valid_tickets_count: int


@router.get("/customerInfo")
def get_customer_info(customer: Customer = Depends(get_current_customer)) -> Customer:
    return customer


@router.get("/data")
def get_profile_data(
    customer: Customer = Depends(get_current_customer),
    db_session: Session = Depends(get_session)
) -> ProfileDataResponse:
    """Get comprehensive profile data including customer info, wallet, and ticketing summary"""
    
    now = datetime.now()
    
    # Get wallet balance
    wallet_stmt = select(CustomerWallet).where(CustomerWallet.customer_id == customer.id).limit(1)
    wallet = db_session.exec(wallet_stmt).first()
    wallet_balance = wallet.balance if wallet else 0
    
    # Get active pass (most recent non-expired pass)
    pass_stmt = (
        select(IssuedTicket, TicketType)
        .join(TicketType, IssuedTicket.ticket_type_id == TicketType.id)
        .where(
            IssuedTicket.customer_id == customer.id,
            IssuedTicket.expires_at > now,
            TicketType.category == TicketCategory.PASS
        )
        .order_by(IssuedTicket.issued_at.desc())
        .limit(1)
    )
    
    pass_result = db_session.exec(pass_stmt).first()
    active_pass = None
    
    if pass_result:
        issued_ticket, ticket_type = pass_result
        active_pass = ActivePassInfo(
            ticket_id=issued_ticket.id,
            ticket_type_name=ticket_type.name,
            expires_at=issued_ticket.expires_at.isoformat(),
            validated_at=issued_ticket.validated_at.isoformat() if issued_ticket.validated_at else None
        )
    
    # Count valid (non-expired) tickets
    tickets_count_stmt = (
        select(func.count(IssuedTicket.id))
        .join(TicketType, IssuedTicket.ticket_type_id == TicketType.id)
        .where(
            IssuedTicket.customer_id == customer.id,
            IssuedTicket.expires_at > now,
            TicketType.category == TicketCategory.TICKET
        )
    )
    
    valid_tickets_count = db_session.exec(tickets_count_stmt).one()
    
    return ProfileDataResponse(
        customer=customer,
        wallet_balance=wallet_balance,
        active_pass=active_pass,
        valid_tickets_count=valid_tickets_count
    )