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
from constants import STATUS, WIDGET, DISCONNECT, CONNECT, SELECT_ACTION_ID, ADD_REGISTERS_ID, REMOVE_REGISTERS_ID, \
                        CONNECT_ID, HIDE_DEVICE_ID, DELETE_DEVICE_ID

from PyQt5.QtWidgets import  QScrollArea, QWidget,  QAction, \
    QVBoxLayout, QDialog, QHBoxLayout,  QTableWidget, \
    QTableWidgetItem,  QToolBar, QCheckBox, QLabel, QSizePolicy

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
        self.hidden_devices = self.file_handler.get_hidden_devices()
        
        # Initializing the main window

        self.main_widget = None
        self.observer = Observer()
        self.threadpool = QThreadPool()
        # self.connected_devices = []

        self.worker = Worker(self.observer.read_all_registers)
        self.worker.signals.result.connect(self.refresh_gui)
        # Stop the worker thread when the application is stopped.
        QCoreApplication.instance().aboutToQuit.connect(self.worker.stop)


        

        # Set the title of the window
        self.setWindowTitle("ModConnect")
        self.setGeometry(100, 100, 1100, 1100)


        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)  # Display icons and text labels side by side
        self.addToolBar(self.toolbar)
        # Create actions for the toolbar
        add_new_device_action = QAction(QIcon(resource_path('resources/more.png')),'Add New Device', self)
        add_new_device_action.triggered.connect(self.on_new_button_clicked)
        self.toolbar.addAction(add_new_device_action)

        self.toolbar.addSeparator()

        start_polling_action = QAction(QIcon(resource_path('resources/play-button.png')), 'Start Polling', self)
        start_polling_action.triggered.connect(self.start_ui_refresh)
        self.toolbar.addAction(start_polling_action)

        stop_polling_action = QAction(QIcon(resource_path('resources/stop-button.png')), 'Stop Polling', self)
        stop_polling_action.triggered.connect(self.stop_polling)
        self.toolbar.addAction(stop_polling_action)
        
        # Display all the registered devices on the screen
        self.initialize_ui()


        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        self.toolbar.addSeparator()
        hidden_widgets = QLabel('Hidden Widgets')
        # hidden_widgets.setStyleSheet("background-color: lightgray; padding: 5px;")  # Set background color and padding
        self.toolbar.addWidget(hidden_widgets)
        self.toolbar.addSeparator()
        
        for device_number in self.hidden_devices:
            self.add_hidden_device_to_toolbar(device_number)
        # hidden_widgets.triggered.connect(self.stop_polling)

        self.main_thread = threading.main_thread()
        self.ready_to_poll_event =  threading.Event()
        self.polling_stopped =  threading.Event()



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
        """
        This portion of the code checks how many devices are connected. If the number of devices is 0, we stop polling.
        """
        connected_devices = 0
        for device in self.observer.table_widgets.values():
            if device.connection_status == True:
                connected_devices += 1
        if connected_devices == 0:
            self.stop_polling()


        # The key of the dictionary represents the device number.
        if result is not None:
            for device_number in result.keys():
                # The value of the dictionary is a list of the register results for this particular device number.
                register_list = result[device_number]
                row_count = self.observer.table_widgets[device_number].table_widget.rowCount()

                # This happens as a precaution. Ideally, the number of registers should match the number of rows in the table widget.
                if len(register_list) < row_count:
                    print("Registers are less than the number of rows in the table.")
                    row_count = len(register_list)

                # Create a loop to iterate over the QtableWidget's rows and update the value column with the read registers.
                for row in range(row_count):
                    self.observer.table_widgets[device_number].table_widget.setItem(row, VALUE_COLUMN, QTableWidgetItem(str(register_list[row])))
            stop_time = time.perf_counter()
            print("Time :", stop_time - start_time)
        else:
            print("No results were transmitted.")



    def on_checkbox_state_changed(self):
        checkbox = self.sender()
        name = checkbox.text()
        for device in self.observer.table_widgets.values():
            if device.device_name == name:
                self.show_widget(device.device_number)
                checkbox.setParent(None)






    def start_ui_refresh(self):
        # self.connected_devices = self.main_central_widget.findChildren(QTableWidget)
        if self.ready_to_poll_event.is_set():
            self.start_tasks()
        else:
            self.notification.set_warning_message("No connected devices", "Please connect to a device first")

            

    def on_new_button_clicked(self):
        device_count = self.file_handler.get_device_count()
        if device_count >= self.file_handler.max_devices:
            self.notification.set_warning_message(f"{self.file_handler.max_devices} maximum devices.", "You have reached the maximum number of devices")
            return False
        dialog = AddNewDevice()
        if dialog.exec_() == QDialog.Accepted:
            new_device = dialog.device_number
            if new_device is not None:
                self.add_single_widget(new_device)


    def on_edit_button_clicked(self, index):
        edit_connection = EditConnection(index)
        if edit_connection.exec_() == QDialog.Accepted:
            self.observer.table_widgets[index].update_method_label()
            self.observer.table_widgets[index].update_device_name()
            self.observer.table_widgets[index].set_active_connection()


    def on_drop_down_menu_selected(self, device_number, position):
        current_table = self.observer.table_widgets[device_number]

        if position == ADD_REGISTERS_ID: # Add Registers
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)
            current_table.show_register_dialog() # Show the message box for adding registers
            current_table.list_of_registers = self.file_handler.get_registers_to_read(device_number) # Update the list of registers.
        elif position == REMOVE_REGISTERS_ID: # Remove Registers
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)
            if current_table.active_connection:
                print(f"Is device connected? :{current_table.active_connection.is_connected()}")
            else:
                print("No device connected")
        elif position == CONNECT_ID: # Connect/Disconnect
            current_text = current_table.action_menu.currentText()
            if current_text == CONNECT:
                result = current_table.connect_to_device()
                if result:
                    self.ready_to_poll_event.set()
                else:
                    current_table.notification.set_warning_message("Connection Failure", result)
            elif current_text ==  DISCONNECT: # Disconnect device
                current_table.disconnect_from_device()
                if not self.check_for_connected_devices():
                    self.ready_to_poll_event.clear()
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)
        elif position == HIDE_DEVICE_ID: # Hide device
            if self.observer.table_widgets[device_number].connection_status == True:
                self.notification.set_warning_message("Device is connected!", "Please disconnect before hiding the device.")
                return
            self.hide_widget(device_number)
            self.file_handler.update_hidden_status(device_number, True)
            self.add_hidden_device_to_toolbar(device_number)
        elif position == DELETE_DEVICE_ID: # Delete device
            if self.observer.table_widgets[device_number].connection_status == True:
                self.notification.set_warning_message("Device is connected!", "Please disconnect before deleting the device.")
                return
            self.delete_widget(device_number)


    def add_widgets_to_horizontal_layout(self):
        """
        This function adds all QTableWidgets to an horizontal layout

        arguments:
            None
        returns:
            layout: the horizontal layout or None
        """
        self.observer.table_widgets.clear()
        device_tags = self.file_handler.get_int_device_tags()
        if device_tags:
            # Create a central widget
            # Create a horizontal layout to add the table widgets
            for device_tag in device_tags:
                widget = tablewidget(device_tag) # Create and instance of our table widget. Adding 1 to prevent having device_0
                widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
                widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
                widget.modbus_method_label
                self.observer.add_table_widget(device_tag, widget)
                if widget.hidden_status == False:
                    self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout
            return True
        return None
    

    def add_single_widget(self, new_device_number):
        widget = tablewidget(new_device_number) # Create and instance of our table widget. Adding 1 to prevent having device_0
        widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
        widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
        widget.modbus_method_label
        self.observer.add_table_widget(new_device_number, widget)
        self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout


    def delete_widget(self, device_number):
        self.observer.table_widgets[device_number].setParent(None)
        self.observer.remove_table_widget(device_number)
        self.file_handler.delete_device(device_number)


    def hide_widget(self, device_number):
        self.hidden_devices.append(device_number)
        self.observer.table_widgets[device_number].hide()
        self.observer.table_widgets[device_number].hidden_status = True


    def show_widget(self, device_number):
        widget = tablewidget(device_number) # Create and instance of our table widget. Adding 1 to prevent having device_0
        widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
        widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
        self.observer.add_table_widget(device_number, widget)
        self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout
        self.observer.table_widgets[device_number].hidden_status = False
        self.file_handler.update_hidden_status(device_number, False)


    def add_hidden_device_to_toolbar(self, device_number):
        device_checkbox = QCheckBox(self.observer.table_widgets[device_number].device_name)
        device_checkbox.setChecked(True)
        device_checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        self.toolbar.addWidget(device_checkbox)
        self.toolbar.addSeparator()


    def check_for_connected_devices(self):
        for device in self.observer.table_widgets.values():
            if device.connection_status == True:
                return True
        return False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()
