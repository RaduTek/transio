import os
import sys
import time
from dataclasses import dataclass
from typing import Any

import nfc
import requests
from PySide6 import QtCore, QtGui, QtWidgets


@dataclass
class AppConfig:
    api_base_url: str
    api_key: str
    nfc_conn_string: str
    auth_mode: str
    request_timeout_seconds: float

    @classmethod
    def from_env(cls) -> "AppConfig":
        api_base_url = os.getenv("TRANSIO_API_BASE_URL", "").strip().rstrip("/")
        api_key = os.getenv("TRANSIO_DEVICE_API_KEY", "").strip()
        nfc_conn_string = (
            os.getenv("TRANSIO_NFC_CONN_STRING")
            or os.getenv("TRANSIO_NFC_CONN")
            or os.getenv("NFC_CLF_CONN")
            or ""
        ).strip()
        auth_mode = os.getenv("TRANSIO_CARD_AUTH_MODE", "Physical Card").strip() or "Physical Card"

        timeout_raw = os.getenv("TRANSIO_API_TIMEOUT_SECONDS", "8")
        try:
            timeout = float(timeout_raw)
        except ValueError:
            timeout = 8.0

        return cls(
            api_base_url=api_base_url,
            api_key=api_key,
            nfc_conn_string=nfc_conn_string,
            auth_mode=auth_mode,
            request_timeout_seconds=max(timeout, 1.0),
        )


class ApiClientWorker(QtCore.QObject):
    state_loaded = QtCore.Signal(dict)
    route_loaded = QtCore.Signal(str, str)
    validation_loaded = QtCore.Signal(dict)
    api_error = QtCore.Signal(str)

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self._config.api_key}"})

    @QtCore.Slot()
    def fetch_state(self) -> None:
        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return
        if not self._config.api_key:
            self.api_error.emit("TRANSIO_DEVICE_API_KEY is not configured")
            return

        url = f"{self._config.api_base_url}/device/validator/state"
        try:
            response = self._session.get(url, timeout=self._config.request_timeout_seconds)
            response.raise_for_status()
            self.state_loaded.emit(response.json())
        except requests.RequestException as exc:
            self.api_error.emit(f"Failed to load validator state: {exc}")

    @QtCore.Slot(str)
    def fetch_route_name(self, route_id: str) -> None:
        if not route_id:
            return

        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return

        url = f"{self._config.api_base_url}/public/routes/{route_id}"
        try:
            response = self._session.get(url, timeout=self._config.request_timeout_seconds)
            response.raise_for_status()
            payload = response.json()
            route_name = payload.get("name") or payload.get("code") or route_id
            self.route_loaded.emit(route_id, route_name)
        except requests.RequestException as exc:
            self.api_error.emit(f"Failed to load route details: {exc}")

    @QtCore.Slot(str)
    def validate_uid(self, uid: str) -> None:
        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return
        if not self._config.api_key:
            self.api_error.emit("TRANSIO_DEVICE_API_KEY is not configured")
            return

        url = f"{self._config.api_base_url}/device/validator/validate"
        payload = {
            "card_id": uid,
            "auth_mode": self._config.auth_mode,
        }

        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self._config.request_timeout_seconds,
            )

            if response.status_code >= 400:
                detail = "Validation failed"
                try:
                    body = response.json()
                    detail = body.get("detail", detail)
                except ValueError:
                    pass
                self.validation_loaded.emit(
                    {
                        "ok": False,
                        "uid": uid,
                        "detail": detail,
                        "status_code": response.status_code,
                    }
                )
                return

            body = response.json()
            self.validation_loaded.emit(
                {
                    "ok": True,
                    "uid": uid,
                    "payload": body,
                }
            )
        except requests.RequestException as exc:
            self.validation_loaded.emit(
                {
                    "ok": False,
                    "uid": uid,
                    "detail": str(exc),
                    "status_code": None,
                }
            )


