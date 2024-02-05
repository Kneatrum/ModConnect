"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""

from PyQt5.QtCore import QRunnable, QThreadPool


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

    def update_table_widget(self):
        # Reading register data.
        for table_view in self.table_widgets:
            table_view.read_registers()
            
        # Updating register data.
        for table_view in self.table_widgets:
            table_view.update_register_data()

    def refresh_gui(self):
        worker = Worker(lambda: self.update_table_widget())
        self.threadpool.start(worker)
