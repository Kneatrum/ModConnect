import sys
from PyQt5.QtCore import Qt, QThreadPool, QCoreApplication, QTimer, QThread
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from file_handler import FileHandler 
from tableview import TableWidget as tablewidget
from custom_dialogs import EditConnection, AddNewDevice
from register_reader import Observer, DeviceWorker, PollCoordinator
import threading
from notifications import Notification
from constants import STATUS, WIDGET, DISCONNECT, CONNECT, SELECT_ACTION_ID, ADD_REGISTERS_ID, REMOVE_REGISTERS_ID, \
                        CONNECT_ID, HIDE_DEVICE_ID, DELETE_DEVICE_ID, MAX_DEVICES

from PyQt5.QtWidgets import  QScrollArea, QWidget,  QAction, \
    QVBoxLayout, QDialog, QHBoxLayout,  QTableWidget, \
    QTableWidgetItem,  QToolBar, QCheckBox, QLabel, QSizePolicy, QSpacerItem

from constants import resource_path
from time import perf_counter

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
        self.thread_manager_pool = QThreadPool()
        self.worker_dict = {}
        self.ready_for_reconnect = False
        self.device_list_ready_to_refresh = []   
        self.start_signal_count = 0
        self.finish_signal_count = 0
        self.connected_device_count = 0

        self.poll_mode = "synchronized"  # or "independent"
        self.global_interval_ms = 1000   # default
        self.coordinator_thread = None
        self.coordinator = None

        

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
        
        if self.hidden_devices is not None:
            for device_number in self.hidden_devices:
                self.add_hidden_device_to_toolbar(device_number)
        # hidden_widgets.triggered.connect(self.stop_polling)

        self.main_thread = threading.main_thread()
        self.ready_to_poll_event =  threading.Event()
        self.polling_stopped =  threading.Event()
        self.polling_stopped.set() # Polling is stopped by default when the application has started.



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

        # Stop workers first
        for device_number, (thread, worker) in self.worker_dict.items():
            worker.stop()

        # Then stop coordinator
        if self.coordinator:
            self.coordinator.stop()

        # Now quit threads
        if self.coordinator_thread:
            self.coordinator_thread.quit()
            self.coordinator_thread.wait(2000)

        for device_number, (thread, worker) in self.worker_dict.items():
            thread.quit()
            thread.wait(2000)

        self.worker_dict.clear()
        self.coordinator = None
        self.coordinator_thread = None

    def start_tasks(self):
        # Create workers
        for device in self.observer.table_widgets.values():
            if device.connection_status:

                thread = QThread()
                worker = DeviceWorker(device)

                worker.moveToThread(thread)
                thread.started.connect(worker.run)

                thread.start()

                self.worker_dict[device.device_number] = (thread, worker)

        if not self.worker_dict:
            return

        if self.poll_mode == "independent":

            for device_number, (thread, worker) in self.worker_dict.items():
                worker.result.connect(self.update_device_table)
                worker.trigger()  # Start continuous polling
                # For independent mode, you can modify worker to auto-loop

        else:
            # SYNCHRONIZED MODE

            workers = {k: w for k, (t, w) in self.worker_dict.items()}

            self.coordinator_thread = QThread()
            self.coordinator = PollCoordinator(
                workers,
                self.global_interval_ms
            )

            self.coordinator.moveToThread(self.coordinator_thread)
            self.coordinator_thread.started.connect(self.coordinator.run)
            self.coordinator.synchronized_snapshot.connect(
                self.handle_synchronized_snapshot
            )

            self.coordinator_thread.start()

    def handle_synchronized_snapshot(self, data_dict, timestamp):

        # Update GUI
        for device_number, register_data in data_dict.items():
            table = self.observer.table_widgets[device_number]

            for row, value in enumerate(register_data):
                table.table_widget.setItem(
                    row,
                    VALUE_COLUMN,
                    QTableWidgetItem(str(value))
                )

        # Future: log timestamp + data_dict
        print(f"Synchronized sample at {timestamp}")

    def count_starts(self):
        self.start_signal_count += 1
        

    def count_finish(self):
        self.finish_signal_count += 1        
        

    def update_device_table(self, device_number, register_data):

        table = self.observer.table_widgets[device_number]

        for row, value in enumerate(register_data):
            table.table_widget.setItem(
                row,
                VALUE_COLUMN,
                QTableWidgetItem(str(value))
            )

    def resume_polling(self):
        self.stop_polling()
        self.start_ui_refresh()


    def on_checkbox_state_changed(self):
        checkbox = self.sender()
        name = checkbox.text()
        for device in self.observer.table_widgets.values():
            if device.device_name == name:
                self.show_widget(device.device_number)
                checkbox.setParent(None)






    def start_ui_refresh(self):
        # self.connected_devices = self.main_central_widget.findChildren(QTableWidget)
        if not self.worker_dict and not self.coordinator:
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
        print(f"Type of index: {type(index)}")
        print(f"Edit button clicked for device {index}")
        edit_connection = EditConnection(index)
        if edit_connection.exec_() == QDialog.Accepted:
            self.observer.table_widgets[index].update_method_label()
            self.observer.table_widgets[index].update_device_name()
            self.observer.table_widgets[index].set_active_connection()
            self.observer.table_widgets[index].on_connection_settings_updated()


    def on_drop_down_menu_selected(self, device_number, position):
        current_table = self.observer.table_widgets[device_number]

        if position == ADD_REGISTERS_ID: # Add Registers
            current_table.action_menu.setCurrentIndex(SELECT_ACTION_ID)
            current_table.show_register_dialog() # Show the message box for adding registers
            current_table.list_of_registers = self.file_handler.get_registers_to_read(device_number) # Update the list of registers.
        elif position == REMOVE_REGISTERS_ID: # Remove Registers
            current_table.delete_registers()
        elif position == CONNECT_ID: # Connect/Disconnect
            current_text = current_table.action_menu.currentText()
            if current_text == CONNECT:
                result = current_table.connect_to_device()
                if result:
                    if self.ready_for_reconnect == True:
                        self.ready_for_reconnect = False
                        self.resume_polling()
                    else:
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
            beginning_spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(beginning_spacer_item)
            for device_tag in device_tags:
                widget = tablewidget(device_tag) # Create and instance of our table widget. Adding 1 to prevent having device_0
                widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
                widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
                # widget.modbus_method_label
                self.observer.add_table_widget(device_tag, widget)
                if widget.hidden_status == False:
                    self.horizontal_box.addWidget(widget) # Create the table widgets and add them in the horizontal layout
            # Add a spacer item at the end
            end_spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(end_spacer_item)
            return True
        return None
    

    def add_single_widget(self, new_device_number):
        tablewidget_count = self.horizontal_box.count()
        if tablewidget_count == 0:
            beginning_spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(beginning_spacer_item)
            end_spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.horizontal_box.addSpacerItem(end_spacer_item)

            widget = tablewidget(new_device_number) # Create and instance of our table widget. Adding 1 to prevent having device_0
            widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
            widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
            self.observer.add_table_widget(new_device_number, widget)
            self.horizontal_box.insertWidget(1, widget) # Add the new widget after the last widget in the horizontal layout

        elif tablewidget_count >= 2:
            tablewidget_count -= 2 # There are two spacers in the horizontal layout that we are going to ignore.
            widget = tablewidget(new_device_number) # Create and instance of our table widget. Adding 1 to prevent having device_0
            widget.edit_connection_button_clicked.connect(self.on_edit_button_clicked)
            widget.drop_down_menu_clicked.connect(self.on_drop_down_menu_selected)
            self.observer.add_table_widget(new_device_number, widget)
            self.horizontal_box.insertWidget(tablewidget_count + 1, widget) # Add the new widget after the last widget in the horizontal layout


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
        device_checkbox = QCheckBox(self.observer.table_widgets[device_number].device_name)
        device_checkbox.setChecked(True)
        device_checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        self.toolbar.addWidget(device_checkbox)
        # self.toolbar.addSeparator()


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
