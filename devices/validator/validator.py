import sys

from PySide6 import QtCore, QtGui, QtWidgets

from config import AppConfig
from apiworker import ApiClientWorker
from nfcworker import NfcWorker


class ValidatorApp(QtWidgets.QWidget):
    request_state = QtCore.Signal()
    request_route = QtCore.Signal(str)
    request_validate = QtCore.Signal(str)

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config
        self._route_name_cache: dict[str, str] = {}
        
        # State tracking
        self._shift_active = False
        self._scanner_available = False
        self._current_route_name = "-"
        self._last_validation_success = False

        self.setWindowTitle("Transio Ticket Validator")
        self.setFixedSize(480, 440)
        self.move(0, 0)

        self._build_ui()
        self._setup_api_worker()
        self._setup_nfc_worker()

        self._state_timer = QtCore.QTimer(self)
        self._state_timer.setInterval(10000)
        self._state_timer.timeout.connect(self._request_state)
        
        self._time_timer = QtCore.QTimer(self)
        self._time_timer.setInterval(1000)
        self._time_timer.timeout.connect(self._update_time)
        self._time_timer.start()

        self._request_state()
        self._state_timer.start()
        self._start_scanning()

    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(12)

        # Top section: Title, time, and route
        top_layout = QtWidgets.QVBoxLayout()
        top_layout.setSpacing(8)
        
        title = QtWidgets.QLabel("Transio Ticket Validator")
        title_font = QtGui.QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(QtCore.Qt.AlignCenter)
        
        info_layout = QtWidgets.QHBoxLayout()
        info_layout.setSpacing(10)
        self._time_label = QtWidgets.QLabel("00:00:00")
        time_font = QtGui.QFont()
        time_font.setPointSize(11)
        self._time_label.setFont(time_font)
        
        self._route_label = QtWidgets.QLabel("Route: -")
        self._route_label.setFont(time_font)
        
        info_layout.addWidget(self._time_label)
        info_layout.addStretch()
        info_layout.addWidget(self._route_label)
        
        top_layout.addWidget(title)
        top_layout.addLayout(info_layout)

        # Middle section: Status display
        middle_layout = QtWidgets.QVBoxLayout()
        middle_layout.setSpacing(10)
        middle_layout.addStretch()
        
        self._status_label = QtWidgets.QLabel("Initializing...")
        status_font = QtGui.QFont()
        status_font.setPointSize(32)
        status_font.setBold(True)
        self._status_label.setFont(status_font)
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet("color: black;")
        
        self._details_label = QtWidgets.QLabel("")
        details_font = QtGui.QFont()
        details_font.setPointSize(11)
        self._details_label.setFont(details_font)
        self._details_label.setAlignment(QtCore.Qt.AlignCenter)
        self._details_label.setWordWrap(True)
        
        middle_layout.addWidget(self._status_label)
        middle_layout.addWidget(self._details_label, alignment=QtCore.Qt.AlignTop)
        middle_layout.addStretch()

        # Combine sections
        root.addLayout(top_layout)
        root.addLayout(middle_layout, 1)
        
        # Initialize status
        self._update_status_display()

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

    def _set_status(self, message: str, color: str, details: str = "") -> None:
        """Update status display with message, color, and optional details."""
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {color};")
        self._details_label.setText(details)
    
    def _update_time(self) -> None:
        """Update time label with current time."""
        current_time = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        self._time_label.setText(current_time)
    
    def _update_status_display(self) -> None:
        """Update status display based on current state."""
        if not self._shift_active:
            self._set_status("Validator is unavailable", "red")
        elif not self._scanner_available:
            self._set_status("Scanner is out of order", "red")
        else:
            self._set_status("Please scan your card", "black")

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
        self._scanner_available = True
        self._update_status_display()

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
        self._scanner_available = False
        self._update_status_display()

    @QtCore.Slot(str)
    def _on_scanner_status(self, message: str) -> None:
        # Scanner status tracking for future use if needed
        pass

    @QtCore.Slot(str)
    def _on_scanner_error(self, message: str) -> None:
        self._scanner_available = False
        self._update_status_display()
        self._stop_scanning()

    @QtCore.Slot(str)
    def _on_card_detected(self, uid: str) -> None:
        self._set_status("Validating...", "black")
        self.request_validate.emit(uid)

    @QtCore.Slot()
    def _request_state(self) -> None:
        self.request_state.emit()

    @QtCore.Slot(dict)
    def _on_state_loaded(self, payload: dict) -> None:
        shift = payload.get("transit_shift") or {}

        if shift:
            self._shift_active = True
            route_id = shift.get("route_id")

            if route_id:
                route_name = self._route_name_cache.get(route_id)
                if route_name:
                    self._current_route_name = route_name
                    self._route_label.setText(f"Route: {route_name}")
                else:
                    self._current_route_name = route_id
                    self._route_label.setText(f"Route: {route_id}")
                    self.request_route.emit(route_id)
            else:
                self._current_route_name = "-"
                self._route_label.setText("Route: -")
        else:
            self._shift_active = False
            self._current_route_name = "-"
            self._route_label.setText("Route: -")
        
        self._update_status_display()

    @QtCore.Slot(str, str)
    def _on_route_loaded(self, route_id: str, route_name: str) -> None:
        self._route_name_cache[route_id] = route_name
        self._current_route_name = route_name
        self._route_label.setText(f"Route: {route_name}")

    @QtCore.Slot(dict)
    def _on_validation_loaded(self, result: dict) -> None:
        if result.get("ok"):
            self._last_validation_success = True
            payload = result.get("payload") or {}
            ticket = payload.get("ticket") or {}
            ticket_type = payload.get("ticket_type") or {}
            
            details = (
                f"Ticket {ticket.get('id', '-')[:8]} | "
                f"Type: {ticket_type.get('name', ticket_type.get('code', '-'))}"
            )
            self._set_status("Ticket/Pass validated successfully", "green", details)
            
            # Reset to ready after 3 seconds
            QtCore.QTimer.singleShot(3000, self._update_status_display)
        else:
            self._last_validation_success = False
            uid = result.get("uid", "-")
            detail = result.get("detail", "Validation failed")
            status = result.get("status_code")
            
            if status is not None:
                error_msg = f"Validation failed ({status})"
            else:
                error_msg = "Validation failed"
            
            self._set_status(error_msg, "red", detail)
            
            # Reset to ready after 3 seconds
            QtCore.QTimer.singleShot(3000, self._update_status_display)

    @QtCore.Slot(str)
    def _on_api_error(self, message: str) -> None:
        self._set_status("API Error", "red", message)
        
        # Reset to previous state after 3 seconds
        QtCore.QTimer.singleShot(3000, self._update_status_display)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._state_timer.stop()
        self._time_timer.stop()

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
