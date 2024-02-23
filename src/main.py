import sys
from PyQt5.QtCore import Qt, QThreadPool, QCoreApplication
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from file_handler import FileHandler 
from tableview import TableWidget as tablewidget
from serial_ports import SerialPorts
from register_reader import Observer, Worker
import threading
import time

from PyQt5.QtWidgets import  QScrollArea, \
    QGroupBox, QWidget, QMenu, QAction, \
    QMenuBar, QPushButton,  QVBoxLayout, \
    QLabel, QLineEdit, QComboBox, \
    QDialog, QHBoxLayout, QCheckBox, QTableWidget, QTableWidgetItem, QSizePolicy

from constants import SLAVE_ADDRESS, \
        BAUD_RATE, PORT, DEVICE_NAME, HOST, \
        CONNECTION_PARAMETERS, RTU_PARAMETERS, \
        TCP_PARAMETERS, DEVICE_PREFIX, BYTESIZE, \
        TIMEOUT, PARITY, STOP_BITS, BYTESIZE, \
        PARITY_ITEMS, STOP_BIT_ITEMS, BAUD_RATE_ITEMS, \
        BYTESIZE_ITEMS, TIMEOUT_ITEMS, REGISTERS, \
        DEFAULT_METHOD, SERIAL_PORT

# Constant that stores the index of the column that displays the value of the read registers.
VALUE_COLUMN = 2

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_handler = FileHandler()

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
        self.setWindowTitle("Modpoll")

        # Defining the menu bar
        menubar = QMenuBar(self)
        fileMenu = QMenu('File', self)
        editMenu = QMenu('Edit', self)
        menubar.addMenu(fileMenu)
        menubar.addMenu(editMenu)

        # Add actions to the "File" menu
        newAction = QAction('New', self)
        # Connect the "triggered" signal of the "New" QAction to the "on_new_button_clicked" function
        newAction.triggered.connect(self.on_new_button_clicked)

        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        saveAction.triggered.connect(self.start_ui_refresh)
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)

        # Add actions to the "Edit" menu
        cutAction = QAction('Cut', self)
        copyAction = QAction('Copy', self)
        pasteAction = QAction('Paste', self)
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        self.setMenuBar(menubar)
        
        # Display all the registered devices on the screen
        self.main_widget = self.create_central_widget()


        self.main_thread = threading.main_thread()
        self.ready_to_poll_event =  threading.Event()
        t2 = threading.Thread(target=self.monitor_connected_devices)
        t2.start()


    def start_tasks(self):
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

            for device in self.observer.table_widgets:
                if device not in self.observer.connected_devices:
                    if device.selected_connection and device.selected_connection.is_connected():
                        self.observer.connected_devices.append(device)
                else:
                    if device.selected_connection and not device.selected_connection.is_connected():
                        self.observer.connected_devices.remove(device)
            # print("\t\t\t\t\tConnected devices : ", len(self.observer.connected_devices))
            time.sleep(0.5)






    def start_ui_refresh(self):
        self.connected_devices = self.main_widget.findChildren(QTableWidget)
        self.start_tasks()

            

    def on_new_button_clicked(self):
        dialog = AddNewDevice()
        if dialog.exec_() == QDialog.Accepted:
            self.main_widget = self.create_central_widget()


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
            layout = QHBoxLayout()
            for index in range(saved_devices):
                widget = tablewidget(index + 1) # Create and instance of our table widget. Adding 1 to prevent having device_0
                self.observer.add_table_widget(widget)
                layout.addWidget(widget) # Create the table widgets and add them in the horizontal layout
                layout.addStretch()
            return layout
        return None
    

    def create_scroll_area_layout(self, layout):
        """
        This function creates a scroll area using a layout that is passed in as a parameter

        arguments: 
            layout: A horizontal layout containing a number of QTableWidgets to be displayed.

        returns:
            layout: A vertical layout in a scroll area
        """
        # Create a scroll area widget and add the horizontal layout to it
        scroll_area = QScrollArea()
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(QWidget())
        scroll_area.widget().setLayout(layout)
        # Add the scroll area widget to the main layout
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        return layout

        #self.setLayout(self.main_layout)  # Set the main layout
        

    def create_central_widget(self):
        """
        This function gets a scroll area layout and creates a central widget.

        arguments:
            scroll_area_layout: The scroll area layout

        returns:
            central_widget: The central widget which is used to display all the QtableWidgets.
        """
        layout = self.add_widgets_to_horizontal_layout()
        if not layout:
            print("Could not create a layout")
            return None
        scroll_area = self.create_scroll_area_layout(layout)
        central_widget = QWidget()
        central_widget.setLayout(scroll_area) # Assign the main layout to the central widget
        self.setCentralWidget(central_widget)
        # Add a small space between the menu bar and the central widget
        self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)  
        return central_widget
        



  

  
