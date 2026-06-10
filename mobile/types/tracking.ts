export interface VehicleLocationLog {
    id: string;
    timestamp: string; // ISO 8601 format
    vehicle_id: string;
    lat: number;
    lon: number;
    speed_kmph?: number;
    heading_degrees?: number; // 0-360 degrees from north
}

export interface TransitShiftArrivalLog {
    id: string;
    timestamp: string; // ISO 8601 format
    shift_id?: string;
    stop_id: string;
}
