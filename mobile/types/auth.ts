export enum AuthMode {
    PHYSICAL_CARD = "Physical Card",
    DIGITAL_CARD = "Digital Card",
    PASSWORD = "Password",
    KEY = "Key",
    KEYPAIR = "Key Pair",
    OTHER = "Other",
}

export interface CustomerAuth {
    id: string;
    customer_id: string;
    auth_mode: AuthMode;
    auth_details: string;
    created_at: string; // ISO 8601 format
    ttl_seconds: number;
    valid: boolean;
}

export interface EmployeeAuth {
    id: string;
    employee_id: string;
    auth_mode: AuthMode;
    auth_details: string;
    created_at: string; // ISO 8601 format
    ttl_seconds: number;
    valid: boolean;
}

export interface DeviceAuth {
    id: string;
    device_id: string;
    auth_mode: AuthMode;
    auth_details: string;
    created_at: string; // ISO 8601 format
    ttl_seconds: number;
    valid: boolean;
}
