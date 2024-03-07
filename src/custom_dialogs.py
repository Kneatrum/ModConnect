
from file_handler import FileHandler
from  modbus_group_boxes import RtuGroupBox, TcpGroupBox 

from PyQt5.QtWidgets import  QPushButton,  QVBoxLayout, QLabel, QLineEdit, \
    QDialog, QHBoxLayout, QCheckBox, QSizePolicy



from constants import SLAVE_ADDRESS, \
        BAUD_RATE, PORT, DEVICE_NAME, HOST, \
        CONNECTION_PARAMETERS, RTU_PARAMETERS, \
        TCP_PARAMETERS, DEVICE_PREFIX, BYTESIZE, \
        TIMEOUT, PARITY, STOP_BITS, BYTESIZE, \
        DEFAULT_METHOD, SERIAL_PORT, REGISTERS



class AddNewDevice(QDialog):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()

        self.setWindowTitle("Connection Setup")
        self.setGeometry(100, 100, 300, 300)  # Set the initial size and position of the dialog

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
 
        self.optional_tcp_custom_name_label = QLabel("Custom Name")
        self.optional_tcp_custom_name = QLineEdit()
        self.optional_tcp_custom_name_label.setVisible(False)
        self.optional_tcp_custom_name.setVisible(False)

        self.global_slave_address_label = QLabel("Slave Address")
        self.global_slave_address = QLineEdit()
        self.global_slave_address_label.setVisible(False)
        self.global_slave_address.setVisible(False)

        # Generate Modbus RTU and Modbus TCP group boxes and set them as invisible.
        rtu_groupbox = RtuGroupBox("Modbus RTU")
        tcp_groupbox = TcpGroupBox("Modbus TCP")
        status = self.modbus_tcp_check_box.isChecked() and self.modbus_rtu_check_box.isChecked()
        rtu_groupbox.set_custom_name_invisible(status)
        tcp_groupbox.set_custom_name_invisible(status)
        rtu_groupbox.set_slave_address_invisible(status)
        tcp_groupbox.set_slave_address_invisible(status)
        self.modbus_rtu_group_box = rtu_groupbox
        self.modbus_tcp_group_box = tcp_groupbox
        self.modbus_tcp_group_box.setVisible(False)
        self.modbus_rtu_group_box.setVisible(False)

        # Connect radio buttons to show/hide the respective group boxes
        self.modbus_tcp_check_box.stateChanged.connect(self.toggle_tcp_groupbox)
        self.modbus_rtu_check_box.stateChanged.connect(self.toggle_rtu_groupbox)

        self.modbus_tcp_check_box.toggled.connect(self.update_button_visibility)
        self.modbus_rtu_check_box.toggled.connect(self.update_button_visibility)

        self.modbus_tcp_check_box.toggled.connect(self.update_custom_name_visibility)
        self.modbus_rtu_check_box.toggled.connect(self.update_custom_name_visibility)

        self.modbus_tcp_check_box.toggled.connect(self.update_slave_address_visibility)
        self.modbus_rtu_check_box.toggled.connect(self.update_slave_address_visibility)

        self.modbus_tcp_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.modbus_rtu_group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Create a QPushButton for the submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setVisible(False)
        self.submit_button.clicked.connect(self.submit_user_input)

        # Add the "Modbus RTU", "Modbus TCP" and submit button to the main layout.
        self.device_setup_main_layout.addWidget(self.optional_tcp_custom_name_label)
        self.device_setup_main_layout.addWidget(self.optional_tcp_custom_name)
        self.device_setup_main_layout.addWidget(self.global_slave_address_label)
        self.device_setup_main_layout.addWidget(self.global_slave_address)
        self.device_setup_main_layout.addWidget(self.modbus_rtu_group_box)
        self.device_setup_main_layout.addWidget(self.modbus_tcp_group_box)
        self.device_setup_main_layout.addWidget(self.submit_button)

        self.device_setup_main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Set size constraint

        # Execute the dialog box
        self.setLayout(self.device_setup_main_layout)


    def toggle_tcp_groupbox(self,state):
        self.modbus_tcp_group_box.setVisible(state)
        self.update_button_visibility()
        self.update_custom_name_visibility()
        self.update_slave_address_visibility()



    def toggle_rtu_groupbox(self,state):
        self.modbus_rtu_group_box.setVisible(state)
        self.update_button_visibility()
        self.update_custom_name_visibility()
        self.update_slave_address_visibility()

    def update_button_visibility(self):
        self.submit_button.setVisible(self.modbus_tcp_group_box.isVisible() or self.modbus_rtu_group_box.isVisible())
        status = self.modbus_tcp_check_box.isChecked() and self.modbus_rtu_check_box.isChecked()
        self.modbus_rtu_group_box.set_custom_name_invisible(status)
        self.modbus_tcp_group_box.set_custom_name_invisible(status)
        self.modbus_rtu_group_box.set_slave_address_invisible(status)
        self.modbus_tcp_group_box.set_slave_address_invisible(status)

    def update_custom_name_visibility(self):
        status = self.modbus_tcp_group_box.isVisible() and self.modbus_rtu_group_box.isVisible()
        self.optional_tcp_custom_name_label.setVisible(status)
        self.optional_tcp_custom_name.setVisible(status)

    def update_slave_address_visibility(self):
        status = self.modbus_tcp_group_box.isVisible() and self.modbus_rtu_group_box.isVisible()
        self.global_slave_address_label.setVisible(status)
        self.global_slave_address.setVisible(status)
        
    def submit_user_input(self) -> dict:
        # Check which radio button is selected (Modbus TCP or Modbus RTU)
        if self.modbus_tcp_check_box.isChecked() and not self.modbus_rtu_check_box.isChecked(): 
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

        elif self.modbus_rtu_check_box.isChecked() and not self.modbus_tcp_check_box.isChecked():
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

        elif self.modbus_rtu_check_box.isChecked() and self.modbus_tcp_check_box.isChecked():
            temp_dict = {}
            tcp_client_dict = {}
            rtu_client_dict = {}

            device_name = self.optional_tcp_custom_name.text()
            slave_address = self.global_slave_address.text()

            rtu_client_dict[SERIAL_PORT] = self.modbus_rtu_group_box.com_ports.currentText()  # Get the selected COM Port
            rtu_client_dict[BAUD_RATE] = self.modbus_rtu_group_box.baud_rates.currentText()
            rtu_client_dict[PARITY] = self.modbus_rtu_group_box.parity_options.currentText()
            rtu_client_dict[STOP_BITS] = self.modbus_rtu_group_box.stop_bits_options.currentText()
            rtu_client_dict[BYTESIZE] = self.modbus_rtu_group_box.byte_size_options.currentText()
            rtu_client_dict[TIMEOUT] = self.modbus_rtu_group_box.timeout_options.currentText()

            tcp_client_dict[HOST] = self.modbus_tcp_group_box.ip_address.text()
            tcp_client_dict[PORT] = self.modbus_tcp_group_box.port.text()

            temp_dict = {SLAVE_ADDRESS: slave_address, DEVICE_NAME: device_name, DEFAULT_METHOD: {}, CONNECTION_PARAMETERS: {RTU_PARAMETERS: rtu_client_dict, TCP_PARAMETERS: tcp_client_dict}, REGISTERS:{}}
            temp_dict = {f'{DEVICE_PREFIX}{self.device_number}': temp_dict}

            self.file_handler.add_device(temp_dict)

        self.accept()


class EditConnection(QDialog):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()

        self.setWindowTitle("Connection Setup")
        self.setGeometry(100, 100, 500, 300)  # Set the initial size and position of the dialog

        # Create the main Vertical layout
        self.device_setup_main_layout = QVBoxLayout()

        rtu_groupbox = RtuGroupBox("Modbus RTU")
        tcp_groupbox = TcpGroupBox("Modbus TCP")

        # Create a QPushButton for the submit button
        self.submit_button = QPushButton("Submit", self)
        # self.submit_button.setVisible(False)
        # self.submit_button.clicked.connect(self.submit_user_input)

        self.device_setup_main_layout.addWidget(rtu_groupbox)
        self.device_setup_main_layout.addWidget(tcp_groupbox)
        self.device_setup_main_layout.addWidget(self.submit_button)

        # self.device_setup_main_layout.setSizeConstraint(QVBoxLayout.SetFixedSize)  # Set size constraint

        # Execute the dialog box
        self.setLayout(self.device_setup_main_layout)
