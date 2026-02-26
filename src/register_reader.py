"""
This module implements the observer pattern for reading and updating the register table widget.

Synchronization is handled entirely through Qt signals/slots and QTimer no busy-wait loops,
no threading.Event, no time.sleep() so QThread.quit() always works cleanly.
"""

from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal, pyqtSlot
from pymodbus.exceptions import ConnectionException, ModbusIOException
import time


# ---------------------------------------------------------------------------
# DeviceWorker
# ---------------------------------------------------------------------------

class DeviceWorker(QObject):
    """
    Lives in its own QThread and performs a single Modbus read each time
    do_read() is invoked via a queued signal connection.

    Because there is no blocking run() loop the thread keeps a normal Qt
    event loop, so thread.quit() always succeeds immediately.
    """

    result         = pyqtSignal(int, list)   # device_number, data
    finished_cycle = pyqtSignal(int)         # device_number
    error          = pyqtSignal(int, str)    # device_number, message

    # Emitted internally so stop() can be called safely from any thread
    _stop_requested = pyqtSignal()

    def __init__(self, device):
        super().__init__()
        self.device = device
        self._stop_requested.connect(self._on_stop_requested, Qt.QueuedConnection)

    # ------------------------------------------------------------------
    # Public API (thread-safe)
    # ------------------------------------------------------------------

    def request_stop(self):
        """Call from any thread; schedules client close on the worker thread."""
        self._stop_requested.emit()

    # ------------------------------------------------------------------
    # Slots – executed on the worker thread
    # ------------------------------------------------------------------

    @pyqtSlot()
    def do_read(self):
        """Triggered by PollCoordinator.trigger_workers signal."""
        if not self.device.connection_status:
            self.finished_cycle.emit(self.device.device_number)
            return

        try:
            data = self.device.read_registers()
            self.result.emit(self.device.device_number, data)

        except ModbusIOException:
            self.error.emit(self.device.device_number, "Modbus IO Exception")

        except ConnectionException:
            self.device.set_connection_status(False)
            self.error.emit(self.device.device_number, "Connection lost")

        finally:
            self.finished_cycle.emit(self.device.device_number)

    @pyqtSlot()
    def _on_stop_requested(self):
        """Closes the Modbus client on the worker thread."""
        try:
            self.device.client.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# PollCoordinator
# ---------------------------------------------------------------------------

class PollCoordinator(QObject):
    """
    Lives in its own QThread and orchestrates synchronized polling of all
    DeviceWorkers using a single-shot QTimer.

    Cycle flow
    ----------
    1. QTimer fires  → _start_cycle() → emits trigger_workers
    2. Each DeviceWorker.do_read() runs (in worker threads)
    3. Each worker emits finished_cycle → _on_worker_finished()
    4. When all workers have reported in → emit synchronized_snapshot
                                         → restart QTimer for next cycle

    No blocking code, no time.sleep(), no threading primitives.
    """

    # Signal emitted once per cycle when all workers have responded
    synchronized_snapshot = pyqtSignal(dict, float)   # data_dict, timestamp

    # Connected to every DeviceWorker.do_read slot (queued, cross-thread)
    trigger_workers = pyqtSignal()

    # Internal stop signal so stop() is safe to call from any thread
    _stop_requested = pyqtSignal()

    def __init__(self, workers: dict, interval_ms: int):
        """
        Parameters
        ----------
        workers      : {device_number: DeviceWorker}
        interval_ms  : target poll cycle time in milliseconds
        """
        super().__init__()

        self.workers      = workers
        self.interval_ms  = interval_ms

        self._results       = {}
        self._finished_count = 0
        self._total_workers  = len(workers)
        self._cycle_start    = 0.0

        # Single-shot timer: restarted at the end of each cycle
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._start_cycle)

        # Wire stop signal so it's handled on the coordinator's own thread
        self._stop_requested.connect(self._on_stop_requested, Qt.QueuedConnection)

        # Collect results and track completion
        for worker in self.workers.values():
            worker.result.connect(self._collect_result)
            worker.finished_cycle.connect(self._on_worker_finished)

    # ------------------------------------------------------------------
    # Public API (thread-safe)
    # ------------------------------------------------------------------

    def request_stop(self):
        """Call from any thread to stop the timer cleanly."""
        self._stop_requested.emit()

    # ------------------------------------------------------------------
    # Slots – executed on the coordinator thread
    # ------------------------------------------------------------------

    @pyqtSlot()
    def start(self):
        """Connected to coordinator_thread.started — kicks off the first cycle."""
        self._start_cycle()

    @pyqtSlot()
    def _on_stop_requested(self):
        self._timer.stop()

    @pyqtSlot()
    def _start_cycle(self):
        self._results.clear()
        self._finished_count = 0
        self._cycle_start = time.perf_counter()
        self.trigger_workers.emit()

    @pyqtSlot(int, list)
    def _collect_result(self, device_number: int, data: list):
        self._results[device_number] = data

    @pyqtSlot(int)
    def _on_worker_finished(self, device_number: int):
        self._finished_count += 1

        if self._finished_count >= self._total_workers:
            # All workers done for this cycle
            timestamp = time.time()
            self.synchronized_snapshot.emit(self._results.copy(), timestamp)

            elapsed_ms = (time.perf_counter() - self._cycle_start) * 1000
            next_ms    = max(0, int(self.interval_ms - elapsed_ms))
            self._timer.start(next_ms)


# ---------------------------------------------------------------------------
# Observer  (unchanged from original)
# ---------------------------------------------------------------------------

class Observer:
    def __init__(self):
        self.table_widgets   = {}
        self.connected_devices = []

    def add_table_widget(self, index, widget):
        if index not in self.table_widgets:
            self.table_widgets[index] = widget

    def remove_table_widget(self, index):
        del self.table_widgets[index]

    def read_all_registers(self):
        result_dict = {}
        for key, device in self.table_widgets.items():
            if device.connection_status and not device.hidden_status:
                try:
                    response = device.read_registers()
                    if response:
                        result_dict[key] = device.read_registers()
                    else:
                        print("No response after reading registers")
                except ModbusIOException:
                    print("Failed to perform Modbus operation due to IO exception.")
                except ConnectionException:
                    print("Failed to connect to Modbus device.")
                    device.set_connection_status(False)
        return result_dict