class AddNewDevice(QDialog):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()

        self.setWindowTitle("Connect")

        # Create the main Vertical layout
        self.device_setup_main_layout = QVBoxLayout()
        
        self.device_number = self.file_handler.get_device_count() + 1

        # Create a horizontal layout for the Modbus options (radio buttons)
        modbus_options_layout = QHBoxLayout()
        self.modbus_tcp_check_box = QCheckBox("Modbus TCP")
        self.modbus_rtu_check_box = QCheckBox("Modbus RTU")
        # Add radio buttons to the layout
        modbus_options_layout.addWidget(self.modbus_tcp_check_box)
        modbus_options_layout.addWidget(self.modbus_rtu_check_box)
        # Add the Modbus options layout to the main layout
        self.device_setup_main_layout.addLayout(modbus_options_layout)

        # Generate Modbus RTU and Modbus TCP group boxes and set them as invisible.
        rtu_groupbox = RtuGroupBox("Modbus RTU")
        tcp_groupbox = TcpGroupBox("Modbus TCP")
        status = self.modbus_tcp_check_box.isChecked() and self.modbus_rtu_check_box.isChecked()
        rtu_groupbox.set_custom_name_invisible(status)
        tcp_groupbox.set_custom_name_invisible(status)
        self.modbus_rtu_group_box = rtu_groupbox
        self.modbus_tcp_group_box = tcp_groupbox
        self.modbus_tcp_group_box.setVisible(False)
        self.modbus_rtu_group_box.setVisible(False)

        # Connect radio buttons to show/hide the respective group boxes
        self.modbus_tcp_check_box.stateChanged.connect(self.toggle_tcp_groupbox)
        self.modbus_rtu_check_box.stateChanged.connect(self.toggle_rtu_groupbox)

        self.modbus_tcp_check_box.toggled.connect(self.update_button_visibility)
        self.modbus_rtu_check_box.toggled.connect(self.update_button_visibility)

        self.modbus_tcp_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.modbus_rtu_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Create a QPushButton for the submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setVisible(False)
        self.submit_button.clicked.connect(self.submit_user_input)

        # Add the "Modbus RTU", "Modbus TCP" and submit button to the main layout.
        self.device_setup_main_layout.addWidget(self.modbus_rtu_group_box)
        self.device_setup_main_layout.addWidget(self.modbus_tcp_group_box)
        self.device_setup_main_layout.addWidget(self.submit_button)

        self.device_setup_main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Set size constraint

        # Execute the dialog box
        self.setLayout(self.device_setup_main_layout)


    def toggle_tcp_groupbox(self,state):
        self.modbus_tcp_group_box.setVisible(state)
        self.update_button_visibility()



    def toggle_rtu_groupbox(self,state):
        self.modbus_rtu_group_box.setVisible(state)
        self.update_button_visibility()

    def update_button_visibility(self):
        self.submit_button.setVisible(self.modbus_tcp_group_box.isVisible() or self.modbus_rtu_group_box.isVisible())
        status = self.modbus_tcp_check_box.isChecked() and self.modbus_rtu_check_box.isChecked()
        self.modbus_rtu_group_box.set_custom_name_invisible(status)
        self.modbus_tcp_group_box.set_custom_name_invisible(status)
        
    def submit_user_input(self) -> dict:
        # Check which radio button is selected (Modbus TCP or Modbus RTU)
        if self.modbus_tcp_check_box.isChecked(): 
            temp_dict = {}
            tcp_client_dict = {}

            # Modbus TCP is selected
            slave_address_value = self.modbus_tcp_group_box.tcp_slave_id.text()
            device_name_value = self.modbus_tcp_group_box.tcp_custom_name.text()
            tcp_client_dict[HOST] = self.modbus_tcp_group_box.ip_address.text()
            tcp_client_dict[PORT] = self.modbus_tcp_group_box.port.text()

            temp_dict = {SLAVE_ADDRESS: slave_address_value, DEVICE_NAME: device_name_value, DEFAULT_METHOD: {}, CONNECTION_PARAMETERS: {RTU_PARAMETERS: {}, TCP_PARAMETERS:tcp_client_dict}, REGISTERS:{}}
            temp_dict = {f'{DEVICE_PREFIX}{self.device_number}': temp_dict}

            self.file_handler.add_device(temp_dict)

        if self.modbus_rtu_check_box.isChecked():
            temp_dict = {}
            rtu_client_dict = {}
            slave_address_dict = {}

            
            # Modbus RTU is selected
            device_name = self.modbus_rtu_group_box.rtu_custom_name.text()
            slave_address_dict[SLAVE_ADDRESS] = self.modbus_rtu_group_box.rtu_slave_id.text()
            rtu_client_dict[SERIAL_PORT] = self.modbus_rtu_group_box.com_ports.currentText()  # Get the selected COM Port
            rtu_client_dict[BAUD_RATE] = self.modbus_rtu_group_box.baud_rates.currentText()
            rtu_client_dict[PARITY] = self.modbus_rtu_group_box.parity_options.currentText()
            rtu_client_dict[STOP_BITS] = self.modbus_rtu_group_box.stop_bits_options.currentText()
            rtu_client_dict[BYTESIZE] = self.modbus_rtu_group_box.byte_size_options.currentText()
            rtu_client_dict[TIMEOUT] = self.modbus_rtu_group_box.timeout_options.currentText()

            temp_dict = {SLAVE_ADDRESS: slave_address_dict, DEVICE_NAME: device_name, DEFAULT_METHOD: {}, CONNECTION_PARAMETERS: {RTU_PARAMETERS: rtu_client_dict, TCP_PARAMETERS:{}}, REGISTERS:{}}
            temp_dict = {f'{DEVICE_PREFIX}{self.device_number}': temp_dict}

            self.file_handler.add_device(temp_dict)
        self.accept()

