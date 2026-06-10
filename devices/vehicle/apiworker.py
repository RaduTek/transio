import requests

from PySide6 import QtCore

from config import AppConfig


class ApiClientWorker(QtCore.QObject):
    state_loaded = QtCore.Signal(dict)
    routes_loaded = QtCore.Signal(list)
    subroutes_loaded = QtCore.Signal(str, list)
    driver_login_loaded = QtCore.Signal(dict)
    shift_started = QtCore.Signal(dict)
    shift_ended = QtCore.Signal(dict)
    driver_logged_out = QtCore.Signal(dict)
    telemetry_result = QtCore.Signal(dict)
    api_error = QtCore.Signal(str)

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self._config.api_key}"})

    @QtCore.Slot()
    def fetch_state(self) -> None:
        if not self._validate_core_config():
            return

        try:
            response = self._session.get(
                f"{self._config.api_base_url}/device/vehicle/state",
                timeout=self._config.api_timeout_seconds,
            )
            response.raise_for_status()
            self.state_loaded.emit(response.json())
        except requests.RequestException as exc:
            self.api_error.emit(f"Failed to load vehicle state: {exc}")

    @QtCore.Slot()
    def fetch_routes(self) -> None:
        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return

        try:
            response = self._session.get(
                f"{self._config.api_base_url}/public/routes",
                timeout=self._config.api_timeout_seconds,
            )
            response.raise_for_status()
            self.routes_loaded.emit(response.json())
        except requests.RequestException as exc:
            self.api_error.emit(f"Failed to load routes: {exc}")

    @QtCore.Slot(str)
    def fetch_subroutes(self, route_id: str) -> None:
        if not route_id:
            self.subroutes_loaded.emit(route_id, [])
            return

        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return

        try:
            response = self._session.get(
                f"{self._config.api_base_url}/public/routes/{route_id}/subroutes",
                timeout=self._config.api_timeout_seconds,
            )
            response.raise_for_status()
            self.subroutes_loaded.emit(route_id, response.json())
        except requests.RequestException as exc:
            self.api_error.emit(f"Failed to load subroutes: {exc}")

    @QtCore.Slot(str)
    def login_driver(self, card_id: str) -> None:
        if not self._validate_core_config():
            return

        payload = {
            "card_id": card_id,
            "auth_mode": self._config.driver_auth_mode,
        }

        try:
            response = self._session.post(
                f"{self._config.api_base_url}/device/vehicle/shift/login",
                json=payload,
                timeout=self._config.api_timeout_seconds,
            )
            self.driver_login_loaded.emit(self._normalize_response(response, context="Driver login"))
        except requests.RequestException as exc:
            self.driver_login_loaded.emit({"ok": False, "detail": str(exc), "status_code": None})

    @QtCore.Slot(str, str, str)
    def start_shift(self, employee_id: str, route_id: str, subroute_id: str) -> None:
        if not self._validate_core_config():
            return

        payload = {
            "employee_id": employee_id,
            "route_id": route_id,
            "subroute_id": subroute_id or None,
        }

        try:
            response = self._session.post(
                f"{self._config.api_base_url}/device/vehicle/shift/start",
                json=payload,
                timeout=self._config.api_timeout_seconds,
            )
            self.shift_started.emit(self._normalize_response(response, context="Shift start"))
        except requests.RequestException as exc:
            self.shift_started.emit({"ok": False, "detail": str(exc), "status_code": None})

    @QtCore.Slot()
    def end_shift(self) -> None:
        if not self._validate_core_config():
            return

        try:
            response = self._session.post(
                f"{self._config.api_base_url}/device/vehicle/shift/end",
                timeout=self._config.api_timeout_seconds,
            )
            self.shift_ended.emit(self._normalize_response(response, context="Shift end"))
        except requests.RequestException as exc:
            self.shift_ended.emit({"ok": False, "detail": str(exc), "status_code": None})

    @QtCore.Slot()
    def logout_driver(self) -> None:
        if not self._validate_core_config():
            return

        try:
            response = self._session.post(
                f"{self._config.api_base_url}/device/vehicle/shift/logout",
                timeout=self._config.api_timeout_seconds,
            )
            self.driver_logged_out.emit(self._normalize_response(response, context="Driver logout"))
        except requests.RequestException as exc:
            self.driver_logged_out.emit({"ok": False, "detail": str(exc), "status_code": None})

    @QtCore.Slot(dict)
    def submit_telemetry(self, payload: dict) -> None:
        if not self._validate_core_config():
            return

        try:
            response = self._session.post(
                f"{self._config.api_base_url}/device/vehicle/telemetry",
                json=payload,
                timeout=self._config.api_timeout_seconds,
            )
            self.telemetry_result.emit(self._normalize_response(response, context="Telemetry upload"))
        except requests.RequestException as exc:
            self.telemetry_result.emit({"ok": False, "detail": str(exc), "status_code": None})

    def _validate_core_config(self) -> bool:
        if not self._config.api_base_url:
            self.api_error.emit("TRANSIO_API_BASE_URL is not configured")
            return False

        if not self._config.api_key:
            self.api_error.emit("TRANSIO_DEVICE_API_KEY is not configured")
            return False

        return True

    def _normalize_response(self, response: requests.Response, context: str) -> dict:
        if response.status_code >= 400:
            detail = f"{context} failed"
            try:
                payload = response.json()
                detail = payload.get("detail", detail)
            except ValueError:
                pass

            return {
                "ok": False,
                "detail": detail,
                "status_code": response.status_code,
            }

        payload = response.json()
        return {
            "ok": True,
            "payload": payload,
            "status_code": response.status_code,
        }
