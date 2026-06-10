# Transio Vehicle On-Board Controller application

This is the application that runs on the transit vehicle's on-board controller.

This application connects to the Transio server, supplies live location data from the vehicle's GPS sensor, and gives the driver access to shift controls.

## Hardware assumptions

- Raspberry Pi 3
- USB GPS receiver on `/dev/ttyACM0`
- PN532 NFC reader on USB (`/dev/ttyUSB0`, `nfcpy` connection string defaults to `tty:USB0:pn532`)
- 800x600 display

## Environment variables

- `TRANSIO_API_BASE_URL` (required)
- `TRANSIO_DEVICE_API_KEY` (required)
- `TRANSIO_NFC_CONN_STRING` (optional, default: `tty:USB0:pn532`)
- `TRANSIO_GPS_DEVICE` (optional, default: `/dev/ttyACM0`)
- `TRANSIO_DRIVER_AUTH_MODE` (optional, default: `Physical Card`)
- `TRANSIO_API_TIMEOUT_SECONDS` (optional, default: `8`)
- `TRANSIO_TELEMETRY_FAST_INTERVAL_SECONDS` (optional, default: `10`)
- `TRANSIO_TELEMETRY_IDLE_INTERVAL_SECONDS` (optional, default: `600`)
- `TRANSIO_TELEMETRY_IDLE_AFTER_SECONDS` (optional, default: `600`)
- `TRANSIO_MOVING_SPEED_THRESHOLD_KMPH` (optional, default: `2.0`)

## Run

```bash
cd devices/vehicle
python vehicle.py
```

## Telemetry behavior

- While moving: telemetry is sent every 10 seconds.
- While idle: after 10 continuous minutes below movement threshold, telemetry is sent every 10 minutes.
- Once movement resumes: telemetry immediately returns to fast cadence.

## Operational flow

1. App waits for driver badge scan.
2. Driver scan logs in via `/device/vehicle/shift/login`.
3. Driver selects route/subroute and starts shift.
4. GPS telemetry uploads continuously based on movement-aware cadence.
5. Driver ends shift or logs out (logout auto-ends active shift).

## Troubleshooting

- If GPS disconnects, the worker retries connection automatically.
- If NFC disconnects, the scanner status panel will show the error.
- Ensure the runtime user has permission for serial devices (`/dev/ttyACM0`, `/dev/ttyUSB0`).
