from PyQt5.QtWidgets import QWidget,  QGroupBox, QWidget,  QPushButton, QTableWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout
from file_handler import FileHandler as fh

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


    def __init__(self, device_number, columns = 3, ):
        super().__init__()

        self.device_number = device_number
        self.columns = columns
        self.rows = fh.get_register_count(self.device_number)
        self.device_name = fh.get_device_name(self.device_number)
        self.slave_address = fh.get_slave_address(self.device_number)
        self.device_protocols = fh.get_modbus_protocol(self.device_name)

        self.connection_status = False

        



        # Add a label for the register group or device group
        label_name = "Device " + str(self.device_number) # Create an initial name "Device " + the index of the register group. For example, Device 1

        # Create a QGroupBox
        group_box = QGroupBox(label_name, self)
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
        

        # Create a horizontal layout to hold the connection status
        con_status_h_layout = QHBoxLayout()
        con_status_h_layout.addWidget(self.connection_status_label)


        # Create a vertical box layout for the qlabel and combo box
        action_status_combo_box_v_layout = QVBoxLayout() 
        action_status_combo_box_v_layout.addSpacing(10)
        action_status_combo_box_v_layout.addWidget(self.actions_label) # Add the action label to the layout
        action_status_combo_box_v_layout.addWidget(self.action_menu) # Add the action dropdown menu to the layout
        action_status_combo_box_v_layout.addSpacing(20)

        top_horizontal_layout.addLayout(action_status_combo_box_v_layout)
        top_horizontal_layout.addSpacing(200)
        top_horizontal_layout.addLayout(con_status_h_layout)

        


        

        
        
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


    def onItemChanged(self, item):
        row = item.row()
        col = item.column()
        text = item.text()
        # print(f"Cell ({row}, {col}) changed to {text}")
        if item.column() == 0:
            # interface.update_register_name(self.device,row,text)
            pass


   

    def on_drop_down_menu_current_index_changed(self):
        
        if self.action_menu.currentIndex() == 1: # If the selectec option is Add registers (index 1)
            self.table_widget.itemChanged.disconnect(self.onItemChanged) # Disconnect the ItemChanged signal to alow us to reload the GUI
            self.add_registers() # Show the message box for adding registers
            self.action_menu.setCurrentIndex(0)
            self.table_widget.itemChanged.connect(self.onItemChanged)    # Reconnect the ItemChanged signal to allow us to update the register names
        elif self.action_menu.currentIndex() == 2: # If the selectec option is Delete registers (index 2)
            self.action_menu.setCurrentIndex(0)
        elif self.action_menu.currentIndex() == 3: # If the selected option is Connect (index 3)
            self.action_menu.setCurrentIndex(0)
            if self.connect_to_device(self.device):
                light_green = "rgb(144, 238, 144)"
                self.set_conection_status("Connected",light_green)
            



    def set_conection_status(self,text,background_color):
        self.connection_status_label.setText(text)
        self.connection_status_label.setStyleSheet("background-color: " + background_color + "; padding: 25px;")
        

    



    def add_register_data(self):
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
        self.rset_submit_button.clicked.connect(self.get_user_input)
        self.register_setup_dialog.accept()

        # Add all the layouts to the main vertical layout
        # rset_main_layout.addLayout(r_set_h_layout_1)
        rset_main_layout.addLayout(r_set_v_layout_1)
        rset_main_layout.addLayout(r_set_h_layout_2)
        rset_main_layout.addLayout(r_set_h_layout_3)
        rset_main_layout.addLayout(r_set_h_layout_4) 
        self.register_setup_dialog.setLayout(rset_main_layout)
        self.register_setup_dialog.exec_() 



        # This function gets the user input values and the default values from the constructor function and sends them to interface.py
    def get_user_input(self):
       
        user_input = {} # An empty dictionary to store user input
        self.REGISTER_PROPERTIES['address'] = int(self.reg_address.text())
        self.REGISTER_PROPERTIES['function_code'] = self.READ_FUNCTION_CODES[self.function_code.currentText()]

        self.register_quantity = self.reg_quantity.text()
        user_input["device"] = self.device_number
        user_input['quantity'] = self.register_quantity
        user_input["registers"] = self.REGISTER_PROPERTIES

        #interface.generate_setup_file(user_input)
        fh.save_register_data(user_input)
        # self.update_register_table(self.reg_address.text(),self.reg_quantity.text())
        self.update_register_table()
        self.table_widget.update()



    def update_register_table(self):
        """
        The below method returns a dictionary with a list of name and value
        Example: register_1: [name, value]
        To extract the name -> register_1[0]
        To extract the value -> register_1[1]
        """
        results = fh.get_register_names_and_addresses(self.device_number)
        for index, register in enumerate(results):
            self.table_widget.setItem(index, NAME_COLUMN, register[0])
            self.table_widget.setItem(index, ADDRESS_COLUMN, register[1])



    def connect_to_device(self,device) -> bool:
        # print("Connect to device",device)
        # if interface.connect_to_client(device):
        #     print("#####Success")
        #     return True
        # else:
        #     print("#####Failure")
        #     return False
        pass

        


    def delete_register(self):
        print("Delete register")
        pass

    def delete_device(self):
        print("Delete register")
        pass