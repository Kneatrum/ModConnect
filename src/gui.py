import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget,QTableWidgetItem, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout
import interface







class MainWindow(QWidget):
    def __init__(self,rows=0,columns = 3, register_group = 1, units = "N/A", gain = 1, data_type = "N/A", access_type = "RO"):
        super().__init__()
        self.setWindowTitle("Modpoll")
        self.rows = rows
        self.columns = columns
        self.register_group = register_group
        self.units = units
        self.gain = gain
        self.data_type = data_type
        self.access_type = access_type
        

        


        # Add a button to add registers
        self.add_reg_button = QPushButton()
        self.add_reg_button.setText("Add registers")
        self.add_reg_button.clicked.connect(self.showMessageBox)



        # Create a table to display the registers
        self.reg_tablewidget = QTableWidget(self)
        self.reg_tablewidget.setRowCount(self.rows)
        self.reg_tablewidget.setColumnCount(self.columns)
        self.reg_tablewidget.setHorizontalHeaderLabels(["Register Name ", "Address", "Value"])

        # Create a layout and add widgets to it, then set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.add_reg_button)
        layout.addWidget(self.reg_tablewidget)
        self.setLayout(layout)

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

    def update_register_table(self):
        register = int(self.reg_address.text())
        for row in range (int(self.reg_quantity.text())):
            str_register = str(register)
            self.reg_tablewidget.setItem(row, 1, QTableWidgetItem(str_register))
            register = register + 1

    def get_user_input(self):
        user_input = {}
        slave_id = self.slave_id.text()
        function_code = self.function_code.currentText()
        reg_address = self.reg_address.text()
        reg_quantity = self.reg_quantity.text()
        user_input["register_group"] = self.register_group
        user_input['slave_address'] = slave_id
        user_input['function_code'] = function_code
        user_input['address'] = reg_address
        user_input['quantity'] = reg_quantity
        self.rows = int(reg_quantity)
        self.reg_tablewidget.setRowCount(self.rows)
        interface.generate_setup_file(user_input)
        self.update_register_table()
        self.reg_tablewidget.update()

        

        



         


    


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()