from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget,  QGroupBox, QWidget,  QPushButton, QTableWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout, QTableWidgetItem, QCheckBox, QSpacerItem, QSizePolicy
from file_handler import FileHandler
from modbus_clients import ModbusTCP, ModbusRTU
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.exceptions import ModbusIOException
from modbus_group_boxes import RtuGroupBox, TcpGroupBox
from constants import REGISTER_NAME, REGISTER_ADDRESS, REGISTER_PREFIX, TCP_METHOD, RTU_METHOD, \
                        HOST, PORT, SERIAL_PORT, BAUD_RATE, PARITY, STOP_BITS, BYTESIZE, \
                        FUNCTION_CODE, REGISTER_QUANTITY

from notifications import Notification

NAME_COLUMN = 0
ADDRESS_COLUMN = 1
VALUE_COLUMN = 2

TABLE_HEADER = {"Register Name": NAME_COLUMN, "Address": ADDRESS_COLUMN, "Value": VALUE_COLUMN}

class TableWidget(QWidget):

    REGISTER_PROPERTIES = {
        'register_name': "", 
        'address': 0,
        'function_code': 1,
        'units': "",
        'gain': 1,
        'data_type': "",
        'access_type': "",
    }

    READ_FUNCTION_CODES = {
        "READ_COILS (01)": 1,
        "READ_DISCRETE_INPUTS (02)": 2,
        "READ_HOLDING_REGISTERS (03)": 3,
        "READ_INPUT_REGISTERS (04)": 4
    }

    WRITE_FUNCTION_CODES = {
        "WRITE_SINGLE_COIL (05)": 5,
        "WRITE_SINGLE_REGISTER (06)": 6,
        "WRITE_MULTIPLE_COILS (15)": 15,
        "WRITE_MULTIPLE_REGISTERS (16)": 16
    }
    
    edit_connection_button_clicked = pyqtSignal(int)
    drop_down_menu_clicked = pyqtSignal(int, int)

    def __init__(self, device_number:int, columns = 3):
        super().__init__()

         
        self.file_handler = FileHandler()
        self.notification = Notification()

        self.device_number = device_number
        self.columns = columns
        self.rows = self.file_handler.get_register_count(self.device_number)
        self.device_name = self.file_handler.get_device_name(self.device_number)
        self.slave_address = self.file_handler.get_slave_address(self.device_number)
        self.modbus_method_label = ""
        self.table_widget_default_attrs = [REGISTER_NAME, REGISTER_ADDRESS]
        self.connection_methods = self.__get_available_connection_methods(self.device_number)
        self.connection_status = False
        self.set_default_modbus_method_if_not_set()
        self.selected_connection = self.__set_selected_connection()
        self.list_of_registers = self.file_handler.get_registers_to_read(self.device_number)

        self.register_data = []

        self.modbus_connection_label = QLabel("")
        # Add a label for the register group or device group
        if not self.device_name:
            self.device_name = "Device " + str(self.device_number) # Create an initial name "Device " + the index of the register group. For example, Device 1
            

        # Create a QGroupBox
        self.group_box = QGroupBox(self.device_name, self)
        self.group_box.setMinimumWidth(505) # set minimum width
        self.group_box.setMaximumWidth(505) # set maximum width




        # Create the connection status Qlabel
        self.connection_status_label = QLabel("Disconnected",self)
        self.connection_status_label.setStyleSheet("background-color: rgb(212, 212, 212); padding: 25px;")
        self.connection_status_label.setFixedSize(150, 30)
                
        # Set the object name of the connection status label
        self.connection_status_label.setObjectName("connection_status_label_device_" + str(self.device_number))


        check_box_h_layout = QHBoxLayout()
        self.tcp_checkbox = QCheckBox('TCP')
        self.rtu_checkbox = QCheckBox('RTU')
        checkbox_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.tcp_checkbox.stateChanged.connect(self.on_tcp_connection_status_changed)
        self.rtu_checkbox.stateChanged.connect(self.on_rtu_connection_status_changed)
        check_box_h_layout.addWidget(self.tcp_checkbox)
        check_box_h_layout.addItem(checkbox_spacer)
        check_box_h_layout.addWidget(self.rtu_checkbox)
        

        # Create the connection status Qlabel
        # self.modbus_connection_label = QLabel(self.modbus_method_label)
        connection_params = self.file_handler.get_connection_params(self.device_number)
        default_method = self.file_handler.get_default_modbus_method(self.device_number)
        modbus_protocols = self.file_handler.get_modbus_protocol(self.device_number)
        
        if default_method == TCP_METHOD:
            # Constructing the following string. 127.0.0.1:502 
            self.modbus_method_label = self.get_tcp_connection_string(connection_params)
            self.tcp_checkbox.setChecked(True)
        elif default_method == RTU_METHOD:
            # Constructing the following string. 9600,COM1,N,1,8,1.0
            self.modbus_method_label  = self.get_rtu_connection_string(connection_params)
            self.rtu_checkbox.setChecked(True)

        # If there is only one option, disable the checkboxes
        if not modbus_protocols or  len(modbus_protocols) == 1:
            self.rtu_checkbox.setDisabled(True)
            self.tcp_checkbox.setDisabled(True)
         
        self.modbus_connection_label.setText(self.modbus_method_label)
        self.modbus_connection_label.setStyleSheet("Color: gray;")

        self.edit_connection_button = QPushButton('...')
        self.edit_connection_button.setFixedSize(30, 30)
        self.edit_connection_button.clicked.connect(lambda checked, idx=self.device_number: self.on_edit_connection_button_clicked(idx))


        # Create a vertical box layout for the qlabel and combo box
        action_status_combo_box_h_layout = QHBoxLayout() 
        # Create the actions Qlabel
        self.actions_label = QLabel("Actions",self)
        self.selected_option = 0
        # Add a dropdown menu and add actions to it
        self.action_items = ["Select an action","Add Registers", "Remove register", "Connect", "Quit"] # Create a list of actions
        self.action_menu = QComboBox() 
        self.action_menu.addItems(self.action_items) 
        self.action_menu.setCurrentIndex(0)
        self.action_menu.setFixedSize(150, 30)
        view = self.action_menu.view() # Get the view of the combo box
        view.setRowHidden(0, True) # Hide the first row of the combo box view
        self.action_menu.currentIndexChanged.connect(lambda position=self.selected_option, device_number=self.device_number:self.__on_drop_down_menu_current_index_changed(device_number, position)) # Trigger an action when the user selects an option
        action_status_combo_box_h_layout.addWidget(self.actions_label) # Add the action label to the layout
        action_status_combo_box_h_layout.addWidget(self.action_menu) # Add the action dropdown menu to the layout


        # Create a table to display the registers
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(self.rows)
        self.table_widget.setColumnCount(self.columns)
        self.table_widget.setHorizontalHeaderLabels(list(TABLE_HEADER.keys()))
        self.table_widget.setColumnWidth(NAME_COLUMN, 200) # Set the width of the "Register Name" column to 200
        self.table_widget.setColumnWidth(ADDRESS_COLUMN, 120) # Set the width of the "Address" column to 100
        self.table_widget.setColumnWidth(VALUE_COLUMN, 120) # Set the width of the "Value" column to 100
        self.table_widget.cellChanged.connect(self.on_cell_changed)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        
        # Create a horizontal layout to hold action label and combo box vlayouy and connection status label
        self.left_group_box = QGroupBox()
        self.center_group_box = QGroupBox()
        self.right_group_box = QGroupBox()
        first_column = QVBoxLayout()
        second_column = QVBoxLayout()
        

        # Create a horizontal layout to hold the connection status
        con_status_h_layout = QHBoxLayout()
        status_label = QLabel("Status")
        con_status_h_layout.addWidget(status_label)
        con_status_h_layout.addWidget(self.connection_status_label)

        
        connection_h_layout = QHBoxLayout()
        connection_h_layout.addWidget(self.modbus_connection_label)
        connection_h_layout.addWidget(self.edit_connection_button)

        

        first_column.addLayout(check_box_h_layout)
        first_column.addLayout(connection_h_layout)
        second_column.addLayout(con_status_h_layout)
        second_column.addLayout(action_status_combo_box_h_layout)

        self.left_group_box.setLayout(first_column)
        self.right_group_box.setLayout(second_column)
       
        # Create a vertical layout to hold the buttons and the table widget
        group_box_internal_layout = QVBoxLayout()
        top_horizontal_layout = QHBoxLayout()
        bottom_vertical_layout = QVBoxLayout()

        top_horizontal_layout.addWidget(self.left_group_box)
        top_horizontal_layout.addWidget(self.right_group_box)
        bottom_vertical_layout.addWidget(self.table_widget)

        group_box_internal_layout.addLayout(top_horizontal_layout)
        group_box_internal_layout.addLayout(bottom_vertical_layout)

        # Add the button and table widget to the group box
        self.group_box.setLayout(group_box_internal_layout)
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.group_box)

        self.setLayout(main_layout)
        self.update_register_table()


    def on_cell_changed(self, row, column):
        """
        This method allows the user to assign a custom name to a register.
        """
        new_register_name = self.table_widget.item(row, column)
        register_address = self.table_widget.item(row, column + 1) # column + 1 is the address column
        if new_register_name and register_address  and column == NAME_COLUMN:
            if self.file_handler.update_register_name(self.device_number, register_address.text(), new_register_name.text()):
                print(f"Updated register name to : {new_register_name.text()}")
            else:
                print(f"Failed to update register name")
        

    def on_tcp_connection_status_changed(self):
        if self.tcp_checkbox.isChecked():
            if self.rtu_checkbox.isChecked():
                self.rtu_checkbox.setChecked(False)
                self.file_handler.set_default_modbus_method(self.device_number, TCP_METHOD)
                print(f"Connection status changed")
                self.update_method_label()


    def on_rtu_connection_status_changed(self):
        if self.rtu_checkbox.isChecked():
            if self.tcp_checkbox.isChecked():
                self.tcp_checkbox.setChecked(False)
                self.file_handler.set_default_modbus_method(self.device_number, RTU_METHOD)
                self.update_method_label()
                    

    def update_method_label(self):
        connection_params = self.file_handler.get_connection_params(self.device_number)
        default_method = self.file_handler.get_default_modbus_method(self.device_number)
        if TCP_METHOD in default_method:
            message = self.get_tcp_connection_string(connection_params)
            self.modbus_connection_label.setText(message)
            self.modbus_connection_label.setStyleSheet("color: gray;")
        if RTU_METHOD in default_method:
            message = self.get_rtu_connection_string(connection_params)
            self.modbus_connection_label.setText(message)
            self.modbus_connection_label.setStyleSheet("color: gray;")


    def update_device_name(self):
        device_name = self.file_handler.get_device_name(self.device_number)
        self.group_box.setTitle(device_name)


    def on_edit_connection_button_clicked(self, index):
        self.edit_connection_button_clicked.emit(index)
   

    def __on_drop_down_menu_current_index_changed(self, device_number, position):
        current_index = self.action_menu.currentIndex()
        if current_index == 1: # If the selectec option is Add registers (index 1)
            position = current_index
            self.action_menu.setCurrentIndex(0)
            self.drop_down_menu_clicked.emit(device_number, position)
        elif current_index == 2: # If the selectec option is Delete registers (index 2)
            position = current_index
            self.action_menu.setCurrentIndex(0)
            self.drop_down_menu_clicked.emit(device_number, position)
        elif current_index == 3: # If the selected option is Connect (index 3)
            position = current_index
            self.action_menu.setCurrentIndex(0)
            self.drop_down_menu_clicked.emit(device_number, position)
            



    def set_conection_status(self,text,background_color):
        self.connection_status_label.setText(text)
        self.connection_status_label.setStyleSheet("background-color: " + background_color + "; padding: 25px;")



        
    def set_default_modbus_method_if_not_set(self):
        """
            This function checks whether a default modbus method has been set

            and sets it if it has not been set.

            arguments: 
                None
            returns: 
                None
        """
        modbus_protocols = self.file_handler.get_modbus_protocol(self.device_number)
        if not modbus_protocols:
            print("No Modbus protocols found")
            return None
        
        if len(modbus_protocols) > 1:
            default_method = self.file_handler.get_default_modbus_method(self.device_number)
            if not default_method:
                # Set the default method to TCP if it is not set.
                self.file_handler.set_default_modbus_method(self.device_number, TCP_METHOD)
        elif len(modbus_protocols) == 1:
            if TCP_METHOD in modbus_protocols:
                self.file_handler.set_default_modbus_method(self.device_number, TCP_METHOD)
            elif RTU_METHOD in modbus_protocols:
                self.file_handler.set_default_modbus_method(self.device_number, RTU_METHOD)
    



    def show_register_dialog(self):
        self.register_setup_dialog = QDialog(self)
        self.register_setup_dialog.setWindowTitle("Register Setup")

        # # Create the main Vertical layout
        rset_main_layout = QVBoxLayout()


        # Create a vertical layout and add a dropdown list of the function codes
        r_set_v_layout_1 = QVBoxLayout()
        self.fx_code_label = QLabel("Function Code")
        r_set_v_layout_1.addWidget(self.fx_code_label) # Add the label to the vertical layout

        self.fx_code_items = list(self.READ_FUNCTION_CODES.keys())  # Create a list of function codes
        self.function_code = QComboBox() # Create a drop down list of function codes
        self.function_code.addItems(self.fx_code_items) # Add function codes to the dropdown list
        r_set_v_layout_1.addWidget(self.function_code) # Add function code items to widget

        # Create a horizontal layout for Register address label and its edit box
        r_set_h_layout_2 = QHBoxLayout()
        self.reg_address_label =  QLabel("Register Address")
        self.reg_address = QLineEdit(self)
        r_set_h_layout_2.addWidget(self.reg_address_label)
        r_set_h_layout_2.addWidget(self.reg_address)

        # Create a horizontal layout for Register quantity and its edit box
        r_set_h_layout_3 = QHBoxLayout(self)
        self.reg_quantity_label = QLabel("Quantity")
        self.reg_quantity = QLineEdit(self)
        r_set_h_layout_3.addWidget(self.reg_quantity_label)
        r_set_h_layout_3.addWidget(self.reg_quantity)
        
        # Create a button to submit the register setup
        r_set_h_layout_4 = QHBoxLayout(self)
        self.rset_submit_button = QPushButton("Submit")
        r_set_h_layout_4.addWidget(self.rset_submit_button)
        self.rset_submit_button.clicked.connect(self.on_button_clicked)
        # self.register_setup_dialog.accept()

        # Add all the layouts to the main vertical layout
        # rset_main_layout.addLayout(r_set_h_layout_1)
        rset_main_layout.addLayout(r_set_v_layout_1)
        rset_main_layout.addLayout(r_set_h_layout_2)
        rset_main_layout.addLayout(r_set_h_layout_3)
        rset_main_layout.addLayout(r_set_h_layout_4) 
        self.register_setup_dialog.setLayout(rset_main_layout)
        self.register_setup_dialog.exec_() 


    def on_button_clicked(self):
        user_input = self.get_user_input()
        self.file_handler.update_register_details(self.device_number, user_input)
        self.update_register_table()
        self.register_setup_dialog.accept()
        self.table_widget.update()


        # This function gets the user input values and the default values from the constructor function and sends them to interface.py
    def get_user_input(self) -> dict:
        user_input = {} # An empty dictionary to store user input
        self.REGISTER_PROPERTIES['address'] = int(self.reg_address.text())
        self.REGISTER_PROPERTIES['function_code'] = self.READ_FUNCTION_CODES[self.function_code.currentText()]

        self.register_quantity = self.reg_quantity.text()
        user_input["device"] = self.device_number
        user_input['quantity'] = self.register_quantity
        user_input["registers"] = self.REGISTER_PROPERTIES
        return user_input

        
        # self.update_register_table(self.reg_address.text(),self.reg_quantity.text())
        



    def update_register_table(self):
        """
        This method updates the register table widget with 
        the defaul attributes which are:

        Register name: This is the first column of the table widget.
        Register address: This is the second column of the table widget.

        The attributes are passed in form of a list.
        """
        results = self.file_handler.get_register_attributes(self.device_number, self.table_widget_default_attrs)
        if results:
            self.table_widget.setRowCount(0)
            for index in range(len(results)):
                self.table_widget.insertRow(index)
                self.table_widget.setItem(index, NAME_COLUMN, QTableWidgetItem(results[REGISTER_PREFIX + str(index + 1)][REGISTER_NAME]))
                self.table_widget.setItem(index, ADDRESS_COLUMN, QTableWidgetItem(str(results[REGISTER_PREFIX + str(index + 1)][REGISTER_ADDRESS]))) # Convert address to a string for it to be displayed.


    def update_register_data(self):
        for row, data in enumerate(self.register_data):
            self.table_widget.setItem(row, VALUE_COLUMN, QTableWidgetItem(str(data)))
        self.table_widget.viewport().update()



    def __get_available_connection_methods(self, device_number):
        """
        This method returns a dictionary of available connection methods.

        arguments: 
            device_number

        return: 
            dictionary of available connection
        """
        temp_dict = {}
        rtu_connection = ModbusRTU(device_number)
        if rtu_connection.client:
            temp_dict[RTU_METHOD] = rtu_connection

        tcp_connection = ModbusTCP(device_number)
        if tcp_connection.client:
            temp_dict[TCP_METHOD] = tcp_connection

        return temp_dict


    def connect_to_device(self) -> bool:
        """
        This method connects to the client registered with the table widget.

        arguments:
            None
        returns:
            bool: True if connected successfully or False otherwise
        """
        try:
            if self.selected_connection.client.connect():
                return True
        except Exception as e:
            return e

     


    def __set_selected_connection(self):
        """
        This method checks for the default modbus connection and sets the appropriate connection method

        which can be either TCP or RTU

        arguments:
            None

        returns:
            modbus_object (object): An instance of either Modbus RTU or Modbus TCP
        """
        modbus_object = None
        result = self.file_handler.get_default_modbus_method(self.device_number)
        if result == TCP_METHOD:
            modbus_object = ModbusTCP(self.device_number)
        elif result == RTU_METHOD:
            modbus_object = ModbusRTU(self.device_number)
        else:
            print("Default method has not been set")
            return None
        return modbus_object
    

    def read_registers(self):
        self.register_data.clear()
        for register in self.list_of_registers:
            if self.list_of_registers[register][FUNCTION_CODE]  == 1:
                address = self.list_of_registers[register].get(REGISTER_ADDRESS)
                quantity = self.list_of_registers[register].get(REGISTER_QUANTITY)
                if address is not None or address == 0:
                    try:
                        response = self.selected_connection.client.read_coils(address, quantity, unit=self.slave_address)
                        if response.isError():
                            self.register_data.append("Error")
                            print(response)
                        else:
                            self.register_data += response.registers
                    except ModbusIOException as e:
                        self.register_data.append(e)
                        return None
            elif self.list_of_registers[register][FUNCTION_CODE] == 2:
                address = self.list_of_registers[register].get(REGISTER_ADDRESS)
                quantity = self.list_of_registers[register].get(REGISTER_QUANTITY)
                if address is not None or address == 0:
                    try:
                        response = self.selected_connection.client.read_discrete_inputs(address, quantity, unit=self.slave_address)
                        if response.isError():
                            self.register_data.append("Error")
                            print(response)
                        else:
                            self.register_data += response.registers
                    except ModbusIOException as exception:
                        self.register_data.append("Comm Error")
                        return None
            elif self.list_of_registers[register][FUNCTION_CODE] == 3:
                address = self.list_of_registers[register].get(REGISTER_ADDRESS)
                quantity = self.list_of_registers[register].get(REGISTER_QUANTITY)
                if address is not None or address == 0:
                    try:
                        response = self.selected_connection.client.read_holding_registers(address, quantity, unit=self.slave_address)
                        if response.isError():
                            self.register_data.append("Error")
                            print(response)
                        else:
                            self.register_data += response.registers
                    except ModbusIOException as exception:
                        self.register_data.append("Comm Error")
                        return None
            elif self.list_of_registers[register][FUNCTION_CODE] == 4:
                address = self.list_of_registers[register].get(REGISTER_ADDRESS)
                quantity = self.list_of_registers[register].get(REGISTER_QUANTITY)
                if address is not None or address == 0:
                    try:
                        response = self.selected_connection.client.read_input_registers(address, quantity, unit=self.slave_address)
                        if response.isError():
                            self.register_data.append("Error")
                            print(response)
                        else:   
                            self.register_data += response.registers
                    except ModbusIOException as exception:
                        self.register_data.append("Comm Error")
                        return None
        return self.register_data
    
    def get_tcp_connection_string(self, connection_params):
        return f'{connection_params[TCP_METHOD].get(HOST)}:{connection_params[TCP_METHOD].get(PORT)}'

    def get_rtu_connection_string(self, connection_params):
        return f'{connection_params[RTU_METHOD].get(BAUD_RATE)}, '\
            f'{connection_params[RTU_METHOD].get(SERIAL_PORT)}, '\
            f'{connection_params[RTU_METHOD].get(BYTESIZE)}, '\
            f'{connection_params[RTU_METHOD].get(PARITY)[0]}, '\
            f'{connection_params[RTU_METHOD].get(STOP_BITS)}'


    def delete_register(self):
        print("Delete register")
        pass

    def delete_device(self):
        print("Delete register")
        pass