class TcpGroupBox(QGroupBox):
        # Create a QGroupBox for the "Set" elements
    def __init__(self, title, parent=None):
        super(TcpGroupBox, self).__init__(title, parent)
        modbus_tcp_group_box = QGroupBox("Modbus TCP", self)
        modbus_tcp_group_box.setFixedWidth(450)  # Set a fixed width to prevent resizing

        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        tcp_custom_name_layout = QHBoxLayout()
        self.tcp_custom_name_label = QLabel("Custom Name")
        self.tcp_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus TCP"
        tcp_custom_name_layout.addWidget(self.tcp_custom_name_label)
        tcp_custom_name_layout.addWidget(self.tcp_custom_name)

        # Create the first horizontal layout and add Slave ID label and its edit box for "Modbus TCP"
        tcp_slave_id_h_layout = QHBoxLayout()
        self.tcp_slave_id_label = QLabel("Slave ID")
        self.tcp_slave_id = QLineEdit()

        # Create the second horizontal layout and add IP Address label and its edit box for "Modbus TCP"
        r_set_h_layout_2 = QHBoxLayout()  
        self.ip_address_label = QLabel("IP Address")
        self.ip_address = QLineEdit()

        # Create the third horizontal layout and add Port Number label and its edit box for "Modbus TCP"
        r_set_h_layout_3 = QHBoxLayout() 
        self.port_label = QLabel("Port Number")
        self.port = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus TCP"
        tcp_slave_id_h_layout.addWidget(self.tcp_slave_id_label)
        tcp_slave_id_h_layout.addWidget(self.tcp_slave_id)

        # Add label and IP Address widgets to the second horizontal layout for "Set"
        r_set_h_layout_2.addWidget(self.ip_address_label)
        r_set_h_layout_2.addWidget(self.ip_address)

        # Add label and Port widgets to the third horizontal layout for "Set"
        r_set_h_layout_3.addWidget(self.port_label)
        r_set_h_layout_3.addWidget(self.port)

        # Create a the first vertical layout and add the slave ID layout
        r_set_v_layout_1 = QVBoxLayout()
        r_set_v_layout_1.addLayout(tcp_slave_id_h_layout)  

        # Create the second vertical layout and add the IP Address layout
        r_set_v_layout_2 = QVBoxLayout()
        r_set_v_layout_2.addLayout(r_set_h_layout_2)  

        # Create the third vertical layout and add the Port layout
        r_set_v_layout_3 = QVBoxLayout()
        r_set_v_layout_3.addLayout(r_set_h_layout_3)  

    
        # Create a vertical layout for the elements inside the "Modbus TCP" group box
        modbust_tcp_group_box_layout = QVBoxLayout()
        modbust_tcp_group_box_layout.addLayout(tcp_custom_name_layout)
        modbust_tcp_group_box_layout.addLayout(r_set_v_layout_1)
        modbust_tcp_group_box_layout.addLayout(r_set_v_layout_2)
        modbust_tcp_group_box_layout.addLayout(r_set_v_layout_3)

        # Set the layout of the "Modbus TCP" group box
        self.setLayout(modbust_tcp_group_box_layout)
        self.resize(300, 200)

    def set_custom_name_invisible(self, status):
        status = not status
        self.tcp_custom_name_label.setVisible(status)
        self.tcp_custom_name.setVisible(status)



