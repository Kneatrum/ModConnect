"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""
from pymodbus.exceptions import ConnectionException
from pymodbus.exceptions import ModbusIOException
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from time import perf_counter
import time
from constants import CONNECT_ID, CONNECT, STATUS, WIDGET

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

    
    def add_table_widget(self, index, status, widget):
        if widget not in self.table_widgets:
            temp_dict = {}
            temp_dict[STATUS] = status
            temp_dict[WIDGET] = widget
            self.table_widgets[index] = temp_dict

    def remove_table_widget(self, index):
        del self.table_widgets[index]

    def read_all_registers(self):
        # Reading register data.
        result_dict = {}
        read_start = perf_counter()
        for key in self.table_widgets:
            if self.table_widgets[key][STATUS] == True:
                try:
                    response = self.table_widgets[key][WIDGET].read_registers()
                    if response:
                        result_dict[key] = self.table_widgets[key][WIDGET].read_registers()
                    else:
                        print("No response after reading registers")
                except ModbusIOException:
                    print("Failed to perform Modbus operation due to IO exception.")
                except ConnectionException:
                    print("Failed to connect to Modbus device.")
                    self.table_widgets[key][STATUS] = False
                    self.table_widgets[key][WIDGET].set_connection_status(False)
                    self.table_widgets[key][WIDGET].change_action_item(CONNECT_ID, CONNECT)
                        
        read_end = perf_counter()
        print(f"Reading registers :{read_end - read_start}" )
        return result_dict

