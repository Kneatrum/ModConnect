"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from pymodbus.exceptions import ConnectionException, ModbusIOException
import threading
import time
# import perf_counter

class WorkerSignals(QObject):
    start = pyqtSignal()
    finished = pyqtSignal()
    result = pyqtSignal(object)

class DeviceWorker(QObject):

    result = pyqtSignal(int, list)          # device_number, data
    finished_cycle = pyqtSignal(int)       # device_number
    error = pyqtSignal(int, str)

    def __init__(self, device):
        super().__init__()
        self.device = device
        self._running = True
        self._trigger_event = threading.Event()

    def stop(self):
        self._running = False
        self._trigger_event.set()
        try:
            self.device.client.close()
        except:
            pass

    def trigger(self):
        self._trigger_event.set()

    def run(self):
        while self._running:

            self._trigger_event.wait()
            self._trigger_event.clear()

            if not self._running:
                break

            if not self.device.connection_status:
                continue

            try:
                data = self.device.read_registers()
                self.result.emit(self.device.device_number, data)

            except ModbusIOException:
                self.error.emit(self.device.device_number, "Modbus IO Exception")

            except ConnectionException:
                self.device.set_connection_status(False)
                self.error.emit(self.device.device_number, "Connection lost")

            self.finished_cycle.emit(self.device.device_number)


class PollCoordinator(QObject):

    synchronized_snapshot = pyqtSignal(dict, float)  # data, timestamp

    def __init__(self, workers, interval_ms):
        super().__init__()
        self.workers = workers
        self.interval = interval_ms / 1000.0
        self._running = True
        self._results = {}
        self._finished_count = 0

        for worker in self.workers.values():
            worker.result.connect(self._collect_result)
            worker.finished_cycle.connect(self._worker_finished)

    def stop(self):
        self._running = False

    def _collect_result(self, device_number, data):
        self._results[device_number] = data

    def _worker_finished(self, device_number):
        self._finished_count += 1

    def run(self):

        while self._running:

            cycle_start = time.perf_counter()

            self._results.clear()
            self._finished_count = 0

            # Trigger all workers
            for worker in self.workers.values():
                worker.trigger()

            # Wait for all workers
            while self._finished_count < len(self.workers):
                time.sleep(0.001)

            timestamp = time.time()

            self.synchronized_snapshot.emit(self._results.copy(), timestamp)

            elapsed = time.perf_counter() - cycle_start
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)


class Observer:
    def __init__(self):
        self.table_widgets ={}
        self.connected_devices = []


    def add_table_widget(self, index, widget):
        if widget not in self.table_widgets:
            self.table_widgets[index] = widget

    def remove_table_widget(self, index):
        del self.table_widgets[index]

    def read_all_registers(self):
        # Reading register data.
        result_dict = {}
        # read_start = perf_counter()
        for key, device in self.table_widgets.items():
            if device.connection_status == True and device.hidden_status == False:
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
                        
        # read_end = perf_counter()
        # print(f"Reading registers :{read_end - read_start}" )
        return result_dict