class NfcWorker(QtCore.QObject):
    status_changed = QtCore.Signal(str)
    card_detected = QtCore.Signal(str)
    scan_error = QtCore.Signal(str)

    def __init__(self, nfc_conn_string: str, dedupe_seconds: float = 1.5):
        super().__init__()
        self._nfc_conn_string = nfc_conn_string
        self._dedupe_seconds = dedupe_seconds
        self._stop_requested = False
        self._last_uid = ""
        self._last_seen_monotonic = 0.0

    @QtCore.Slot()
    def run(self) -> None:
        if not self._nfc_conn_string:
            self.scan_error.emit("TRANSIO_NFC_CONN_STRING is not configured")
            return

        clf = None
        try:
            clf = nfc.ContactlessFrontend(self._nfc_conn_string)
            self.status_changed.emit(f"Scanner connected ({self._nfc_conn_string})")

            while not self._stop_requested:

                def on_connect(tag: Any) -> bool:
                    uid = self._extract_uid(tag)
                    if not uid:
                        self.status_changed.emit("Card detected, but UID is unavailable")
                        return False

                    if not self._is_mifare_classic(tag):
                        self.status_changed.emit(f"Ignored non-Mifare Classic card (UID: {uid})")
                        return False

                    now = time.monotonic()
                    if uid == self._last_uid and (now - self._last_seen_monotonic) < self._dedupe_seconds:
                        return False

                    self._last_uid = uid
                    self._last_seen_monotonic = now
                    self.card_detected.emit(uid)
                    return False

                clf.connect(
                    rdwr={"on-connect": on_connect},
                    terminate=lambda: self._stop_requested,
                )
        except Exception as exc:  # noqa: BLE001
            self.scan_error.emit(f"NFC scanner error: {exc}")
        finally:
            if clf is not None:
                try:
                    clf.close()
                except Exception:
                    pass
            self.status_changed.emit("Scanner stopped")

    @QtCore.Slot()
    def stop(self) -> None:
        self._stop_requested = True

    def _extract_uid(self, tag: Any) -> str:
        identifier = getattr(tag, "identifier", None)
        if identifier:
            return identifier.hex().upper()
        return ""

    def _is_mifare_classic(self, tag: Any) -> bool:
        class_name = tag.__class__.__name__.lower()
        if "mifareclassic" in class_name:
            return True

        tag_text = str(tag).lower()
        return "mifare classic" in tag_text


