"""
This module implements the observer pattern in reading and updating the register table or table widget.
"""

import time
import threading


class Observer:
    def __init__(self):
        self.table_widgets =[]

    
    def add_table_widget(self, table_view):
        if table_view not in self.table_widgets:
            self.table_widgets.append(table_view)

    def remove_table_widget(self, table_view):
        self.table_widgets.remove(table_view)

    def update_table_widget(self):
        # Reading register data.
        threads = []
        for table_view in self.table_widgets:
            thread = threading.Thread(target=table_view.read_registers)
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        # Updating register data.
        threads = []
        for table_view in self.table_widgets:
            thread = threading.Thread(target=table_view.update_register_data)
            thread.start()
            threads.append(thread)

        for process in threads:
            process.join()