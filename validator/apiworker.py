import requests

from PySide6 import QtCore

from config import AppConfig


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
