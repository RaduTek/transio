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
