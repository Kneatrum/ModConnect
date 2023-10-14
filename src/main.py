import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QScrollArea, QGroupBox, QWidget, QMenu, QAction, QMenuBar, QPushButton, QTableWidget,QTableWidgetItem, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout,QRadioButton
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import interface
import random
import time


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self,rows = 0, columns = 3, device = 1, slave_address = 1, register_quantity = 1, register_name = "N/A", units = "N/A", gain = 1, data_type = "N/A", access_type = "RO"):
        super().__init__()

        interface.confirm_if_data_file_exists()
        
        # Initializing the main window
        self.rows = rows
        self.columns = columns
        self.device = device
        self.slave_address = slave_address
        self.register_quantity = register_quantity
        self.register_name = register_name
        self.units = units
        self.gain = gain
        self.data_type = data_type
        self.access_type = access_type

        self.main_widget = None


        

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
        # Update the registers after every one second.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_cells)
        self.timer.start(1000) # Update cells every 1 second



        

    def update_cells(self):  
        # interface.ModbusTcpClient.read_tcp_registers()
        device_table_widget = self.main_widget.findChildren(QTableWidget)

        for device_id in range(len(device_table_widget)): # Loop through the devices
            for row in range(device_table_widget[device_id].rowCount()): # Loop through the rows
                device_table_widget[device_id].setItem(row, 2, QTableWidgetItem(str(random.randint(0, 100)))) # Updating the register column (column 2) with the register values


        # Find the QLabel with name "connection_status_label"
        labels = self.main_widget.findChildren(QLabel)
        for label in labels:
            if label is not None:
                print("Label {}".format(label.objectName()))
                # label.setText("New connection status") # Change the text of the label  
            else:
                print("None") 


    # def update_cells(self):
    #     # row = random.randint(0, 9)
    #     # col = random.randint(0, 9)
    #     # value = random.randint(0, 100)
    #     # item = QtWidgets.QTableWidgetItem(str(value))
    #     # self.table_widget.setItem(row, col, item)
    #     child = window.main_widget.findChildren(QTableWidget)
    #     # print("Number of children",len(child))
    #     for num in range(len(child)):
    #         for row in range(child[num].rowCount()):
    #             child[num].setItem(row, 2, QTableWidgetItem(str(random.randint(0, 100))))
    #             # child[num].setItem(0, 2, QTableWidgetItem("Mwiti"))
    #             # child[num].setItem(0, 2, QTableWidgetItem("Njue"))

        

            

    def on_new_button_clicked(self):
        self.new_device_setup_dialog()
        config = self.submit_button_clicked()
        
        # print("Adding a new device")
        interface.append_device(config)
        self.add_devices_to_layout()


    '''
    This is the functions responsible for displaying all the registered devices on the screen.
    
    '''
    def add_devices_to_layout(self):
        saved_devices = interface.saved_device_count()

        if saved_devices != None:
            print("Found saved devices")
            self.main_widget = self.device_widget_setup(saved_devices)
            self.setCentralWidget(self.main_widget)
            # Add a small space between the menu bar and the central widget
            self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)
            self.show()
        else:
            # interface.append_device()
            # saved_devices = interface.saved_device_count()
            self.main_widget = self.device_widget_setup(saved_devices)
            self.setCentralWidget(self.main_widget)
            # Add a small space between the menu bar and the central widget
            self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)
            self.show()
        

    
    def device_widget_setup(self,saved_devices):
        if( saved_devices != None ):
            # Create a central widget
            central_widget = QWidget()
            # Create a horizontal layout to add the table widgets
            self.horizontal_layout = QHBoxLayout()
            # Read the register setup file and save the content in the 'data' variable
            data = interface.read_register_setup_file()
            # Loop through the register setup and create widgets for each device
            for i in range(len(saved_devices)):
                self.device = i+1
                registers_per_device = saved_devices["device_"+str(self.device)]
                widget = TableWidget(self.device, registers_per_device) # Create and instance of our table widget
                # widget.table_widget.setRowCount(saved_devices["device"+str(self.device)]) # Set the number of rows to the number of registers we have
                self.horizontal_layout.addWidget(widget) # Create the table widgets and add them in the horizontal layout
                # Add the register parameters in the rows and columns of each device
                for j in range(registers_per_device):
                    widget.table_widget.setItem(j, 0, QTableWidgetItem(data["device_" + str(self.device)]["registers"]["register_" + str(j+1)]["Register_name"])) # Update the register name
                    widget.table_widget.setItem(j, 1, QTableWidgetItem(str(data["device_" + str(self.device)]["registers"]["register_" + str(j+1)]["address"]))) # Update the string version of the register address
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
        



  

  
    def new_device_setup_dialog(self):
        self.register_setup_dialog = QDialog(self)
        self.register_setup_dialog.setWindowTitle("Connect")

        # Create the main Vertical layout
        device_setup_main_layout = QVBoxLayout()

        self.device_number = self.device

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

        self.com_port_items = interface.get_available_ports()
        # Create a list of the available com port
        self.com_ports = QComboBox()  # Create a drop-down list of com ports
        self.com_ports.addItems(self.com_port_items)  # Add com ports to the dropdown list for "Modbus RTU"
        com_ports_layout.addWidget(self.com_ports)  # Add com ports to the widget for "Modbus RTU"

        # Create a Horizontal layout and add a dropdown list of the com ports for "Modbus RTU"
        baud_rate_layout = QHBoxLayout()
        self.baud_rate_label = QLabel("Baud Rate")
        baud_rate_layout.addWidget(self.baud_rate_label)  # Add the label to the horizontal layout

        self.baud_rate_items = ["9600","14400","19200","38400","57600","115200"]
        # Create a list of baud rates for "Modbus RTU"
        self.baud_rates = QComboBox()  # Create a drop-down list of the baud rates for "Modbus RTU"
        self.baud_rates.addItems(self.baud_rate_items)  # Add baud rates to the dropdown list for "Modbus RTU"
        baud_rate_layout.addWidget(self.baud_rates)  # Add baud rates to the widget for "Modbus RTU"


        # Create a Horizontal layout and add a dropdown list of the Parity 
        parity_layout = QHBoxLayout()
        self.parity_label = QLabel("Parity")
        parity_layout.addWidget(self.parity_label)  # Add the label to the horizontal layout

        self.parity_items = ["None","Even","Odd","Mark","Space"]
        # Create a list of Parity options
        self.parity_options = QComboBox()  # Create a drop-down list of the Parity options.
        self.parity_options.addItems(self.parity_items)  # Add the parity options to the dropdown list.
        parity_layout.addWidget(self.parity_options)  # Add the parity options to the widget.

        # Create a Horizontal layout and add a dropdown list of the Stop bits 
        stop_bits_layout = QHBoxLayout()
        self.stop_bits_label = QLabel("Stop bits")
        stop_bits_layout.addWidget(self.stop_bits_label)  # Add the label to the horizontal layout

        self.stop_bits_items = ["1","1.5","2"]
        # Create a list of stop bits options
        self.stop_bits_options = QComboBox()  # Create a drop-down list of the stop bits options.
        self.stop_bits_options.addItems(self.stop_bits_items)  # Add the stop bits options to the dropdown list.
        stop_bits_layout.addWidget(self.stop_bits_options)  # Add the stop bits options to the widget.

        # Create a Horizontal layout and add a dropdown list of the byte size options
        byte_size_layout = QHBoxLayout()
        self.byte_size_label = QLabel("Byte size")
        byte_size_layout.addWidget(self.byte_size_label)  # Add the label to the horizontal layout

        self.byte_size_items = ["8","7"]
        # Create a list of byte size options
        self.byte_size_options = QComboBox()  # Create a drop-down list of the byte size options.
        self.byte_size_options.addItems(self.byte_size_items)  # Add the byte size options to the dropdown list.
        byte_size_layout.addWidget(self.byte_size_options)  # Add the byte size options to the widget.

        # Create a Horizontal layout and add list of timeout in seconds
        timeout_layout = QHBoxLayout()
        self.timeout_label = QLabel("Byte size")
        timeout_layout.addWidget(self.timeout_label)  # Add the label to the horizontal layout

        self.timeout_items = ["1","2","3"]
        # Create a list of byte size options
        self.timeout_options = QComboBox()  # Create a drop-down list of the seconds.
        self.timeout_options.addItems(self.timeout_items)  # Add the timeout options to the dropdown list.
        timeout_layout.addWidget(self.timeout_options)  # Add the timeout options to the widget.

        # Create a QPushButton for the submit button
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_button_clicked)

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


    def submit_button_clicked(self) -> dict:
        print("Submitted")
        # Check which radio button is selected (Modbus TCP or Modbus RTU)
        if self.modbus_tcp_radio.isChecked():
            temp_dict = {} 
            # Modbus TCP is selected
            temp_dict["device_name"] = self.tcp_custom_name.text()
            temp_dict['slave_address'] = self.tcp_slave_id.text()
            temp_dict['host'] = self.ip_address.text()
            temp_dict['port'] = self.port.text()

            cfg = {'connection_params': {'rtu_params': {}, 'tcp_params':temp_dict}, 'registers':{}}
            self.register_setup_dialog.accept()
            return cfg

        elif self.modbus_rtu_radio.isChecked():
            temp_dict = {}
            # Modbus RTU is selected
            temp_dict['device_name'] = self.rtu_custom_name.text()
            temp_dict['slave_address'] = self.rtu_slave_id.text()
            temp_dict['port'] = self.com_ports.currentText()  # Get the selected COM Port
            temp_dict['baudrate'] = self.baud_rates.currentText()
            temp_dict['parity'] = self.parity_options.currentText()
            temp_dict['stopbits'] = self.stop_bits_options.currentText()
            temp_dict['bytesize'] = self.byte_size_options.currentText()
            temp_dict['timeout'] = self.timeout_options.currentText()

            cfg = {'connection_params': {'rtu_params': temp_dict, 'tcp_params':{}}, 'registers':{}}
            self.register_setup_dialog.accept()
            return cfg


        
        






