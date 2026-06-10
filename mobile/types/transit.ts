export interface TransitStop {
    id: string;
    name: string;
    description: string;
    lat: number;
    lon: number;
    address: string;
}

export enum VehicleType {
    BUS = "Bus",
    TRAIN = "Train",
    TRAM = "Tram",
    FERRY = "Ferry",
    SUBWAY = "Subway",
    TROLLEY = "Trolley",
    OTHER = "Other",
}

export interface TransitCategory {
    id: string;
    code: string;
    name: string;
    vehicle_type: VehicleType;
    description: string;
}