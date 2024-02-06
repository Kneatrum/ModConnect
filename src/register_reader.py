"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""

from PyQt5.QtCore import QRunnable, QThreadPool
from time import perf_counter

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        self.fn(*self.args, **self.kwargs)


class Observer:
    def __init__(self):
        self.table_widgets =[]
        self.threadpool = QThreadPool()

    
    def add_table_widget(self, table_view):
        if table_view not in self.table_widgets:
            self.table_widgets.append(table_view)

    def remove_table_widget(self, table_view):
        self.table_widgets.remove(table_view)

    def read_all_registers(self):
        # Reading register data.
        read_start = perf_counter()
        for table_view in self.table_widgets:
            table_view.read_registers()
        read_end = perf_counter()
        print(f"Reading registers :{read_end - read_start}" )
    
    def update_all_table_widgets(self):
        # Updating register data.
        update_start = perf_counter()
        for table_view in self.table_widgets:
            table_view.update_register_data()
        update_end = perf_counter()
        print(f"Updating gui:{update_end - update_start}")

    def refresh_gui(self):
        worker = Worker(lambda: self.update_all_table_widgets())
        self.threadpool.start(worker)
