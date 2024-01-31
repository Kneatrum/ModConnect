from PyQt5.QtWidgets import QWidget,  QGroupBox, QWidget,  QPushButton, QTableWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout, QTableWidgetItem, QCheckBox
from file_handler import FileHandler
from modbus_clients import ModbusTCP, ModbusRTU
from constants import REGISTER_NAME, REGISTER_ADDRESS, REGISTER_PREFIX, TCP_METHOD, RTU_METHOD, \
                        HOST, PORT, SERIAL_PORT, BAUD_RATE, PARITY, STOP_BITS, BYTESIZE

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


    def __init__(self, device_number:int, columns = 3, ):
        super().__init__()

         
        self.file_handler = FileHandler()

        self.device_number = device_number
        self.columns = columns
        self.rows = self.file_handler.get_register_count(self.device_number)
        self.device_name = self.file_handler.get_device_name(self.device_number)
        self.slave_address = self.file_handler.get_slave_address(self.device_number)
        self.modbus_method_label = ""
        self.table_widget_default_attrs = [REGISTER_NAME, REGISTER_ADDRESS]
        self.connection_methods = self.get_available_connection_methods(self.device_number)
        self.connection_status = False
        self.selected_connection = None
        self.list_of_registers = self.get_register_addresses()

        self.modbus_connection_label = QLabel("")
        


        



        # Add a label for the register group or device group
        if not self.device_name:
            self.device_name = "Device " + str(self.device_number) # Create an initial name "Device " + the index of the register group. For example, Device 1
            

        # Create a QGroupBox
        group_box = QGroupBox(self.device_name, self)
        group_box.setMinimumWidth(450) # set minimum width
        group_box.setMaximumWidth(450) # set maximum width


        # Create the actions Qlabel
        self.actions_label = QLabel("Actions",self)


        # Create the connection status Qlabel
        self.connection_status_label = QLabel("Disconnected",self)
        self.connection_status_label.setStyleSheet("background-color: rgb(212, 212, 212); padding: 25px;")
        self.connection_status_label.setFixedHeight(30)
                
        # Set the object name of the connection status label
        self.connection_status_label.setObjectName("connection_status_label_device_" + str(self.device_number))


        check_box_h_layout = QHBoxLayout()
        self.tcp_checkbox = QCheckBox('TCP')
        self.rtu_checkbox = QCheckBox('RTU')
        self.tcp_checkbox.stateChanged.connect(self.on_tcp_box_status_changed)
        self.rtu_checkbox.stateChanged.connect(self.on_rtu_box_status_changed)
        check_box_h_layout.addWidget(self.tcp_checkbox)
        check_box_h_layout.addWidget(self.rtu_checkbox)
        

        # Create the connection status Qlabel
        # self.modbus_connection_label = QLabel(self.modbus_method_label)
        self.modbus_method_label = self.create_modbus_connection_label()
        self.modbus_connection_label.setText(self.modbus_method_label)

        self.edit_connection_button = QPushButton('Edit Connection')
        self.edit_connection_button.clicked.connect(self.on_edit_connection_button_clicked)


        # Add a dropdown menu and add actions to it
        self.action_items = ["Select an action","Add Registers", "Remove register", "Connect", "Quit"] # Create a list of actions
        self.action_menu = QComboBox() 
        self.action_menu.addItems(self.action_items) 
        self.action_menu.setCurrentIndex(0)
        self.action_menu.setFixedWidth(150)
        view = self.action_menu.view() # Get the view of the combo box
        view.setRowHidden(0, True) # Hide the first row of the combo box view
        self.action_menu.currentIndexChanged.connect(self.on_drop_down_menu_current_index_changed) # Trigger an action when the user selects an option


        # Create a table to display the registers
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(self.rows)
        self.table_widget.setColumnCount(self.columns)
        self.table_widget.setHorizontalHeaderLabels(list(TABLE_HEADER.keys()))
        self.table_widget.setColumnWidth(NAME_COLUMN, 200) # Set the width of the "Register Name" column to 200
        self.table_widget.setColumnWidth(ADDRESS_COLUMN, 100) # Set the width of the "Address" column to 100
        self.table_widget.setColumnWidth(VALUE_COLUMN, 100) # Set the width of the "Value" column to 100
        self.table_widget.itemChanged.connect(self.onItemChanged)
        #table_widget.setFixedWidth(table_widget.horizontalHeader().length()) # Set the maximum width of the qtable widget to the width of the 3 columnns we have ( "Register Name", "Address", "Value" )

        
        # Create a horizontal layout to hold action label and combo box vlayouy and connection status label
        top_horizontal_layout = QHBoxLayout()
        first_column = QVBoxLayout()
        second_column = QVBoxLayout()
        third_column = QVBoxLayout()
        



        # Create a horizontal layout to hold the connection status
        con_status_v_layout = QVBoxLayout()
        con_status_v_layout.addWidget(self.connection_status_label)

        
        connection_v_layout = QVBoxLayout()
        connection_v_layout.addWidget(self.modbus_connection_label)
        connection_v_layout.addWidget(self.edit_connection_button)

        # Create a vertical box layout for the qlabel and combo box
        action_status_combo_box_v_layout = QVBoxLayout() 
        action_status_combo_box_v_layout.addWidget(self.actions_label) # Add the action label to the layout
        action_status_combo_box_v_layout.addWidget(self.action_menu) # Add the action dropdown menu to the layout


        first_column.addLayout(check_box_h_layout)
        first_column.addLayout(con_status_v_layout)
        second_column.addLayout(connection_v_layout)
        third_column.addLayout(action_status_combo_box_v_layout)



        top_horizontal_layout.addLayout(first_column)
        top_horizontal_layout.addLayout(second_column)
        top_horizontal_layout.addLayout(third_column)
        

        
        
        # Create a vertical layout to hold the buttons and the table widget
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_horizontal_layout)
        main_layout.addWidget(self.table_widget)

        # Add the button and table widget to the group box
        group_box.setLayout(main_layout)

        # Set the layout for the main QWidget
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)
        self.update_register_table()


    def onItemChanged(self, item):
        row = item.row()
        col = item.column()
        text = item.text()
        # print(f"Cell ({row}, {col}) changed to {text}")
        if item.column() == 0:
            # interface.update_register_name(self.device,row,text)
            pass


    def on_rtu_box_status_changed(self):
        if self.rtu_checkbox.isChecked():
            self.tcp_checkbox.setChecked(False)
            self.file_handler.set_default_modbus_method(self.device_number, RTU_METHOD)
            result = self.file_handler.get_connection_params(self.device_number)
            modbus_protocols = self.file_handler.get_modbus_protocol(self.device_number)
            if RTU_METHOD in modbus_protocols:
                self.modbus_method_label = f'Modbus RTU\n{PORT.upper()}: {result[RTU_METHOD].get(SERIAL_PORT)}\n{BAUD_RATE.upper()}: {result[RTU_METHOD].get(BAUD_RATE)}\n{result[RTU_METHOD].get(BYTESIZE)}, {result[RTU_METHOD].get(PARITY)}, {result[RTU_METHOD].get(STOP_BITS)}'
                self.modbus_connection_label.setText(self.modbus_method_label)
                # self.modbus_connection_label.setText("Nyenye")

        

    def on_tcp_box_status_changed(self):
        if self.tcp_checkbox.isChecked():
                self.rtu_checkbox.setChecked(False)
                self.file_handler.set_default_modbus_method(self.device_number, TCP_METHOD)
                result = self.file_handler.get_connection_params(self.device_number)
                modbus_protocols = self.file_handler.get_modbus_protocol(self.device_number)
                if TCP_METHOD in modbus_protocols:
                    self.modbus_method_label = f'Modbus TCP\n{HOST.upper()}: {result[TCP_METHOD].get(HOST)}\n{PORT.upper()}: {result[TCP_METHOD].get(PORT)}'
                    self.modbus_connection_label.setText(self.modbus_method_label)
                    # self.modbus_connection_label.setText("Nyenye")

        

    def on_edit_connection_button_clicked(self):
        pass
   

    def on_drop_down_menu_current_index_changed(self):
        
        if self.action_menu.currentIndex() == 1: # If the selectec option is Add registers (index 1)
            self.table_widget.itemChanged.disconnect(self.onItemChanged) # Disconnect the ItemChanged signal to alow us to reload the GUI
            self.show_register_dialog() # Show the message box for adding registers
            self.action_menu.setCurrentIndex(0)
            self.table_widget.itemChanged.connect(self.onItemChanged)    # Reconnect the ItemChanged signal to allow us to update the register names
        elif self.action_menu.currentIndex() == 2: # If the selectec option is Delete registers (index 2)
            self.action_menu.setCurrentIndex(0)
            if self.selected_connection:
                print(f"Is device connected? :{self.selected_connection.is_connected()}")
            else:
                print("No device connected")
        elif self.action_menu.currentIndex() == 3: # If the selected option is Connect (index 3)
            self.action_menu.setCurrentIndex(0)
            if self.connect_to_device():
                light_green = "rgb(144, 238, 144)"
                self.set_conection_status("Connected",light_green)
            



    def set_conection_status(self,text,background_color):
        self.connection_status_label.setText(text)
        self.connection_status_label.setStyleSheet("background-color: " + background_color + "; padding: 25px;")


    def create_modbus_connection_label(self) -> str:
        """
        This method creates a string that shows the connection parameters used for the specific modbus connection.

        argument: 
            None

        return:
            label (str): A string that shows the connection parameters.

        TCP Example:
            HOST: 192.168.0.1
            PORT: 502

        RTU Example:
            PORT: COM1
            BAUDRATE: 19200
            8, N, 1
        """
        label = ""
        result = self.file_handler.get_connection_params(self.device_number)
        modbus_protocols = self.file_handler.get_modbus_protocol(self.device_number)
        if len(modbus_protocols) > 1:
            default_method = self.file_handler.get_default_modbus_method(self.device_number)
            if not default_method:
                # Set the default method to TCP if it is not set.
                self.file_handler.set_default_modbus_method(self.device_number, TCP_METHOD)
                default_method = TCP_METHOD
                label = f'Modbus TCP\n{HOST.upper()}: {result[TCP_METHOD].get(HOST)}\n{PORT.upper()}: {result[TCP_METHOD].get(PORT)}'
                self.tcp_checkbox.setChecked(True)
            else:
                if default_method == TCP_METHOD:
                    label = f'Modbus TCP\n{HOST.upper()}: {result[TCP_METHOD].get(HOST)}\n{PORT.upper()}: {result[TCP_METHOD].get(PORT)}'
                    self.tcp_checkbox.setChecked(True)
                elif default_method == RTU_METHOD:
                    label = f'Modbus RTU\n{PORT.upper()}: {result[RTU_METHOD].get(SERIAL_PORT)}\n{BAUD_RATE.upper()}: {result[RTU_METHOD].get(BAUD_RATE)}\n{result[RTU_METHOD].get(BYTESIZE)}, {result[RTU_METHOD].get(PARITY)}, {result[RTU_METHOD].get(STOP_BITS)}'
                    self.rtu_checkbox.setChecked(True)
        elif len(modbus_protocols) == 1:
            if TCP_METHOD in modbus_protocols:
                label = f'Modbus TCP\n{HOST.upper()}: {result[TCP_METHOD].get(HOST)}\n{PORT.upper()}: {result[TCP_METHOD].get(PORT)}'
                self.tcp_checkbox.setChecked(True)
                self.tcp_checkbox.setDisabled(True)
                self.rtu_checkbox.setDisabled(True)
            elif RTU_METHOD in modbus_protocols:
                label = f'Modbus RTU\n{PORT.upper()}: {result[RTU_METHOD].get(SERIAL_PORT)}\n{BAUD_RATE.upper()}: {result[RTU_METHOD].get(BAUD_RATE)}\n{result[RTU_METHOD].get(BYTESIZE)}, {result[RTU_METHOD].get(PARITY)}, {result[RTU_METHOD].get(STOP_BITS)}'
                self.rtu_checkbox.setChecked(True)
                self.rtu_checkbox.setDisabled(True)
                self.tcp_checkbox.setDisabled(True)
        return label
        

    



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
        self.table_widget.setRowCount(0)
        for index in range(len(results)):
            self.table_widget.insertRow(index)
            self.table_widget.setItem(index, NAME_COLUMN, QTableWidgetItem(results[REGISTER_PREFIX + str(index + 1)][REGISTER_NAME]))
            self.table_widget.setItem(index, ADDRESS_COLUMN, QTableWidgetItem(str(results[REGISTER_PREFIX + str(index + 1)][REGISTER_ADDRESS]))) # Convert address to a string for it to be displayed.


    def get_available_connection_methods(self, device_number):
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

        If more than one client is registered, the user is prompted to select one of the clients.
        """
        if len(self.clients) > 1:
            #TODO: Implement the below functionality
            print("Prompt user to select their prefered device")

            #Meanwhile, connect to the TCP  by default
            if self.selected_connection is not None:
                print("A device is already connected")
                return False
            self.selected_connection = self.clients.get(TCP_METHOD)
            if self.selected_connection:
                if self.selected_connection.client.connect():
                    return True
        else:
            if RTU_METHOD in self.clients:
                if self.selected_connection is not None:
                    print("A device is already connected")
                    return False
                self.selected_connection = self.clients.get(RTU_METHOD)
                if self.selected_connection:
                    if self.selected_connection.client.connect():
                        return True
            elif TCP_METHOD in self.clients:
                if self.selected_connection is not None:
                    print("A device is already connected")
                    return False
                self.selected_connection = self.clients.get(TCP_METHOD)
                if self.selected_connection:
                    if self.selected_connection.client.connect():
                        return True
        return False

    def get_register_addresses(self):
        temp_list = [REGISTER_ADDRESS]
        result = self.file_handler.get_register_attributes(self.device_number, temp_list)
        addresses = [register_info['address'] for register_info in result.values()]  
        return addresses     


    def delete_register(self):
        print("Delete register")
        pass

    def delete_device(self):
        print("Delete register")
        pass