export enum VehicleType {
    BUS = "Bus",
    TRAIN = "Train",
    TRAM = "Tram",
    FERRY = "Ferry",
    SUBWAY = "Subway",
    TROLLEY = "Trolley",
    OTHER = "Other",
}

export interface Vehicle {
    id: string;
    code: string;
    vehicle_type: VehicleType;
    registration_number: string;
    description?: string;
    private_notes?: string;
}

export enum DeviceType {
    VEHICLE_OBC = "Vehicle OBC",
    VALIDATOR = "Validator",
    DISPLAY_SCREEN = "Display Screen",
    TICKET_MACHINE = "Ticket Vending Machine",
    OTHER = "Other",
}

export interface Device {
    id: string;
    code: string;
    device_type: DeviceType;
    vehicle_id?: string;
    description?: string;
    private_notes?: string;
}
