export enum EmployeeRole {
    DRIVER = "Driver",
    DISPATCHER = "Dispatcher",
    CONTROLLER = "Controller",
    MANAGER = "Manager",
    SALES = "Sales",
    SUPPORT = "Support",
    TECHNICIAN = "Technician",
    MECHANIC = "Mechanic",
    OTHER = "Other",
}

export interface Employee {
    id: string;
    email: string;
    phone: string;
    first_name: string;
    last_name: string;
    active: boolean;
    role: EmployeeRole;
    customer_id: string;
    employment_start_date: string; // YYYY-MM-DD format
}

export interface Customer {
    id: string;
    email: string;
    phone: string;
    first_name: string;
    last_name: string;
    registered_date: string; // ISO 8601 format
    active: boolean;
}

export interface ActivePassInfo {
    ticket_id: string;
    ticket_type_name: string;
    expires_at: string; // ISO 8601 format
    validated_at: string | null; // ISO 8601 format
}

export interface ProfileData {
    customer: Customer;
    wallet_balance: number; // Balance in cents
    active_pass: ActivePassInfo | null;
    valid_tickets_count: number;
}
