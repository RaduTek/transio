export enum FareType {
    STANDARD = "Standard",
    STUDENT = "Student",
    SENIOR = "Senior",
    DISCOUNT = "Discount",
    SURCHARGE = "Surcharge",
    OTHER = "Other",
}

export enum TicketCategory {
    TICKET = "Ticket",
    PASS = "Pass",
    OTHER = "Other",
}

export interface TicketType {
    id: string;
    name: string;
    category: TicketCategory;
    unit_price: number; // Price in cents
    valid_for_routes?: string; // Comma-separated route IDs
    valid_for_rides?: number;
    valid_for_minutes?: number;
    fare_type: FareType;
    published: boolean;
    active: boolean;
    description?: string;
    private_notes?: string;
}

export interface IssuedTicket {
    id: string;
    ticket_type_id: string;
    customer_id: string;
    issued_at: string; // ISO 8601 format
    expires_at: string; // ISO 8601 format
    fare_type: FareType;
    final_price: number; // Price in cents
    validated_at?: string; // ISO 8601 format
    flagged: boolean;
}

export interface TicketValidation {
    id: string;
    issued_ticket_id: string;
    device_id: string;
    vehicle_id: string;
    validated_at: string; // ISO 8601 format
    validation_result: string;
}

export interface CustomerWallet {
    id: string;
    customer_id: string;
    balance: number; // Balance in cents
    last_topup_at?: string; // ISO 8601 format
    active: boolean;
}

export enum WalletTransactionType {
    TOPUP = "Top-up",
    PURCHASE = "Purchase",
    REFUND = "Refund",
    OTHER = "Other",
}

export interface CustomerWalletTransaction {
    id: string;
    wallet_id: string;
    amount: number; // Amount in cents
    transaction_type: WalletTransactionType;
    created_at: string; // ISO 8601 format
    flagged: boolean;
}
