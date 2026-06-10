import os

from dataclasses import dataclass


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
