import time
import threading
from typing import Any

import nfc
from PySide6 import QtCore


class NfcWorker(QtCore.QObject):
    status_changed = QtCore.Signal(str)
    card_detected = QtCore.Signal(str)
    scan_error = QtCore.Signal(str)

    def __init__(self, nfc_conn_string: str, dedupe_seconds: float = 2.0):
        super().__init__()
        self._nfc_conn_string = nfc_conn_string
        self._dedupe_seconds = dedupe_seconds
        self._stop_requested = False
        self._last_uid = ""
        self._last_seen_monotonic = 0.0
        self._clf = None
        self._clf_lock = threading.Lock()

    @QtCore.Slot()
    def run(self) -> None:
        if not self._nfc_conn_string:
            self.scan_error.emit("TRANSIO_NFC_CONN_STRING is not configured")
            return

        self._stop_requested = False
        try:
            clf = nfc.ContactlessFrontend(self._nfc_conn_string)
            with self._clf_lock:
                self._clf = clf
            self.status_changed.emit(f"NFC scanner connected ({self._nfc_conn_string})")

            while not self._stop_requested:

                def on_connect(tag: Any) -> bool:
                    uid = self._extract_uid(tag)
                    if not uid:
                        self.status_changed.emit("Card detected but UID unavailable")
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
            if not self._stop_requested:
                self.scan_error.emit(f"NFC scanner error: {exc}")
        finally:
            self._close_frontend()
            self.status_changed.emit("NFC scanner stopped")

    @QtCore.Slot()
    def stop(self) -> None:
        self._stop_requested = True
        self._close_frontend()

    def _close_frontend(self) -> None:
        with self._clf_lock:
            clf = self._clf
            self._clf = None

        if clf is not None:
            try:
                clf.close()
            except Exception:
                pass

    def _extract_uid(self, tag: Any) -> str:
        identifier = getattr(tag, "identifier", None)
        if identifier:
            return identifier.hex().upper()
        return ""
