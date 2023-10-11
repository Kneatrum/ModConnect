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

        
     
        self.add_devices_to_layout(self.rows,self.columns)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_cells)
        self.timer.start(1000) # Update cells every 1 second



        
    def update_cells(self):
        # row = random.randint(0, 9)
        # col = random.randint(0, 9)
        # value = random.randint(0, 100)
        # item = QtWidgets.QTableWidgetItem(str(value))
        # self.table_widget.setItem(row, col, item)
        child = window.main_widget.findChildren(QTableWidget)
        print("Number of children",len(child))
        for num in range(len(child)):
            for row in range(child[num].rowCount()):
                child[num].setItem(row, 2, QTableWidgetItem(str(random.randint(0, 100))))
                # child[num].setItem(0, 2, QTableWidgetItem("Mwiti"))
                # child[num].setItem(0, 2, QTableWidgetItem("Njue"))

        
            

    def on_new_button_clicked(self):
        self.new_device_setup_dialog()
        
        # print("Adding a new device")
        # interface.append_device()
        # self.add_devices_to_layout(self.rows,self.columns)



    def add_devices_to_layout(self, rows, columns):
        saved_devices = interface.saved_device_count()

        if saved_devices != 0:
            print("Found saved devices")
            self.main_widget = self.device_widget(rows,columns,saved_devices)
            self.setCentralWidget(self.main_widget)
            # Add a small space between the menu bar and the central widget
            self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)
            self.show()
        else:
            saved_devices = 1
            print("No saved devices")
            blank_widget = TableWidget(rows, columns,saved_devices) # Add a blank widget
            self.setCentralWidget(blank_widget)
            # Add a small space between the menu bar and the central widget
            self.centralWidget().layout().setContentsMargins(0, 20, 0, 50)
            self.show()

    
    def device_widget(self,rows,columns,saved_devices):
        if( saved_devices > 0 ):
            # Create a central widget
            central_widget = QWidget()
            # Create a horizontal layout to add the table widgets
            self.horizontal_layout = QHBoxLayout()
            # Read the register setup file and save the content in the 'data' variable
            data = interface.read_register_setup_file()
            # Loop through the register setup and create widgets for each register group/ device
            for i in range(saved_devices):
                self.device = i+1
                registers_per_device = interface.register_count_under_device(data,self.device) # Find how many registers we have per device
                widget = TableWidget(rows, columns, self.device) # Create and instance of our table widget
                widget.table_widget.setRowCount(registers_per_device) # Set the number of rows to the number of registers we have
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
        self.register_setup_dialog.setWindowTitle("Register Setup")

        # Create the main Vertical layout
        rset_main_layout = QVBoxLayout()

        label_name = "Device "

        # Create a QGroupBox for the entire dialog
        dialog_group_box = QGroupBox(label_name, self)

        # Create a horizontal layout for the Modbus options (radio buttons)
        modbus_options_layout = QHBoxLayout()
        
        self.modbus_tcp_radio = QRadioButton("Modbus TCP")
        self.modbus_rtu_radio = QRadioButton("Modbus RTU")
        
        # Add radio buttons to the layout
        modbus_options_layout.addWidget(self.modbus_tcp_radio)
        modbus_options_layout.addWidget(self.modbus_rtu_radio)
        
        # Add the Modbus options layout to the main layout
        rset_main_layout.addLayout(modbus_options_layout)

        # Create a QGroupBox for the "Set" elements
        set_group_box = QGroupBox("Set", self)
        set_group_box.setFixedWidth(450)  # Set a fixed width to prevent resizing

        # Create the first horizontal layout and add Slave ID label and its edit box for "Set"
        r_set_h_layout_1 = QHBoxLayout()
        self.slave_id_label = QLabel("Slave ID1")
        self.slave_id = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Set"
        r_set_h_layout_1.addWidget(self.slave_id_label)
        r_set_h_layout_1.addWidget(self.slave_id)

        # Create a vertical layout and add a dropdown list of the function codes for "Set"
        r_set_v_layout_1 = QVBoxLayout()
        self.fx_code_label = QLabel("Function Code1")
        r_set_v_layout_1.addWidget(self.fx_code_label)  # Add the label to the vertical layout

        self.fx_code_items = ["Read Holding Registers", "Read Input registers", "Read Discrete Inputs", "Read Coils"]
        # Create a list of function codes
        self.function_code = QComboBox()  # Create a drop-down list of function codes
        self.function_code.addItems(self.fx_code_items)  # Add function codes to the dropdown list
        r_set_v_layout_1.addWidget(self.function_code)  # Add function code items to the widget

        # Create a horizontal layout for Register address label and its edit box for "Set"
        r_set_h_layout_2 = QHBoxLayout()
        self.reg_address_label = QLabel("Register Address1")
        self.reg_address = QLineEdit(self)
        r_set_h_layout_2.addWidget(self.reg_address_label)
        r_set_h_layout_2.addWidget(self.reg_address)

        # Create a horizontal layout for Register quantity and its edit box for "Set"
        r_set_h_layout_3 = QHBoxLayout(self)
        self.reg_quantity_label = QLabel("Quantity1")
        self.reg_quantity = QLineEdit(self)
        r_set_h_layout_3.addWidget(self.reg_quantity_label)
        r_set_h_layout_3.addWidget(self.reg_quantity)

        # Create a vertical layout for the elements inside the "Set" group box
        set_group_box_layout = QVBoxLayout()
        set_group_box_layout.addLayout(r_set_h_layout_1)
        set_group_box_layout.addLayout(r_set_v_layout_1)
        set_group_box_layout.addLayout(r_set_h_layout_2)
        set_group_box_layout.addLayout(r_set_h_layout_3)

        # Set the layout of the "Set" group box
        set_group_box.setLayout(set_group_box_layout)

        # Create a QGroupBox for the "Set2" elements
        set2_group_box = QGroupBox("Set2", self)
        set2_group_box.setFixedWidth(450)  # Set a fixed width to prevent resizing

        # Create the first horizontal layout and add Slave ID label and its edit box for "Set2"
        r_set2_h_layout_1 = QHBoxLayout()
        self.slave_id2_label = QLabel("Slave ID")
        self.slave_id2 = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Set2"
        r_set2_h_layout_1.addWidget(self.slave_id2_label)
        r_set2_h_layout_1.addWidget(self.slave_id2)

        # Create a vertical layout and add a dropdown list of the function codes for "Set2"
        r_set2_v_layout_1 = QVBoxLayout()
        self.fx_code2_label = QLabel("Function Code")
        r_set2_v_layout_1.addWidget(self.fx_code2_label)  # Add the label to the vertical layout

        self.fx_code2_items = ["Read Holding Registers", "Read Input registers", "Read Discrete Inputs", "Read Coils"]
        # Create a list of function codes for "Set2"
        self.function_code2 = QComboBox()  # Create a drop-down list of function codes for "Set2"
        self.function_code2.addItems(self.fx_code2_items)  # Add function codes to the dropdown list for "Set2"
        r_set2_v_layout_1.addWidget(self.function_code2)  # Add function code items to the widget for "Set2"

        # Create a horizontal layout for Register address label and its edit box for "Set2"
        r_set2_h_layout_2 = QHBoxLayout()
        self.reg_address2_label = QLabel("Register Address")
        self.reg_address2 = QLineEdit(self)
        r_set2_h_layout_2.addWidget(self.reg_address2_label)
        r_set2_h_layout_2.addWidget(self.reg_address2)

        # Create a horizontal layout for Register quantity and its edit box for "Set2"
        r_set2_h_layout_3 = QHBoxLayout(self)
        self.reg_quantity2_label = QLabel("Quantity")
        self.reg_quantity2 = QLineEdit(self)
        r_set2_h_layout_3.addWidget(self.reg_quantity2_label)
        r_set2_h_layout_3.addWidget(self.reg_quantity2)

        # Create a vertical layout for the elements inside the "Set2" group box
        set2_group_box_layout = QVBoxLayout()
        set2_group_box_layout.addLayout(r_set2_h_layout_1)
        set2_group_box_layout.addLayout(r_set2_v_layout_1)
        set2_group_box_layout.addLayout(r_set2_h_layout_2)
        set2_group_box_layout.addLayout(r_set2_h_layout_3)

        # Set the layout of the "Set2" group box
        set2_group_box.setLayout(set2_group_box_layout)

        # Initially hide "Set" and "Set2" group boxes
        set_group_box.hide()
        set2_group_box.hide()

        # Connect radio buttons to show/hide the respective group boxes
        self.modbus_tcp_radio.toggled.connect(lambda: set_group_box.setVisible(self.modbus_tcp_radio.isChecked()))
        self.modbus_rtu_radio.toggled.connect(lambda: set2_group_box.setVisible(self.modbus_rtu_radio.isChecked()))

        # Add the "Set2" group box to the main layout
        rset_main_layout.addWidget(set2_group_box)

        # Add the "Set" group box to the main layout
        rset_main_layout.addWidget(set_group_box)

        # Add the main layout to the main group box
        dialog_group_box.setLayout(rset_main_layout)

        # Execute the dialog box
        self.register_setup_dialog.setLayout(rset_main_layout)
        self.register_setup_dialog.exec_()





        



