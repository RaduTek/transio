import os
import configparser
from pathlib import Path

from dataclasses import dataclass


@dataclass
class AppConfig:
    api_base_url: str
    api_key: str
    nfc_conn_string: str
    auth_mode: str
    request_timeout_seconds: float

    @classmethod
    def from_env(cls, config_file: str | None = None) -> "AppConfig":
        config_file = config_file or os.getenv("TRANSIO_CONFIG_FILE") or "config.ini"
        config_dict = _load_config_dict(config_file)

        api_base_url = _get_config_value(config_dict, "TRANSIO_API_BASE_URL", "").strip().rstrip("/")
        api_key = _get_config_value(config_dict, "TRANSIO_DEVICE_API_KEY", "").strip()
        nfc_conn_string = (
            _get_config_value(config_dict, "TRANSIO_NFC_CONN_STRING")
            or _get_config_value(config_dict, "TRANSIO_NFC_CONN")
            or _get_config_value(config_dict, "NFC_CLF_CONN")
            or ""
        ).strip()
        auth_mode = _get_config_value(config_dict, "TRANSIO_CARD_AUTH_MODE", "Physical Card").strip() or "Physical Card"

        request_timeout_seconds = _config_float(config_dict, "TRANSIO_API_TIMEOUT_SECONDS", 8.0, minimum=1.0)

        return cls(
            api_base_url=api_base_url,
            api_key=api_key,
            nfc_conn_string=nfc_conn_string,
            auth_mode=auth_mode,
            request_timeout_seconds=request_timeout_seconds,
        )


def _load_config_dict(config_file: str) -> dict:
    """Load configuration from config.ini file and merge with environment variables.
    Environment variables take precedence over file values.
    """
    config_dict = {}

    if Path(config_file).exists():
        parser = configparser.ConfigParser()
        try:
            parser.read(config_file)
            if "transio" in parser:
                config_dict = dict(parser["transio"])
        except Exception:
            pass

    return config_dict


def _get_config_value(config_dict: dict, key: str, fallback: str = "") -> str:
    """Get configuration value from environment variable first, then config file, then fallback."""
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    return config_dict.get(key, fallback)


def _config_float(config_dict: dict, name: str, fallback: float, minimum: float) -> float:
    """Get float configuration value from environment variable first, then config file, then fallback."""
    env_value = os.getenv(name)
    raw = env_value or config_dict.get(name)

    if raw is None:
        return fallback

    try:
        value = float(raw)
    except ValueError:
        return fallback

    return max(value, minimum)
