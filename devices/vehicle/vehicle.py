import sys

from PySide6 import QtCore, QtGui, QtWidgets

from apiworker import ApiClientWorker
from config import AppConfig
from gpsworker import GpsWorker
from nfcworker import NfcWorker


class VehicleObcApp(QtWidgets.QWidget):
    request_state = QtCore.Signal()
    request_routes = QtCore.Signal()
    request_subroutes = QtCore.Signal(str)
    request_driver_login = QtCore.Signal(str)
    request_shift_start = QtCore.Signal(str, str, str)
    request_shift_end = QtCore.Signal()
    request_driver_logout = QtCore.Signal()
    request_telemetry = QtCore.Signal(dict)

    def __init__(self, config: AppConfig):
        super().__init__()
        self._config = config

        self._driver: dict | None = None
        self._active_shift: dict | None = None
        self._route_map: dict[str, dict] = {}
        self._subroute_map: dict[str, dict] = {}

        self.setWindowTitle("Transio Vehicle OBC")
        self.setFixedSize(800, 600)
        self._build_ui()

        self._setup_api_worker()
        self._setup_nfc_worker()
        self._setup_gps_worker()

        self._state_timer = QtCore.QTimer(self)
        self._state_timer.setInterval(30000)
        self._state_timer.timeout.connect(self._request_state)

        self._request_routes()
        self._request_state()
        self._state_timer.start()

        self._start_nfc()
        self._start_gps()

    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        title = QtWidgets.QLabel("Vehicle On-Board Controller")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)

        self._status_device = QtWidgets.QLabel("Device: -")
        self._status_vehicle = QtWidgets.QLabel("Vehicle: -")
        self._status_driver = QtWidgets.QLabel("Driver: awaiting badge")
        self._status_shift = QtWidgets.QLabel("Shift: inactive")
        self._status_nfc = QtWidgets.QLabel("NFC: idle")
        self._status_gps = QtWidgets.QLabel("GPS: idle")
        self._status_telemetry = QtWidgets.QLabel("Telemetry: idle")

        status_font = QtGui.QFont()
        status_font.setPointSize(14)

        for label in (
            self._status_device,
            self._status_vehicle,
            self._status_driver,
            self._status_shift,
            self._status_nfc,
            self._status_gps,
            self._status_telemetry,
        ):
            label.setFont(status_font)

        self._route_combo = QtWidgets.QComboBox()
        self._route_combo.setMinimumHeight(52)
        self._route_combo.currentIndexChanged.connect(self._on_route_changed)

        self._subroute_combo = QtWidgets.QComboBox()
        self._subroute_combo.setMinimumHeight(52)

        self._start_shift_btn = QtWidgets.QPushButton("Start Shift")
        self._end_shift_btn = QtWidgets.QPushButton("End Shift")
        self._logout_btn = QtWidgets.QPushButton("Logout Driver")
        self._refresh_btn = QtWidgets.QPushButton("Refresh")

        for button in (
            self._start_shift_btn,
            self._end_shift_btn,
            self._logout_btn,
            self._refresh_btn,
        ):
            button.setMinimumHeight(56)
            btn_font = button.font()
            btn_font.setPointSize(16)
            btn_font.setBold(True)
            button.setFont(btn_font)

        self._start_shift_btn.clicked.connect(self._on_start_shift_clicked)
        self._end_shift_btn.clicked.connect(self._on_end_shift_clicked)
        self._logout_btn.clicked.connect(self._on_logout_clicked)
        self._refresh_btn.clicked.connect(self._request_state)

        route_form = QtWidgets.QFormLayout()
        route_form.addRow("Route", self._route_combo)
        route_form.addRow("Subroute", self._subroute_combo)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(self._start_shift_btn)
        controls.addWidget(self._end_shift_btn)
        controls.addWidget(self._logout_btn)
        controls.addWidget(self._refresh_btn)

        self._log_box = QtWidgets.QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setPlaceholderText("Operational events will appear here")

        root.addWidget(title)
        root.addWidget(self._status_device)
        root.addWidget(self._status_vehicle)
        root.addWidget(self._status_driver)
        root.addWidget(self._status_shift)
        root.addWidget(self._status_nfc)
        root.addWidget(self._status_gps)
        root.addWidget(self._status_telemetry)
        root.addLayout(route_form)
        root.addLayout(controls)
        root.addWidget(self._log_box, 1)

        self._apply_style()
        self._refresh_ui_state()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f6f8fa;
                color: #1b2a41;
                font-family: "Noto Sans";
            }
            QComboBox, QTextEdit {
                background-color: #ffffff;
                border: 2px solid #9fb3c8;
                border-radius: 8px;
                padding: 6px;
                font-size: 15px;
            }
            QPushButton {
                background-color: #0e7490;
                color: white;
                border-radius: 10px;
                padding: 8px 12px;
            }
            QPushButton:disabled {
                background-color: #9aa7b2;
            }
            QPushButton:hover:!disabled {
                background-color: #155e75;
            }
            """
        )

    def _setup_api_worker(self) -> None:
        self._api_thread = QtCore.QThread(self)
        self._api_worker = ApiClientWorker(self._config)
        self._api_worker.moveToThread(self._api_thread)
        self._api_thread.start()

        self.request_state.connect(self._api_worker.fetch_state)
        self.request_routes.connect(self._api_worker.fetch_routes)
        self.request_subroutes.connect(self._api_worker.fetch_subroutes)
        self.request_driver_login.connect(self._api_worker.login_driver)
        self.request_shift_start.connect(self._api_worker.start_shift)
        self.request_shift_end.connect(self._api_worker.end_shift)
        self.request_driver_logout.connect(self._api_worker.logout_driver)
        self.request_telemetry.connect(self._api_worker.submit_telemetry)

        self._api_worker.state_loaded.connect(self._on_state_loaded)
        self._api_worker.routes_loaded.connect(self._on_routes_loaded)
        self._api_worker.subroutes_loaded.connect(self._on_subroutes_loaded)
        self._api_worker.driver_login_loaded.connect(self._on_driver_login_loaded)
        self._api_worker.shift_started.connect(self._on_shift_started)
        self._api_worker.shift_ended.connect(self._on_shift_ended)
        self._api_worker.driver_logged_out.connect(self._on_driver_logged_out)
        self._api_worker.telemetry_result.connect(self._on_telemetry_result)
        self._api_worker.api_error.connect(self._append_log)

    def _setup_nfc_worker(self) -> None:
        self._nfc_thread: QtCore.QThread | None = None
        self._nfc_worker: NfcWorker | None = None

    def _setup_gps_worker(self) -> None:
        self._gps_thread: QtCore.QThread | None = None
        self._gps_worker: GpsWorker | None = None

    @QtCore.Slot()
    def _request_state(self) -> None:
        self.request_state.emit()

    @QtCore.Slot()
    def _request_routes(self) -> None:
        self.request_routes.emit()

    @QtCore.Slot()
    def _start_nfc(self) -> None:
        if self._nfc_thread is not None:
            return

        self._nfc_thread = QtCore.QThread(self)
        self._nfc_worker = NfcWorker(self._config.nfc_conn_string)
        self._nfc_worker.moveToThread(self._nfc_thread)

        self._nfc_thread.started.connect(self._nfc_worker.run)
        self._nfc_worker.status_changed.connect(self._on_nfc_status)
        self._nfc_worker.scan_error.connect(self._append_log)
        self._nfc_worker.card_detected.connect(self._on_card_detected)
        self._nfc_thread.finished.connect(self._on_nfc_stopped)
        self._nfc_thread.start()

    @QtCore.Slot()
    def _start_gps(self) -> None:
        if self._gps_thread is not None:
            return

        self._gps_thread = QtCore.QThread(self)
        self._gps_worker = GpsWorker(
            device_path=self._config.gps_device,
            fast_interval_seconds=self._config.telemetry_fast_interval_seconds,
            idle_interval_seconds=self._config.telemetry_idle_interval_seconds,
            idle_after_seconds=self._config.telemetry_idle_after_seconds,
            movement_speed_threshold_kmph=self._config.movement_speed_threshold_kmph,
        )
        self._gps_worker.moveToThread(self._gps_thread)

        self._gps_thread.started.connect(self._gps_worker.run)
        self._gps_worker.status_changed.connect(self._on_gps_status)
        self._gps_worker.gps_error.connect(self._append_log)
        self._gps_worker.telemetry_skipped.connect(self._on_telemetry_skipped)
        self._gps_worker.telemetry_ready.connect(self.request_telemetry.emit)
        self._gps_thread.finished.connect(self._on_gps_stopped)
        self._gps_thread.start()

    @QtCore.Slot(str)
    def _on_card_detected(self, uid: str) -> None:
        self._append_log(f"Driver badge scanned: {uid}")
        self.request_driver_login.emit(uid)

    @QtCore.Slot(dict)
    def _on_state_loaded(self, payload: dict) -> None:
        device = payload.get("device") or {}
        vehicle = payload.get("vehicle") or {}
        shift = payload.get("transit_shift")
        driver = payload.get("driver")

        self._status_device.setText(f"Device: {device.get('code', '-')}")
        self._status_vehicle.setText(f"Vehicle: {vehicle.get('code', '-') if vehicle else '-'}")

        self._active_shift = shift
        self._driver = driver

        if driver:
            self._status_driver.setText(
                f"Driver: {driver.get('first_name', '')} {driver.get('last_name', '')}".strip()
            )
        else:
            self._status_driver.setText("Driver: awaiting badge")

        if shift:
            route_id = shift.get("route_id", "-")
            self._status_shift.setText(f"Shift: active ({route_id})")
            self._append_log("Active shift loaded from server state")
        else:
            self._status_shift.setText("Shift: inactive")

        self._refresh_ui_state()

    @QtCore.Slot(list)
    def _on_routes_loaded(self, routes: list) -> None:
        self._route_map = {route["id"]: route for route in routes if "id" in route}

        self._route_combo.blockSignals(True)
        self._route_combo.clear()
        self._route_combo.addItem("Select route", "")

        for route in routes:
            route_id = route.get("id", "")
            label = route.get("name") or route.get("code") or route_id
            self._route_combo.addItem(label, route_id)

        self._route_combo.blockSignals(False)

    @QtCore.Slot(str, list)
    def _on_subroutes_loaded(self, route_id: str, subroutes: list) -> None:
        current_route_id = self._route_combo.currentData() or ""
        if current_route_id != route_id:
            return

        self._subroute_map = {subroute.get("id", ""): subroute for subroute in subroutes if subroute.get("id")}

        self._subroute_combo.clear()
        self._subroute_combo.addItem("No subroute", "")

        for subroute in subroutes:
            subroute_id = subroute.get("id", "")
            label = subroute.get("name") or subroute.get("code") or subroute_id
            self._subroute_combo.addItem(label, subroute_id)

    @QtCore.Slot(dict)
    def _on_driver_login_loaded(self, result: dict) -> None:
        if not result.get("ok"):
            self._append_log(f"Driver login failed: {result.get('detail', 'Unknown error')}")
            return

        payload = result.get("payload") or {}
        employee = payload.get("employee")
        if not employee:
            self._append_log("Driver login failed: employee payload missing")
            return

        self._driver = employee
        self._status_driver.setText(
            f"Driver: {employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        )
        self._append_log("Driver authenticated")
        self._refresh_ui_state()

    @QtCore.Slot(dict)
    def _on_shift_started(self, result: dict) -> None:
        if not result.get("ok"):
            self._append_log(f"Shift start failed: {result.get('detail', 'Unknown error')}")
            return

        payload = result.get("payload") or {}
        shift = payload.get("transit_shift")
        self._active_shift = shift
        self._status_shift.setText(f"Shift: active ({shift.get('route_id', '-') if shift else '-'})")
        self._append_log("Shift started")
        self._refresh_ui_state()

    @QtCore.Slot(dict)
    def _on_shift_ended(self, result: dict) -> None:
        if not result.get("ok"):
            self._append_log(f"Shift end failed: {result.get('detail', 'Unknown error')}")
            return

        self._active_shift = None
        self._status_shift.setText("Shift: inactive")
        self._append_log("Shift ended")
        self._refresh_ui_state()

    @QtCore.Slot(dict)
    def _on_driver_logged_out(self, result: dict) -> None:
        if not result.get("ok"):
            self._append_log(f"Logout failed: {result.get('detail', 'Unknown error')}")
            return

        payload = result.get("payload") or {}
        if payload.get("ended_shift"):
            self._append_log("Logout auto-ended active shift")

        self._driver = None
        self._active_shift = None
        self._status_driver.setText("Driver: awaiting badge")
        self._status_shift.setText("Shift: inactive")
        self._append_log("Driver logged out")
        self._refresh_ui_state()

    @QtCore.Slot(dict)
    def _on_telemetry_result(self, result: dict) -> None:
        if result.get("ok"):
            self._status_telemetry.setText("Telemetry: uploaded")
            return

        detail = result.get("detail", "Unknown error")
        self._status_telemetry.setText("Telemetry: failed")
        self._append_log(f"Telemetry upload failed: {detail}")

    @QtCore.Slot(str)
    def _on_nfc_status(self, status: str) -> None:
        self._status_nfc.setText(f"NFC: {status}")

    @QtCore.Slot(str)
    def _on_gps_status(self, status: str) -> None:
        self._status_gps.setText(f"GPS: {status}")

    @QtCore.Slot(str)
    def _on_telemetry_skipped(self, reason: str) -> None:
        self._status_telemetry.setText("Telemetry: waiting for GPS fix")
        self._append_log(reason)

    @QtCore.Slot(int)
    def _on_route_changed(self, index: int) -> None:
        del index
        route_id = self._route_combo.currentData() or ""
        self.request_subroutes.emit(route_id)

    @QtCore.Slot()
    def _on_start_shift_clicked(self) -> None:
        if not self._driver:
            self._append_log("Scan driver badge before starting shift")
            return

        route_id = self._route_combo.currentData() or ""
        if not route_id:
            self._append_log("Select a route before starting shift")
            return

        subroute_id = self._subroute_combo.currentData() or ""
        employee_id = self._driver.get("id", "")
        self.request_shift_start.emit(employee_id, route_id, subroute_id)

    @QtCore.Slot()
    def _on_end_shift_clicked(self) -> None:
        self.request_shift_end.emit()

    @QtCore.Slot()
    def _on_logout_clicked(self) -> None:
        self.request_driver_logout.emit()

    @QtCore.Slot()
    def _on_nfc_stopped(self) -> None:
        self._nfc_worker = None
        self._nfc_thread = None

    @QtCore.Slot()
    def _on_gps_stopped(self) -> None:
        self._gps_worker = None
        self._gps_thread = None

    def _refresh_ui_state(self) -> None:
        can_start = self._driver is not None and self._active_shift is None
        can_end = self._active_shift is not None
        can_logout = self._driver is not None

        self._start_shift_btn.setEnabled(can_start)
        self._end_shift_btn.setEnabled(can_end)
        self._logout_btn.setEnabled(can_logout)
        self._route_combo.setEnabled(can_start)
        self._subroute_combo.setEnabled(can_start)

    def _append_log(self, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        self._log_box.append(f"[{timestamp}] {message}")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._state_timer.stop()

        if self._nfc_worker is not None:
            QtCore.QMetaObject.invokeMethod(self._nfc_worker, "stop", QtCore.Qt.QueuedConnection)
        if self._nfc_thread is not None:
            self._nfc_thread.quit()
            self._nfc_thread.wait(2000)

        if self._gps_worker is not None:
            QtCore.QMetaObject.invokeMethod(self._gps_worker, "stop", QtCore.Qt.QueuedConnection)
        if self._gps_thread is not None:
            self._gps_thread.quit()
            self._gps_thread.wait(2000)

        self._api_thread.quit()
        self._api_thread.wait(2000)

        super().closeEvent(event)


def main() -> int:
    config = AppConfig.from_env()

    app = QtWidgets.QApplication(sys.argv)
    window = VehicleObcApp(config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