class TableWidget(QWidget):
    def __init__(self, rows, columns,device):
        super().__init__()

        self.rows = rows
        self.columns = columns
        self.device = device



        # Add a label for the register group or device group
        label_name = "Device " + str(self.device) # Create an initial name "Device " + the index of the register group. For example, Device 1

        # Create a QGroupBox
        group_box = QGroupBox(label_name, self)
        group_box.setMinimumWidth(450) # set minimum width
        group_box.setMaximumWidth(450) # set maximum width

  
    

        # Add a button to add registers
        add_reg_button = QPushButton()
        add_reg_button.setText("Add registers")
        add_reg_button.setFixedSize(100,25) # Setting the size of the button
        add_reg_button.clicked.connect(self.showMessageBox)

        # Add a button to remove registers
        remove_reg_button = QPushButton()
        remove_reg_button.setText("Delete register")
        remove_reg_button.setFixedSize(100,25) # Setting the size of the button
        remove_reg_button.clicked.connect(self.delete_register)

        # Add a button to remove Device 
        remove_device_button = QPushButton()
        remove_device_button.setText("Delete device")
        remove_device_button.setFixedSize(100,25) # Setting the size of the button
        remove_device_button.clicked.connect(self.delete_device)

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

        
        # Create a horizontal button layout to hold the three buttons 
        button_layout = QHBoxLayout() 
        button_layout.addWidget(add_reg_button)
        button_layout.addStretch() # Add a stretch to create a spacer
        button_layout.addWidget(remove_reg_button)
        button_layout.addStretch() # Add a stretch to create a spacer
        button_layout.addWidget(remove_device_button)
        
        
        # Create a vertical layout to hold the buttons and the table widget
        button_and_tablewidget_layout = QVBoxLayout()
        button_and_tablewidget_layout.addLayout(button_layout)
        button_and_tablewidget_layout.addWidget(self.table_widget)

        # Add the button and table widget to the group box
        group_box.setLayout(button_and_tablewidget_layout)

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

    


    def showMessageBox(self):
        self.register_setup_dialog = QDialog(self)
        self.register_setup_dialog.setWindowTitle("Register Setup")

        # Create the main Vertical layout
        rset_main_layout = QVBoxLayout()

        # Create the first horizontal layout and add Slave ID label and its edit box
        r_set_h_layout_1 = QHBoxLayout()
        self.slave_id_label = QLabel("Slave ID")
        self.slave_id = QLineEdit()
        
        # Add label and slave widgets to the first horizontal layout
        r_set_h_layout_1.addWidget(self.slave_id_label)
        r_set_h_layout_1.addWidget(self.slave_id)

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
        self.register_setup_dialog.close()

        # Add all the layouts to the main vertical layout
        rset_main_layout.addLayout(r_set_h_layout_1)
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

        self.slave_address = self.slave_id.text()
        self.register_quantity = self.reg_quantity.text()
        user_input["device"] = main_window.device
        user_input['slave_address'] = self.slave_address
        user_input['quantity'] = self.register_quantity

        user_input["registers"] = register_properties_dict
        self.rows = int(self.register_quantity)
        self.table_widget.setRowCount(self.rows)

        #interface.generate_setup_file(user_input)
        interface.update_setup_file(user_input)
        self.update_register_table(self.reg_address.text(),self.reg_quantity.text())
        self.table_widget.update()


        # Add the register addresses to the "Address" column
    def update_register_table(self,register_start_address,register_quantity):
        register = int(register_start_address)
        for row in range (int(register_quantity)):
            str_register = str(register)
            self.table_widget.setItem(row, 1, QTableWidgetItem(str_register))
            register = register + 1

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
