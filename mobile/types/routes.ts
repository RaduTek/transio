export enum VehicleType {
    BUS = "Bus",
    TRAIN = "Train",
    TRAM = "Tram",
    FERRY = "Ferry",
    SUBWAY = "Subway",
    TROLLEY = "Trolley",
    OTHER = "Other",
}

export interface TransitStop {
    id: string;
    name: string;
    description?: string;
    lat: number;
    lon: number;
    address?: string;
}

export interface TransitCategory {
    id: string;
    code: string;
    name: string;
    vehicle_type: VehicleType;
    description?: string;
}

export interface TransitRoute {
    id: string;
    code: string;
    name: string;
    category_id: string;
    description?: string;
    private_notes?: string;
}

export interface TransitSubRoute {
    id: string;
    code: string;
    name: string;
    parent_route_id: string;
    description?: string;
    private_notes?: string;
}

export interface TransitSubRouteStop {
    id: string;
    subroute_id: string;
    stop_id: string;
    stop_order: number;
    description?: string;
    private_notes?: string;
}

export interface TransitShift {
    id: string;
    vehicle_id: string;
    route_id: string;
    subroute_id?: string;
    shift_start: string; // ISO 8601 format
    shift_end?: string; // ISO 8601 format
}
