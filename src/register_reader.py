"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""
from pymodbus.exceptions import ConnectionException
from pymodbus.exceptions import ModbusIOException
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from time import perf_counter
import time

class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn):
        super(Worker, self).__init__()
        self.fn = fn
        self.signals = WorkerSignals()
        self.is_running = True
    
    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            result = self.fn()
            self.signals.result.emit(result)
            self.signals.finished.emit()
            time.sleep(1)


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
        read_start = perf_counter()
        for key, device in self.table_widgets.items():
            if device.connection_status == True:
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
                        
        read_end = perf_counter()
        print(f"Reading registers :{read_end - read_start}" )
        return result_dict

