import sys
from PyQt5.QtCore import Qt, QThreadPool, QThread, pyqtSlot
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from file_handler import FileHandler
from tableview import TableWidget as tablewidget
from custom_dialogs import EditConnection, AddNewDevice
from register_reader import Observer, DeviceWorker, PollCoordinator
import threading
from notifications import Notification
from constants import (
    STATUS, WIDGET, DISCONNECT, CONNECT,
    SELECT_ACTION_ID, ADD_REGISTERS_ID, REMOVE_REGISTERS_ID,
    CONNECT_ID, HIDE_DEVICE_ID, DELETE_DEVICE_ID, MAX_DEVICES,
    resource_path,
)

from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QAction,
    QVBoxLayout, QDialog, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QToolBar, QCheckBox, QLabel,
    QSizePolicy, QSpacerItem,
)

# Column index that displays the value of read registers.
VALUE_COLUMN = 2


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.scroll_area        = QScrollArea()
        self.main_central_widget = QWidget()
        self.horizontal_box     = QHBoxLayout()

        self.file_handler  = FileHandler()
        self.notification  = Notification()

        self.file_handler.create_path_if_not_exists()
        self.hidden_devices = self.file_handler.get_hidden_devices()

        # Core state
        self.main_widget    = None
        self.observer       = Observer()
        self.threadpool     = QThreadPool()

        # worker_dict: {device_number: (QThread, DeviceWorker)}
        self.worker_dict    = {}

        self.ready_for_reconnect = False
        self.start_signal_count  = 0
        self.finish_signal_count = 0
        self.connected_device_count = 0

        self.poll_mode        = "synchronized"   # or "independent"
        self.global_interval_ms = 1000

        self.coordinator_thread = None   # type: QThread | None
        self.coordinator        = None   # type: PollCoordinator | None

        # UI setup
        self.setWindowTitle("ModConnect")
        self.setGeometry(100, 100, 1100, 1100)

        self._build_toolbar()
        self.initialize_ui()

        self.main_thread         = threading.main_thread()
        self.ready_to_poll_event = threading.Event()
        self.polling_stopped     = threading.Event()
        self.polling_stopped.set()

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------

    def _build_toolbar(self):
        SPACE_AFTER_ADD    = 100  # px between "Add New Device" and "Start Polling"
        SPACE_BETWEEN_POLL = 20   # px between "Start Polling" and "Stop Polling"

        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.toolbar.setMinimumHeight(48)
        self.toolbar.setStyleSheet(
            """
            QToolButton {
                padding-top: 6px;
                padding-bottom: 6px;
            }
            """
        )
        self.addToolBar(self.toolbar)

        add_action = QAction('Add New Device', self)
        add_action.triggered.connect(self.on_new_button_clicked)
        self.toolbar.addAction(add_action)

        gap_after_add = QWidget()
        gap_after_add.setFixedWidth(SPACE_AFTER_ADD)
        self.toolbar.addWidget(gap_after_add)

        start_action = QAction('Start Polling', self)
        start_action.triggered.connect(self.start_ui_refresh)
        self.toolbar.addAction(start_action)

        gap_between_poll = QWidget()
        gap_between_poll.setFixedWidth(SPACE_BETWEEN_POLL)
        self.toolbar.addWidget(gap_between_poll)

        stop_action = QAction('Stop Polling', self)
        stop_action.triggered.connect(self.stop_polling)
        self.toolbar.addAction(stop_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addSeparator()

        self.toolbar.addWidget(QLabel('Hidden Widgets'))
        self.toolbar.addSeparator()

        if self.hidden_devices:
            for device_number in self.hidden_devices:
                self.add_hidden_device_to_toolbar(device_number)
    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize_ui(self):
        self.add_widgets_to_horizontal_layout()
        self.main_central_widget.setLayout(self.horizontal_box)

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.main_central_widget)

        self.setCentralWidget(self.scroll_area)
        self.show()

    # ------------------------------------------------------------------
    # Polling – start
    # ------------------------------------------------------------------

    def start_ui_refresh(self):
        """Called by the toolbar 'Start Polling' button."""
        if self.worker_dict or self.coordinator:
            return  # Already running

        if self.ready_to_poll_event.is_set():
            self.start_tasks()
        else:
            self.notification.set_warning_message(
                "No connected devices",
                "Please connect to a device first",
            )

    def start_tasks(self):
        """
        1. Spawn one QThread per connected device, move a DeviceWorker into it.
        2. In synchronized mode, create a PollCoordinator in its own QThread and
           wire its trigger_workers signal to every worker's do_read slot.
        """
        workers = {}

        for device in self.observer.table_widgets.values():
            if not device.connection_status:
                continue

            thread = QThread()
            worker = DeviceWorker(device)
            worker.moveToThread(thread)

            # Error feedback (optional – connect to UI if desired)
            worker.error.connect(self._on_worker_error)

            thread.start()
            self.worker_dict[device.device_number] = (thread, worker)
            workers[device.device_number] = worker

        if not workers:
            return

        if self.poll_mode == "independent":
            for device_number, (_, worker) in self.worker_dict.items():
                worker.result.connect(self.update_device_table)
                # Independent mode: each worker would need its own QTimer here.
                # Left as an extension point.

        else:
            # ---- SYNCHRONIZED MODE ----
            self.coordinator_thread = QThread()
            self.coordinator = PollCoordinator(workers, self.global_interval_ms)

            # Wire coordinator trigger to every worker's do_read slot.
            # Qt automatically uses a QueuedConnection because they live in
            # different threads, so do_read() executes on each worker's thread.
            for worker in workers.values():
                self.coordinator.trigger_workers.connect(
                    worker.do_read,
                    Qt.QueuedConnection,
                )

            self.coordinator.synchronized_snapshot.connect(
                self.handle_synchronized_snapshot
            )

            self.coordinator.moveToThread(self.coordinator_thread)

            # coordinator.start() runs on the coordinator thread after it starts
            self.coordinator_thread.started.connect(self.coordinator.start)
            self.coordinator_thread.start()

    # ------------------------------------------------------------------
    # Polling – stop
    # ------------------------------------------------------------------

    def stop_polling(self):
        """
        Clean shutdown sequence:
        1. Ask coordinator to stop its QTimer (via signal, thread-safe).
        2. Ask each worker to close its Modbus client (via signal, thread-safe).
        3. Quit and wait for the coordinator thread.
        4. Quit and wait for every worker thread.

        Because no thread runs a blocking loop, quit() is always processed
        immediately, so wait() returns in microseconds.
        """
        # --- 1. Stop coordinator timer ---
        if self.coordinator is not None:
            self.coordinator.request_stop()

        # --- 2. Close Modbus clients ---
        for _, worker in self.worker_dict.values():
            worker.request_stop()

        # --- 3. Tear down coordinator thread ---
        if self.coordinator_thread is not None:
            self.coordinator_thread.quit()
            if not self.coordinator_thread.wait(3000):
                print("Warning: coordinator thread did not finish in time.")
            self.coordinator_thread = None

        self.coordinator = None

        # --- 4. Tear down worker threads ---
        for device_number, (thread, _) in self.worker_dict.items():
            thread.quit()
            if not thread.wait(3000):
                print(f"Warning: worker thread {device_number} did not finish in time.")

        self.worker_dict.clear()

    # ------------------------------------------------------------------
    # Data handlers
    # ------------------------------------------------------------------

    @pyqtSlot(dict, float)
    def handle_synchronized_snapshot(self, data_dict: dict, timestamp: float):
        for device_number, register_data in data_dict.items():
            self._update_table(device_number, register_data)
        print(f"Synchronized sample at {timestamp:.3f}")

    @pyqtSlot(int, list)
    def update_device_table(self, device_number: int, register_data: list):
        """Used by independent poll mode."""
        self._update_table(device_number, register_data)

    def _update_table(self, device_number: int, register_data: list):
        table = self.observer.table_widgets.get(device_number)
        if table is None:
            return
        for row, value in enumerate(register_data):
            table.table_widget.setItem(
                row, VALUE_COLUMN, QTableWidgetItem(str(value))
            )

    @pyqtSlot(int, str)
    def _on_worker_error(self, device_number: int, message: str):
        print(f"Device {device_number} error: {message}")

    # ------------------------------------------------------------------
    # Resume helper
    # ------------------------------------------------------------------

    def resume_polling(self):
        self.stop_polling()
        self.start_ui_refresh()

    # ------------------------------------------------------------------
    # Toolbar / UI callbacks
    # ------------------------------------------------------------------

    def on_checkbox_state_changed(self):
        checkbox = self.sender()
        name = checkbox.text()
        for device in self.observer.table_widgets.values():
            if device.device_name == name:
                self.show_widget(device.device_number)
                checkbox.setParent(None)

    def on_new_button_clicked(self):
        device_count = self.file_handler.get_device_count()
        if device_count >= self.file_handler.max_devices:
            self.notification.set_warning_message(
                f"{self.file_handler.max_devices} maximum devices.",
                "You have reached the maximum number of devices",
            )
            return
        dialog = AddNewDevice()
        if dialog.exec_() == QDialog.Accepted:
            new_device = dialog.device_number
            if new_device is not None:
                self.add_single_widget(new_device)

    def on_edit_button_clicked(self, index):
        edit_connection = EditConnection(index)
        if edit_connection.exec_() == QDialog.Accepted:
            w = self.observer.table_widgets[index]
            w.update_method_label()
            w.update_device_name()
            w.set_active_connection()
            w.on_connection_settings_updated()

    def on_drop_down_menu_selected(self, device_number, position):
        current_table = self.observer.table_widgets[device_number]

        if position == ADD_REGISTERS_ID:
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)
            current_table.show_register_dialog()
            current_table.list_of_registers = self.file_handler.get_registers_to_read(device_number)

        elif position == REMOVE_REGISTERS_ID:
            current_table.delete_registers()

        elif position == CONNECT_ID:
            current_text = current_table.action_menu.currentText()
            if current_text == CONNECT:
                result = current_table.connect_to_device()
                if result:
                    if self.ready_for_reconnect:
                        self.ready_for_reconnect = False
                        self.resume_polling()
                    else:
                        self.ready_to_poll_event.set()
                else:
                    print(f"Failed to connect to device {device_number}.")
            elif current_text == DISCONNECT:
                current_table.disconnect_from_device()
                if not self.check_for_connected_devices():
                    self.ready_to_poll_event.clear()
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)

        elif position == HIDE_DEVICE_ID:
            if self.observer.table_widgets[device_number].connection_status:
                self.notification.set_warning_message(
                    "Device is connected!",
                    "Please disconnect before hiding the device.",
                )
                return
            self.hide_widget(device_number)
            self.file_handler.update_hidden_status(device_number, True)
            self.add_hidden_device_to_toolbar(device_number)

        elif position == DELETE_DEVICE_ID:
            if self.observer.table_widgets[device_number].connection_status:
                self.notification.set_warning_message(
                    "Device is connected!",
                    "Please disconnect before deleting the device.",
                )
                return
            self.delete_widget(device_number)

    # ------------------------------------------------------------------
    # Widget layout helpers
    # ------------------------------------------------------------------

    def add_widgets_to_horizontal_layout(self):
        self.observer.table_widgets.clear()
        device_tags = self.file_handler.get_int_device_tags()
        if device_tags:
            beg_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(beg_spacer)
            for device_tag in device_tags:
                widget = tablewidget(device_tag)
                widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
                widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
                self.observer.add_table_widget(device_tag, widget)
                if not widget.hidden_status:
                    self.horizontal_box.addWidget(widget)
            end_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(end_spacer)
            return True
        return None

    def add_single_widget(self, new_device_number):
        count = self.horizontal_box.count()
        widget = tablewidget(new_device_number)
        widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
        widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
        self.observer.add_table_widget(new_device_number, widget)

        if count == 0:
            beg = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            end = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(beg)
            self.horizontal_box.insertWidget(1, widget)
            self.horizontal_box.addSpacerItem(end)
        else:
            insert_at = count - 1  # before the trailing spacer
            self.horizontal_box.insertWidget(insert_at, widget)

    def delete_widget(self, device_number):
        self.observer.table_widgets[device_number].setParent(None)
        self.observer.remove_table_widget(device_number)
        self.file_handler.delete_device(device_number)

    def hide_widget(self, device_number):
        self.hidden_devices.append(device_number)
        self.observer.table_widgets[device_number].hide()
        self.observer.table_widgets[device_number].hidden_status = True

    def show_widget(self, device_number):
        self.add_single_widget(device_number)
        self.observer.table_widgets[device_number].hidden_status = False
        self.file_handler.update_hidden_status(device_number, False)

    def add_hidden_device_to_toolbar(self, device_number):
        cb = QCheckBox(self.observer.table_widgets[device_number].device_name)
        cb.setChecked(True)
        cb.stateChanged.connect(self.on_checkbox_state_changed)
        self.toolbar.addWidget(cb)

    def check_for_connected_devices(self):
        return any(d.connection_status for d in self.observer.table_widgets.values())

    # ------------------------------------------------------------------
    # Misc counts (kept for compatibility)
    # ------------------------------------------------------------------

    def count_starts(self):
        self.start_signal_count += 1

    def count_finish(self):
        self.finish_signal_count += 1


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()