class RtuGroupBox(QGroupBox):
    """
    Create a QGroupBox for the "Modbus RTU" elements
    
    """
    def __init__(self, title, parent=None):
        super(RtuGroupBox, self).__init__(title, parent)
        self.modbus_rtu_group_box = QGroupBox("Modbus RTU", self)
        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        self.rtu_custom_name_layout = QHBoxLayout()
        self.rtu_custom_name_label = QLabel("Custom Name")
        self.rtu_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus RTU"
        self.rtu_custom_name_layout.addWidget(self.rtu_custom_name_label)
        self.rtu_custom_name_layout.addWidget(self.rtu_custom_name)

        # Create the first horizontal layout and add Slave ID label and its edit box for "Modbus RTU"
        rtu_slave_id_layout = QHBoxLayout()
        self.rtu_slave_id_label = QLabel("Slave ID")
        self.rtu_slave_id = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus RTU"
        rtu_slave_id_layout.addWidget(self.rtu_slave_id_label)
        rtu_slave_id_layout.addWidget(self.rtu_slave_id)

        # Create a vertical layout and add a dropdown list of the com ports for "Modbus RTU"
        com_ports_layout = QHBoxLayout()
        self.com_ports_label = QLabel("COM")
        com_ports_layout.addWidget(self.com_ports_label)  # Add the label to the horizontal layout

        self.com_port_items = SerialPorts.get_available_ports()
        # Create a list of the available com port
        self.com_ports = QComboBox()  # Create a drop-down list of com ports
        self.com_ports.addItems(self.com_port_items)  # Add com ports to the dropdown list for "Modbus RTU"
        com_ports_layout.addWidget(self.com_ports)  # Add com ports to the widget for "Modbus RTU"

        # Create a Horizontal layout and add a dropdown list of the com ports for "Modbus RTU"
        baud_rate_layout = QHBoxLayout()
        self.baud_rate_label = QLabel("Baud Rate")
        baud_rate_layout.addWidget(self.baud_rate_label)  # Add the label to the horizontal layout

    
        # Create a list of baud rates for "Modbus RTU"
        self.baud_rates = QComboBox()  # Create a drop-down list of the baud rates for "Modbus RTU"
        self.baud_rates.addItems(BAUD_RATE_ITEMS)  # Add baud rates to the dropdown list for "Modbus RTU"
        baud_rate_layout.addWidget(self.baud_rates)  # Add baud rates to the widget for "Modbus RTU"


        # Create a Horizontal layout and add a dropdown list of the Parity 
        parity_layout = QHBoxLayout()
        self.parity_label = QLabel("Parity")
        parity_layout.addWidget(self.parity_label)  # Add the label to the horizontal layout

    
        # Create a list of Parity options
        self.parity_options = QComboBox()  # Create a drop-down list of the Parity options.
        self.parity_options.addItems(PARITY_ITEMS)  # Add the parity options to the dropdown list.
        parity_layout.addWidget(self.parity_options)  # Add the parity options to the widget.

        # Create a Horizontal layout and add a dropdown list of the Stop bits 
        stop_bits_layout = QHBoxLayout()
        self.stop_bits_label = QLabel("Stop bits")
        stop_bits_layout.addWidget(self.stop_bits_label)  # Add the label to the horizontal layout


        # Create a list of stop bits options
        self.stop_bits_options = QComboBox()  # Create a drop-down list of the stop bits options.
        self.stop_bits_options.addItems(STOP_BIT_ITEMS)  # Add the stop bits options to the dropdown list.
        stop_bits_layout.addWidget(self.stop_bits_options)  # Add the stop bits options to the widget.

        # Create a Horizontal layout and add a dropdown list of the byte size options
        byte_size_layout = QHBoxLayout()
        self.byte_size_label = QLabel("Byte size")
        byte_size_layout.addWidget(self.byte_size_label)  # Add the label to the horizontal layout


        # Create a list of byte size options
        self.byte_size_options = QComboBox()  # Create a drop-down list of the byte size options.
        self.byte_size_options.addItems(BYTESIZE_ITEMS)  # Add the byte size options to the dropdown list.
        byte_size_layout.addWidget(self.byte_size_options)  # Add the byte size options to the widget.

        # Create a Horizontal layout and add list of timeout in seconds
        timeout_layout = QHBoxLayout()
        self.timeout_label = QLabel("Byte size")
        timeout_layout.addWidget(self.timeout_label)  # Add the label to the horizontal layout


        # Create a list of byte size options
        self.timeout_options = QComboBox()  # Create a drop-down list of the seconds.
        self.timeout_options.addItems(TIMEOUT_ITEMS)  # Add the timeout options to the dropdown list.
        timeout_layout.addWidget(self.timeout_options)  # Add the timeout options to the widget.

        # Create a vertical layout for the elements inside the "Modbus RTU" group box
        modbus_rtu_group_box_layout = QVBoxLayout()
        modbus_rtu_group_box_layout.addLayout(self.rtu_custom_name_layout)
        modbus_rtu_group_box_layout.addLayout(rtu_slave_id_layout)
        modbus_rtu_group_box_layout.addLayout(com_ports_layout)
        modbus_rtu_group_box_layout.addLayout(baud_rate_layout)
        modbus_rtu_group_box_layout.addLayout(parity_layout)
        modbus_rtu_group_box_layout.addLayout(stop_bits_layout)
        modbus_rtu_group_box_layout.addLayout(byte_size_layout)
        modbus_rtu_group_box_layout.addLayout(timeout_layout)

        # Set the layout of the "Modbus RTU" group box
        self.setLayout(modbus_rtu_group_box_layout)
        self.resize(300,300)

    def set_custom_name_invisible(self, status):
        status = not status
        self.rtu_custom_name_label.setVisible(status)
        self.rtu_custom_name.setVisible(status)

        # Initially hide "Modbus TCP" and "Modbus RTU" group boxes



    


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()
