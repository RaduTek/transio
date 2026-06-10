from __future__ import annotations

from datetime import datetime, timezone
import time

import serial
from PySide6 import QtCore


class GpsWorker(QtCore.QObject):
    status_changed = QtCore.Signal(str)
    telemetry_ready = QtCore.Signal(dict)
    telemetry_skipped = QtCore.Signal(str)
    gps_error = QtCore.Signal(str)

    def __init__(
        self,
        device_path: str,
        fast_interval_seconds: float,
        idle_interval_seconds: float,
        idle_after_seconds: float,
        movement_speed_threshold_kmph: float,
    ):
        super().__init__()
        self._device_path = device_path
        self._fast_interval = fast_interval_seconds
        self._idle_interval = idle_interval_seconds
        self._idle_after = idle_after_seconds
        self._movement_threshold = movement_speed_threshold_kmph

        self._stop_requested = False
        self._last_emit_monotonic = 0.0
        self._idle_since_monotonic: float | None = None
        self._latest_fix: dict | None = None

    @QtCore.Slot()
    def run(self) -> None:
        while not self._stop_requested:
            ser = None
            try:
                self.status_changed.emit(f"Connecting GPS ({self._device_path})")
                ser = serial.Serial(self._device_path, baudrate=9600, timeout=1.0)
                self.status_changed.emit("GPS connected")

                while not self._stop_requested:
                    line = ser.readline().decode("ascii", errors="ignore").strip()
                    if not line:
                        self._maybe_emit_telemetry()
                        continue

                    parsed = self._parse_nmea_line(line)
                    if parsed:
                        self._latest_fix = parsed
                        self._maybe_emit_telemetry()
            except Exception as exc:  # noqa: BLE001
                self.gps_error.emit(f"GPS read error: {exc}")
                self.status_changed.emit("Retrying GPS connection in 3s")
                time.sleep(3.0)
            finally:
                if ser is not None:
                    try:
                        ser.close()
                    except Exception:
                        pass

        self.status_changed.emit("GPS worker stopped")

    @QtCore.Slot()
    def stop(self) -> None:
        self._stop_requested = True

    def _maybe_emit_telemetry(self) -> None:
        if not self._latest_fix:
            return

        speed = self._latest_fix.get("speed_kmph")
        moving = speed is not None and speed >= self._movement_threshold

        now_mono = time.monotonic()
        if moving:
            self._idle_since_monotonic = None
            interval = self._fast_interval
        else:
            if self._idle_since_monotonic is None:
                self._idle_since_monotonic = now_mono
            idle_duration = now_mono - self._idle_since_monotonic
            interval = self._idle_interval if idle_duration >= self._idle_after else self._fast_interval

        if self._last_emit_monotonic > 0.0 and (now_mono - self._last_emit_monotonic) < interval:
            return

        lat = self._latest_fix.get("lat")
        lon = self._latest_fix.get("lon")
        if lat is None or lon is None:
            self.telemetry_skipped.emit("Skipping telemetry: no GPS coordinates yet")
            return

        payload = {
            "timestamp": self._latest_fix.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "lat": lat,
            "lon": lon,
            "speed_kmph": speed,
            "heading_degrees": self._latest_fix.get("heading_degrees"),
        }

        self._last_emit_monotonic = now_mono
        self.telemetry_ready.emit(payload)

    def _parse_nmea_line(self, line: str) -> dict | None:
        if not line.startswith("$"):
            return None

        parts = line.split(",")
        sentence = parts[0]

        if sentence.endswith("RMC"):
            return self._parse_rmc(parts)

        if sentence.endswith("GGA"):
            return self._parse_gga(parts)

        return None

    def _parse_rmc(self, parts: list[str]) -> dict | None:
        if len(parts) < 10:
            return None

        status = parts[2]
        if status != "A":
            return None

        lat = _parse_nmea_lat_lon(parts[3], parts[4])
        lon = _parse_nmea_lat_lon(parts[5], parts[6])
        speed_knots = _safe_float(parts[7])
        heading = _safe_float(parts[8])

        speed_kmph = speed_knots * 1.852 if speed_knots is not None else None

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": lat,
            "lon": lon,
            "speed_kmph": speed_kmph,
            "heading_degrees": heading,
        }

    def _parse_gga(self, parts: list[str]) -> dict | None:
        if len(parts) < 6:
            return None

        lat = _parse_nmea_lat_lon(parts[2], parts[3])
        lon = _parse_nmea_lat_lon(parts[4], parts[5])

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": lat,
            "lon": lon,
            "speed_kmph": None,
            "heading_degrees": None,
        }


def _safe_float(value: str) -> float | None:
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def _parse_nmea_lat_lon(raw: str, direction: str) -> float | None:
    if not raw or not direction:
        return None

    try:
        value = float(raw)
    except ValueError:
        return None

    degrees = int(value / 100)
    minutes = value - (degrees * 100)
    decimal = degrees + (minutes / 60.0)

    if direction in ("S", "W"):
        decimal *= -1.0

    return decimal
