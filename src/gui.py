import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QScrollArea, QWidget, QMenu, QAction, QMenuBar, QPushButton, QTableWidget,QTableWidgetItem, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout
import interface


class MainWindow(QWidget):
    def __init__(self,rows = 0, columns = 3, device = 1, slave_address = 1, register_quantity = 1, register_name = "N/A", units = "N/A", gain = 1, data_type = "N/A", access_type = "RO"):
        super().__init__()


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

        # Create a vertical layout  and add the menu bar
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(menubar)



        # First check if there is a register setup file in the database
        register_setup_file_exists = interface.check_for_existing_register_setup()

        if register_setup_file_exists == True:
            print ("Register setup file exists")
            data = interface.read_register_setup_file() # read the register setup
            num_devices = 0 # Variable to store the number of register groups
            # Find out how many register groups there are in the register setup file
            for key in data.keys():
                if "device_" in key:
                    num_devices += 1
            print (num_devices)

            # Create a horizontal layout to add the table widgets
            self.horizontal_layout = QHBoxLayout()

            for i in range(num_devices):
                self.device = i+1
                self.horizontal_layout.addWidget(TableWidget(rows, columns, self.device)) # Create table widhets and add them in the horizontal layout
            
            self.horizontal_layout.addStretch()

            # Create a scroll area widget and add the horizontal layout to it
            scroll_area = QScrollArea()
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(QWidget())
            scroll_area.widget().setLayout(self.horizontal_layout)

            # Add the scroll area widget to the main layout
            self.main_layout.addWidget(scroll_area)
            self.setLayout(self.main_layout)  # Set the main layout
            

                
            
        else:
            print ("Register setup file does not exist")

            # Setting a few default values
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


    def on_new_button_clicked(self):
        print ("Create a new group")
        data = interface.read_register_setup_file()
        num_devices = 0 # Variable to store the number of register groups
        # Find out how many register groups there are in the register setup file
        for key in data.keys():
            if "device_" in key:
                num_devices += 1
        print (num_devices)

        






class TableWidget(QWidget):
    def __init__(self, rows, columns,device):
        super().__init__()

        # Add a label for the register group or device group
        label_name = "Device " + str(device) # Create an initial name "Device " + the index of the register group. For example, Device 1
        self.device_label = QLabel(label_name)


        # Add a button to add registers
        self.add_reg_button = QPushButton()
        self.add_reg_button.setText("Add registers")
        self.add_reg_button.setFixedSize(100,25) # Setting the size of the button
        self.add_reg_button.clicked.connect(self.showMessageBox)

        # Add a button to remove registers
        self.remove_reg_button = QPushButton()
        self.remove_reg_button.setText("Delete register")
        self.remove_reg_button.setFixedSize(100,25) # Setting the size of the button
        self.remove_reg_button.clicked.connect(self.delete_register)

        # Create a table to display the registers
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(rows)
        self.table_widget.setColumnCount(columns)
        self.table_widget.setHorizontalHeaderLabels(["Register Name", "Address", "Value"])
        self.table_widget.setColumnWidth(0, 200) # Set the width of the "Register Name" column to 200
        self.table_widget.setColumnWidth(1, 100) # Set the width of the "Address" column to 100
        self.table_widget.setColumnWidth(2, 100) # Set the width of the "Value" column to 100
        self.table_widget.setFixedWidth(self.table_widget.horizontalHeader().length()) # Set the maximum width of the qtable widget to the width of the 3 columnns we have ( "Register Name", "Address", "Value" )

        # Create a layout and add the table widget and the button buttons. 
        self.layout = QVBoxLayout()

        
        # Create a horizontal layout to hold the Device group label and the two buttons (Add and remove register buttons)
        self.h_layout = QHBoxLayout() 
        self.h_layout.addWidget(self.device_label)
        self.h_layout.addWidget(self.add_reg_button)
        self.h_layout.addWidget(self.remove_reg_button)
        self.layout.addLayout(self.h_layout)
        self.layout.addWidget(self.table_widget)
        

        # Set the layout for the widget
        self.setLayout(self.layout)



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
        list_register_properties ={} # Empty dictionary to store register properties
        list_register_properties['Register_name'] = main_window.register_name   
        list_register_properties['address'] = int(self.reg_address.text())
        list_register_properties['function_code'] = self.function_code.currentText()
        list_register_properties['Units'] =main_window.units
        list_register_properties['Gain'] =main_window.gain
        list_register_properties['Data_type'] =main_window.data_type
        list_register_properties['Access_type'] =main_window.access_type

        self.slave_address = self.slave_id.text()
        self.register_quantity = self.reg_quantity.text()
        user_input["device"] = main_window.device
        user_input['slave_address'] = self.slave_address
        user_input['quantity'] = self.register_quantity
        user_input["registers"] = list_register_properties
        self.rows = int(self.register_quantity)
        self.table_widget.setRowCount(self.rows)
        interface.generate_setup_file(user_input)
        self.update_register_table()
        self.table_widget.update()


        # Add the register addresses to the "Address" column
    def update_register_table(self):
        register = int(self.reg_address.text())
        for row in range (int(self.reg_quantity.text())):
            str_register = str(register)
            self.table_widget.setItem(row, 1, QTableWidgetItem(str_register))
            register = register + 1

    def delete_register(self):
        print("Delete register")
        pass

                


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()