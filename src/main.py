import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from file_handler import FileHandler 
from tableview import TableWidget as tablewidget
from serial_ports import SerialPorts
from register_reader import Observer
from threading import Thread
import threading
import time

from PyQt5.QtWidgets import  QScrollArea, \
    QGroupBox, QWidget, QMenu, QAction, \
    QMenuBar, QPushButton,  QVBoxLayout, \
    QLabel, QLineEdit, QComboBox, \
    QDialog, QHBoxLayout, QRadioButton

from constants import SLAVE_ADDRESS, \
        BAUD_RATE, PORT, DEVICE_NAME, HOST, \
        CONNECTION_PARAMETERS, RTU_PARAMETERS, \
        TCP_PARAMETERS, DEVICE_PREFIX, BYTESIZE, \
        TIMEOUT, PARITY, STOP_BITS, BYTESIZE, \
        PARITY_ITEMS, STOP_BIT_ITEMS, BAUD_RATE_ITEMS, \
        BYTESIZE_ITEMS, TIMEOUT_ITEMS, REGISTERS, \
        DEFAULT_METHOD



class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_handler = FileHandler()

        self.file_handler.create_path_if_not_exists()
        
        # Initializing the main window

        self.main_widget = None
        self.observer = Observer()


        

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
        self.add_devices_to_layout()


        # Timer for updating register data on each table widget.
        # self.table_widget_timer = QtCore.QTimer()
        # self.table_widget_timer.timeout.connect(self.observer.refresh_gui)

        self.main_thread = threading.main_thread()
        self.connected_devices = []
        self.ready_to_poll_event =  threading.Event()
        print("Threads : ", self.main_thread)
        print("Thread count : ", threading.active_count())
        self.t1 = threading.Thread(target=self.register_reading_loop)
        t2 = threading.Thread(target=self.monitor_connected_devices)
        
        t2.start()


    def monitor_connected_devices(self):
        while self.main_thread.is_alive():
            if not self.ready_to_poll_event.is_set():
                if len(self.connected_devices) > 0:
                    self.ready_to_poll_event.set()
                elif len(self.connected_devices) == 0:
                    self.ready_to_poll_event.clear()

            for device in self.observer.table_widgets:
                if device not in self.connected_devices:
                    if device.selected_connection.is_connected():
                        self.connected_devices.append(device)
                else:
                    if not device.selected_connection.is_connected():
                        self.connected_devices.remove(device)
            print("                 Connected devices : ", len(self.connected_devices))
            time.sleep(0.5)

    def register_reading_loop(self):
        while self.main_thread.is_alive():
            self.observer.read_all_registers()
            print("Done reading\n")
            time.sleep(1)
        





    def start_ui_refresh(self):
        self.t1.start()

            

    def on_new_button_clicked(self):
        self.show_new_device_dialog()
        user_input = self.get_user_input()
         
        # print("Adding a new device")
        self.file_handler.add_device(user_input)
        self.add_devices_to_layout()


    '''
    This is the functions responsible for displaying all the registered devices on the screen.
    
    '''
    def add_devices_to_layout(self):
        self.observer.table_widgets.clear()
        saved_devices = self.file_handler.get_device_count()
        if saved_devices:
            self.main_widget = self.table_widget_setup(saved_devices)
            self.setCentralWidget(self.main_widget)
            # Add a small space between the menu bar and the central widget
            self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)
            self.show()
        

    
    def table_widget_setup(self,saved_devices):
        if saved_devices:
            # Create a central widget
            central_widget = QWidget()
            # Create a horizontal layout to add the table widgets
            self.horizontal_layout = QHBoxLayout()
            for index in range(saved_devices):
                widget = tablewidget(index + 1) # Create and instance of our table widget. Adding 1 to prevent having device_0
                self.observer.add_table_widget(widget)
                self.horizontal_layout.addWidget(widget) # Create the table widgets and add them in the horizontal layout
            self.horizontal_layout.addStretch() 
            

            # Create a scroll area widget and add the horizontal layout to it
            scroll_area = QScrollArea()
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(QWidget())
            scroll_area.widget().setLayout(self.horizontal_layout)

            # Add the scroll area widget to the main layout
            self.main_layout = QVBoxLayout()
            self.main_layout.addWidget(scroll_area)
            #self.setLayout(self.main_layout)  # Set the main layout

            central_widget.setLayout(self.main_layout) # Assign the main layout to the central widget
            return central_widget
        



  

  
    def show_new_device_dialog(self):
        self.register_setup_dialog = QDialog(self)
        self.register_setup_dialog.setWindowTitle("Connect")

        # Create the main Vertical layout
        device_setup_main_layout = QVBoxLayout()

        
        self.device_number = self.file_handler.get_device_count() + 1

        # Create a QGroupBox for the entire dialog
        dialog_group_box = QGroupBox("Device " + str(self.device_number), self)

        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        tcp_custom_name_layout = QHBoxLayout()
        self.tcp_custom_name_label = QLabel("Custom Name")
        self.tcp_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus TCP"
        tcp_custom_name_layout.addWidget(self.tcp_custom_name_label)
        tcp_custom_name_layout.addWidget(self.tcp_custom_name)



        # Create a horizontal layout for the Modbus options (radio buttons)
        modbus_options_layout = QHBoxLayout()
        
        self.modbus_tcp_radio = QRadioButton("Modbus TCP")
        self.modbus_rtu_radio = QRadioButton("Modbus RTU")
        
        # Add radio buttons to the layout
        modbus_options_layout.addWidget(self.modbus_tcp_radio)
        modbus_options_layout.addWidget(self.modbus_rtu_radio)
        
        # Add the Modbus options layout to the main layout
        device_setup_main_layout.addLayout(modbus_options_layout)

        # Create a QGroupBox for the "Set" elements
        modbus_tcp_group_box = QGroupBox("Modbus TCP", self)
        modbus_tcp_group_box.setFixedWidth(450)  # Set a fixed width to prevent resizing

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
        modbus_tcp_group_box.setLayout(modbust_tcp_group_box_layout)


        """
        Create a QGroupBox for the "Modbus RTU" elements
        
        """
        modbus_rtu_group_box = QGroupBox("Modbus RTU", self)
        modbus_rtu_group_box.setFixedWidth(450)  # Set a fixed width to prevent resizing


        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        rtu_custom_name_layout = QHBoxLayout()
        self.rtu_custom_name_label = QLabel("Custom Name")
        self.rtu_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus RTU"
        rtu_custom_name_layout.addWidget(self.rtu_custom_name_label)
        rtu_custom_name_layout.addWidget(self.rtu_custom_name)

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

        # Create a QPushButton for the submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.get_user_input)

        # Create a layout for the dialog
        submit_button_layout = QVBoxLayout()
        submit_button_layout.addWidget(submit_button)


        # Create a vertical layout for the elements inside the "Modbus RTU" group box
        modbus_rtu_group_box_layout = QVBoxLayout()
        modbus_rtu_group_box_layout.addLayout(rtu_custom_name_layout)
        modbus_rtu_group_box_layout.addLayout(rtu_slave_id_layout)
        modbus_rtu_group_box_layout.addLayout(com_ports_layout)
        modbus_rtu_group_box_layout.addLayout(baud_rate_layout)
        modbus_rtu_group_box_layout.addLayout(parity_layout)
        modbus_rtu_group_box_layout.addLayout(stop_bits_layout)
        modbus_rtu_group_box_layout.addLayout(byte_size_layout)
        modbus_rtu_group_box_layout.addLayout(timeout_layout)
        


        # Set the layout of the "Modbus RTU" group box
        modbus_rtu_group_box.setLayout(modbus_rtu_group_box_layout)

        # Initially hide "Modbus TCP" and "Modbus RTU" group boxes
        modbus_tcp_group_box.hide()
        modbus_rtu_group_box.hide()

        # Connect radio buttons to show/hide the respective group boxes
        self.modbus_tcp_radio.toggled.connect(lambda: modbus_tcp_group_box.setVisible(self.modbus_tcp_radio.isChecked()))
        self.modbus_rtu_radio.toggled.connect(lambda: modbus_rtu_group_box.setVisible(self.modbus_rtu_radio.isChecked()))

        # Add the "Modbus RTU" group box to the main layout
        device_setup_main_layout.addWidget(modbus_rtu_group_box)

        # Add the "Modbus RTU" group box to the main layout
        device_setup_main_layout.addWidget(modbus_tcp_group_box)

        device_setup_main_layout.addLayout(submit_button_layout)

        # Add the main layout to the main group box
        dialog_group_box.setLayout(device_setup_main_layout)

        # Execute the dialog box
        self.register_setup_dialog.setLayout(device_setup_main_layout)
        self.register_setup_dialog.exec_()




    def get_user_input(self) -> dict:
        # Check which radio button is selected (Modbus TCP or Modbus RTU)
        temp_dict = {}
        if self.modbus_tcp_radio.isChecked(): 
            tcp_client_dict = {}
            # Modbus TCP is selected
            slave_address_value = self.tcp_slave_id.text()
            device_name_value = self.tcp_custom_name.text()
            tcp_client_dict[HOST] = self.ip_address.text()
            tcp_client_dict[PORT] = self.port.text()

            temp_dict = {SLAVE_ADDRESS: slave_address_value, DEVICE_NAME: device_name_value, CONNECTION_PARAMETERS: {RTU_PARAMETERS: {}, TCP_PARAMETERS:tcp_client_dict, DEFAULT_METHOD: {}}, REGISTERS:{}}
            temp_dict = {f'{DEVICE_PREFIX}{self.device_number}': temp_dict}
            self.register_setup_dialog.accept()
        elif self.modbus_rtu_radio.isChecked():
            rtu_client_dict = {}
            slave_address_dict = {}
            device_name_dict = {}
            # Modbus RTU is selected
            device_name_dict[DEVICE_NAME] = self.rtu_custom_name.text()
            slave_address_dict[SLAVE_ADDRESS] = self.rtu_slave_id.text()
            rtu_client_dict[PORT] = self.com_ports.currentText()  # Get the selected COM Port
            rtu_client_dict[BAUD_RATE] = self.baud_rates.currentText()
            rtu_client_dict[PARITY] = self.parity_options.currentText()
            rtu_client_dict[STOP_BITS] = self.stop_bits_options.currentText()
            rtu_client_dict[BYTESIZE] = self.byte_size_options.currentText()
            rtu_client_dict[TIMEOUT] = self.timeout_options.currentText()

            temp_dict = {SLAVE_ADDRESS: slave_address_dict, DEVICE_NAME: device_name_dict, CONNECTION_PARAMETERS: {RTU_PARAMETERS: rtu_client_dict, TCP_PARAMETERS:{}, DEFAULT_METHOD: {}}, REGISTERS:{}}
            temp_dict = {f'{DEVICE_PREFIX}{self.device_number}': temp_dict}
            self.register_setup_dialog.accept()
        return temp_dict
        
    
        


        
        














if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()