class TableWidget(QWidget):
    def __init__(self, device, rows, columns=3):
        super().__init__()

        self.rows = rows
        self.columns = columns
        self.device = device

        self.connection_status = False

        



        # Add a label for the register group or device group
        label_name = "Device " + str(self.device) # Create an initial name "Device " + the index of the register group. For example, Device 1

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
        self.connection_status_label.setObjectName("connection_status_label_device_" + str(self.device))
        



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
        self.table_widget.setHorizontalHeaderLabels(["Register Name", "Address", "Value"])
        self.table_widget.setColumnWidth(0, 200) # Set the width of the "Register Name" column to 200
        self.table_widget.setColumnWidth(1, 100) # Set the width of the "Address" column to 100
        self.table_widget.setColumnWidth(2, 100) # Set the width of the "Value" column to 100
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
            interface.update_register_name(self.device,row,text)


   

    def on_drop_down_menu_current_index_changed(self):
        
        if self.action_menu.currentIndex() == 1: # If the selectec option is Add registers (index 1)
            self.table_widget.itemChanged.disconnect(self.onItemChanged) # Disconnect the ItemChanged signal to alow us to reload the GUI
            self.showMessageBox() # Show the message box for adding registers
            self.action_menu.setCurrentIndex(0)
            self.table_widget.itemChanged.connect(self.onItemChanged)    # Reconnect the ItemChanged signal to allow us to update the register names
        elif self.action_menu.currentIndex() == 2: # If the selectec option is Delete registers (index 2)
            self.action_menu.setCurrentIndex(0)
            pass
        elif self.action_menu.currentIndex() == 3: # If the selected option is Connect (index 3)
            self.action_menu.setCurrentIndex(0)
            pass
        

    



    def showMessageBox(self):
        self.register_setup_dialog = QDialog(self)
        self.register_setup_dialog.setWindowTitle("Register Setup")

        # # Create the main Vertical layout
        rset_main_layout = QVBoxLayout()

        # # Create the first horizontal layout and add Slave ID label and its edit box
        # r_set_h_layout_1 = QHBoxLayout()
        # self.slave_id_label = QLabel("Slave ID")
        # self.slave_id = QLineEdit()
        
        # Add label and slave widgets to the first horizontal layout
        # r_set_h_layout_1.addWidget(self.slave_id_label)
        # r_set_h_layout_1.addWidget(self.slave_id)

        # Create a vertical layout and add a dropdown list of the function codes
        r_set_v_layout_1 = QVBoxLayout()
        self.fx_code_label = QLabel("Function Code")
        r_set_v_layout_1.addWidget(self.fx_code_label) # Add the label to the vertical layout

        self.fx_code_items = ["Read Holding Registers", "Read Input registers", "Read Discrete Inputs", "Read Coils"] # Create a list of function codes
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
        main_window = MainWindow()  # Create an instance of the main window to enable us to access some of the default values
        user_input = {} # An empty dictionary to store user input

        register_properties_dict ={} # Empty dictionary to store register properties
        register_properties_dict['Register_name'] = main_window.register_name   
        register_properties_dict['address'] = int(self.reg_address.text())
        register_properties_dict['function_code'] = self.function_code.currentText()
        register_properties_dict['Units'] =main_window.units
        register_properties_dict['Gain'] =main_window.gain
        register_properties_dict['Data_type'] =main_window.data_type
        register_properties_dict['Access_type'] =main_window.access_type

        # self.slave_address = self.slave_id.text()
        self.register_quantity = self.reg_quantity.text()
        user_input["device"] = self.device
        # user_input['slave_address'] = self.slave_address
        user_input['quantity'] = self.register_quantity

        user_input["registers"] = register_properties_dict
        row_count = self.table_widget.rowCount()
        print("Row count is ",str(row_count))
        register_quantity = int(self.register_quantity)
        register_address = int(self.reg_address.text())
        self.table_widget.setRowCount(row_count  + register_quantity)
        for x in range(register_quantity):
            register_address = register_address + x
            self.table_widget.setItem(row_count+x, 0, QTableWidgetItem("N/A"))
            self.table_widget.setItem(row_count+x, 1, QTableWidgetItem(str(register_address)))

        #interface.generate_setup_file(user_input)
        interface.update_setup_file(user_input)
        # self.update_register_table(self.reg_address.text(),self.reg_quantity.text())
        self.table_widget.update()




    def delete_register(self):
        print("Delete register")
        pass

    def delete_device(self):
        print("Delete register")
        pass







if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()
