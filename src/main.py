import sys
from PyQt5.QtCore import Qt, QThreadPool, QCoreApplication
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from file_handler import FileHandler 
from tableview import TableWidget as tablewidget
from custom_dialogs import EditConnection
from custom_dialogs import AddNewDevice
from register_reader import Observer, Worker
import threading
import time
from notifications import Notification

from PyQt5.QtWidgets import  QScrollArea, QWidget,  QAction, \
    QVBoxLayout, QDialog, QHBoxLayout,  QTableWidget, \
    QTableWidgetItem,  QToolBar

from constants import resource_path

# Constant that stores the index of the column that displays the value of the read registers.
VALUE_COLUMN = 2

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.scroll_area = QScrollArea()
        self.main_central_widget = QWidget()
        self.horizontal_box = QHBoxLayout()

        self.file_handler = FileHandler()
        self.notification = Notification()

        self.file_handler.create_path_if_not_exists()
        
        # Initializing the main window

        self.main_widget = None
        self.observer = Observer()
        self.threadpool = QThreadPool()
        self.connected_devices = []

        self.worker = Worker(self.observer.read_all_registers)
        self.worker.signals.result.connect(self.refresh_gui)
        # Stop the worker thread when the application is stopped.
        QCoreApplication.instance().aboutToQuit.connect(self.worker.stop)


        

        # Set the title of the window
        self.setWindowTitle("ModConnect")
        self.setGeometry(100, 100, 1100, 1100)


        customWidget = QWidget()
        # customWidget.setFixedHeight(30)  # Set the desired height for the toolbar
        # Create a toolbar and set the custom widget as its widget
        toolbar = QToolBar()
        toolbar.setStyleSheet("QToolBar { border: 0px; }")  # Remove border
        toolbar.addWidget(customWidget)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # Display icons and text labels side by side
        self.addToolBar(toolbar)
        # Create actions for the toolbar
        add_new_device_action = QAction(QIcon(resource_path('resources/more.png')),'Add New Device', self)
        add_new_device_action.triggered.connect(self.on_new_button_clicked)
        toolbar.addAction(add_new_device_action)

        toolbar.addSeparator()

        start_polling_action = QAction(QIcon(resource_path('resources/play-button.png')), 'Start Polling', self)
        start_polling_action.triggered.connect(self.start_ui_refresh)
        toolbar.addAction(start_polling_action)

        stop_polling_action = QAction(QIcon(resource_path('resources/stop-button.png')), 'Stop Polling', self)
        stop_polling_action.triggered.connect(self.stop_polling)
        toolbar.addAction(stop_polling_action)
        
        # Display all the registered devices on the screen
        self.initialize_ui()


        self.main_thread = threading.main_thread()
        self.ready_to_poll_event =  threading.Event()
        self.polling_stopped =  threading.Event()
        t2 = threading.Thread(target=self.monitor_connected_devices)
        t2.start()


    def initialize_ui(self):
        self.add_widgets_to_horizontal_layout()
        self.main_central_widget.setLayout(self.horizontal_box)

        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.main_central_widget)

        self.setCentralWidget(self.scroll_area)
        # self.centralWidget().layout().setContentsMargins(0, 20, 0, 50) 
        self.show()


    def stop_polling(self):
        self.worker.stop()
        self.polling_stopped.set()


    def start_tasks(self):
        if self.polling_stopped.is_set():
            self.worker = Worker(self.observer.read_all_registers)
            self.worker.signals.result.connect(self.refresh_gui)
            self.polling_stopped.clear()
        self.threadpool.start(self.worker)


    def refresh_gui(self, result):
        """
        This method is responsible for updating the GUI with the register results

        arguments:
            result (dict): This is a dictionary containing the device number and a list of its registers.

            Example: 
                {1: [2238, 2238, 2238], 2: [2221, 2221, 2221]}

        returns:
            None
        
        """
        start_time = time.perf_counter()
        # The key of the dictionary represents the device number.
        for device_number in result.keys():
            # The value of the dictionary is a list of the register results for this particular device number.
            register_list = result[device_number]
            # Create a loop to iterate over the QtableWidget's rows and update the value column with the read registers.
            for row in range(self.connected_devices[device_number - 1].rowCount()):
                self.connected_devices[device_number - 1].setItem(row, VALUE_COLUMN, QTableWidgetItem(str(register_list[row])))
        stop_time = time.perf_counter()
        print("Time :", stop_time - start_time)


    def monitor_connected_devices(self):
        while self.main_thread.is_alive():
            if not self.ready_to_poll_event.is_set():
                if len(self.observer.connected_devices) > 0:
                    self.ready_to_poll_event.set()
                elif len(self.observer.connected_devices) == 0:
                    self.ready_to_poll_event.clear()

            for device in self.observer.table_widgets.values():
                if device not in self.observer.connected_devices:
                    if device.selected_connection and device.selected_connection.is_connected():
                        self.observer.connected_devices.append(device)
                else:
                    if device.selected_connection and not device.selected_connection.is_connected():
                        self.observer.connected_devices.remove(device)
            # print("\t\t\t\t\tConnected devices : ", len(self.observer.connected_devices))
            time.sleep(0.5)






    def start_ui_refresh(self):
        # self.connected_devices = self.main_widget.findChildren(QTableWidget)
        if self.ready_to_poll_event.set():
            self.start_tasks()
        else:
            self.notification.set_warning_message("No connected devices", "Please connect to a device first")

            

    def on_new_button_clicked(self):
        dialog = AddNewDevice()
        if dialog.exec_() == QDialog.Accepted:
            self.add_single_widget()


    def on_edit_button_clicked(self, index):
        edit_connection = EditConnection(index)
        if edit_connection.exec_() == QDialog.Accepted:
            self.observer.table_widgets[index].update_method_label()


    def add_widgets_to_horizontal_layout(self):
        """
        This function adds all QTableWidgets to an horizontal layout

        arguments:
            None
        returns:
            layout: the horizontal layout or None
        """
        self.observer.table_widgets.clear()
        saved_devices = self.file_handler.get_device_count()
        if saved_devices:
            # Create a central widget
            # Create a horizontal layout to add the table widgets
            for index in range(saved_devices):
                temp_index = index + 1
                widget = tablewidget(temp_index) # Create and instance of our table widget. Adding 1 to prevent having device_0
                widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
                widget.modbus_method_label
                self.observer.add_table_widget(temp_index, widget)
                self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout
            return True
        return None
    

    def add_single_widget(self):
        saved_devices = self.file_handler.get_device_count()
        if not saved_devices:
            return None
        widget = tablewidget(saved_devices) # Create and instance of our table widget. Adding 1 to prevent having device_0
        widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
        widget.modbus_method_label
        self.observer.add_table_widget(saved_devices, widget)
        self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()