class ValidatorApp(QtWidgets.QWidget):
    request_state = QtCore.Signal()
    request_route = QtCore.Signal(str)
    request_validate = QtCore.Signal(str)

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._route_name_cache: dict[str, str] = {}

        self.setWindowTitle("Transio Ticket Validator")
        self.setFixedSize(480, 480)

        self._build_ui()
        self._setup_api_worker()
        self._setup_nfc_worker()

        self._state_timer = QtCore.QTimer(self)
        self._state_timer.setInterval(30000)
        self._state_timer.timeout.connect(self._request_state)

        self._request_state()
        self._state_timer.start()
        self._start_scanning()

    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QtWidgets.QLabel("Ticket Validator", alignment=QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title.setFont(title_font)

        self._scanner_status = QtWidgets.QLabel("Scanner: idle")
        self._device_label = QtWidgets.QLabel("Device: -")
        self._vehicle_label = QtWidgets.QLabel("Vehicle: -")
        self._shift_label = QtWidgets.QLabel("Shift: -")
        self._route_label = QtWidgets.QLabel("Route: -")
        self._last_uid_label = QtWidgets.QLabel("Last card UID: -")

        self._result_box = QtWidgets.QTextEdit()
        self._result_box.setReadOnly(True)
        self._result_box.setPlaceholderText("Validation results will appear here")

        controls = QtWidgets.QHBoxLayout()
        self._refresh_btn = QtWidgets.QPushButton("Refresh State")
        self._start_btn = QtWidgets.QPushButton("Start Scan")
        self._stop_btn = QtWidgets.QPushButton("Stop Scan")
        controls.addWidget(self._refresh_btn)
        controls.addWidget(self._start_btn)
        controls.addWidget(self._stop_btn)

        root.addWidget(title)
        root.addWidget(self._scanner_status)
        root.addWidget(self._device_label)
        root.addWidget(self._vehicle_label)
        root.addWidget(self._shift_label)
        root.addWidget(self._route_label)
        root.addWidget(self._last_uid_label)
        root.addWidget(self._result_box, 1)
        root.addLayout(controls)

        self._refresh_btn.clicked.connect(self._request_state)
        self._start_btn.clicked.connect(self._start_scanning)
        self._stop_btn.clicked.connect(self._stop_scanning)
        self._set_scan_button_state(scanning=False)

    def _setup_api_worker(self) -> None:
        self._api_thread = QtCore.QThread(self)
        self._api_worker = ApiClientWorker(self._config)
        self._api_worker.moveToThread(self._api_thread)
        self._api_thread.start()

        self.request_state.connect(self._api_worker.fetch_state)
        self.request_route.connect(self._api_worker.fetch_route_name)
        self.request_validate.connect(self._api_worker.validate_uid)

        self._api_worker.state_loaded.connect(self._on_state_loaded)
        self._api_worker.route_loaded.connect(self._on_route_loaded)
        self._api_worker.validation_loaded.connect(self._on_validation_loaded)
        self._api_worker.api_error.connect(self._on_api_error)

    def _setup_nfc_worker(self) -> None:
        self._nfc_thread: QtCore.QThread | None = None
        self._nfc_worker: NfcWorker | None = None

    def _set_scan_button_state(self, scanning: bool) -> None:
        self._start_btn.setEnabled(not scanning)
        self._stop_btn.setEnabled(scanning)

    @QtCore.Slot()
    def _start_scanning(self) -> None:
        if self._nfc_thread is not None:
            return

        self._nfc_thread = QtCore.QThread(self)
        self._nfc_worker = NfcWorker(self._config.nfc_conn_string)
        self._nfc_worker.moveToThread(self._nfc_thread)

        self._nfc_thread.started.connect(self._nfc_worker.run)
        self._nfc_worker.status_changed.connect(self._on_scanner_status)
        self._nfc_worker.scan_error.connect(self._on_scanner_error)
        self._nfc_worker.card_detected.connect(self._on_card_detected)
        self._nfc_thread.finished.connect(self._on_scan_stopped)

        self._nfc_thread.start()
        self._set_scan_button_state(scanning=True)
        self._on_scanner_status("Starting scanner...")

    @QtCore.Slot()
    def _stop_scanning(self) -> None:
        if self._nfc_worker is None or self._nfc_thread is None:
            return

        QtCore.QMetaObject.invokeMethod(self._nfc_worker, "stop", QtCore.Qt.QueuedConnection)
        self._nfc_thread.quit()
        self._nfc_thread.wait(2000)

    @QtCore.Slot()
    def _on_scan_stopped(self) -> None:
        self._nfc_worker = None
        self._nfc_thread = None
        self._set_scan_button_state(scanning=False)

    @QtCore.Slot(str)
    def _on_scanner_status(self, message: str) -> None:
        self._scanner_status.setText(f"Scanner: {message}")

    @QtCore.Slot(str)
    def _on_scanner_error(self, message: str) -> None:
        self._scanner_status.setText(f"Scanner: {message}")
        self._append_result(message)
        self._stop_scanning()

    @QtCore.Slot(str)
    def _on_card_detected(self, uid: str) -> None:
        self._last_uid_label.setText(f"Last card UID: {uid}")
        self._append_result(f"Scanned card UID: {uid}")
        self.request_validate.emit(uid)

    @QtCore.Slot()
    def _request_state(self) -> None:
        self.request_state.emit()

    @QtCore.Slot(dict)
    def _on_state_loaded(self, payload: dict) -> None:
        device = payload.get("device") or {}
        vehicle = payload.get("vehicle") or {}
        shift = payload.get("transit_shift") or {}

        self._device_label.setText(f"Device: {device.get('code', '-')}")
        self._vehicle_label.setText(f"Vehicle: {vehicle.get('code', '-') if vehicle else '-'}")

        if shift:
            route_id = shift.get("route_id")
            self._shift_label.setText(f"Shift: active ({shift.get('id', '-')})")

            if route_id:
                route_name = self._route_name_cache.get(route_id)
                if route_name:
                    self._route_label.setText(f"Route: {route_name}")
                else:
                    self._route_label.setText(f"Route: {route_id}")
                    self.request_route.emit(route_id)
            else:
                self._route_label.setText("Route: -")
        else:
            self._shift_label.setText("Shift: none")
            self._route_label.setText("Route: -")

    @QtCore.Slot(str, str)
    def _on_route_loaded(self, route_id: str, route_name: str) -> None:
        self._route_name_cache[route_id] = route_name
        self._route_label.setText(f"Route: {route_name}")

    @QtCore.Slot(dict)
    def _on_validation_loaded(self, result: dict) -> None:
        uid = result.get("uid", "-")
        if result.get("ok"):
            payload = result.get("payload") or {}
            ticket = payload.get("ticket") or {}
            ticket_type = payload.get("ticket_type") or {}
            message = (
                f"VALID | UID {uid} | "
                f"Ticket {ticket.get('id', '-')[:8]} | "
                f"Type {ticket_type.get('name', ticket_type.get('code', '-'))}"
            )
            self._append_result(message)
        else:
            detail = result.get("detail", "Validation failed")
            status = result.get("status_code")
            if status is not None:
                self._append_result(f"INVALID ({status}) | UID {uid} | {detail}")
            else:
                self._append_result(f"INVALID | UID {uid} | {detail}")

    @QtCore.Slot(str)
    def _on_api_error(self, message: str) -> None:
        self._append_result(message)

    def _append_result(self, text: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        self._result_box.append(f"[{timestamp}] {text}")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._state_timer.stop()

        self._stop_scanning()

        self._api_thread.quit()
        self._api_thread.wait(2000)

        super().closeEvent(event)


def main() -> int:
    config = AppConfig.from_env()

    app = QtWidgets.QApplication(sys.argv)
    widget = ValidatorApp(config)
    widget.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
