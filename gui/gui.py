import sys,os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialog,QHBoxLayout
#from Interface import interface

interface_module_path = os.path.join(os.getcwd(), 'Interface')
print (interface_module_path)
sys.path.append(interface_module_path)






class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modpoll")

        


        # Add a button to add registers
        self.add_reg_button = QPushButton()
        self.add_reg_button.setText("Add registers")
        self.add_reg_button.clicked.connect(self.showMessageBox)



        # Create a table to display the registers
        self.reg_tablewidget = QTableWidget()
        self.reg_tablewidget.setRowCount(0)
        self.reg_tablewidget.setColumnCount(3)
        self.reg_tablewidget.setHorizontalHeaderLabels(["Register Name ", "Address", "Value"])

        # Create a layout and add widgets to it, then set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.add_reg_button)
        layout.addWidget(self.reg_tablewidget)
        self.setLayout(layout)

    def showMessageBox(self):
        register_setup_dialog = QDialog(self)
        register_setup_dialog.setWindowTitle("Register Setup")

        # Create the main Vertical layout
        rset_main_layout = QVBoxLayout()

        # Create the first horizontal layout and add Slave ID label and its edit box
        r_set_h_layout_1 = QHBoxLayout()
        slave_id_label = QLabel("Slave ID")
        slave_id = QLineEdit()

        # Add label and slave widgets to the first horizontal layout
        r_set_h_layout_1.addWidget(slave_id_label)
        r_set_h_layout_1.addWidget(slave_id)


        # Create a vertical layout and add a dropdown list of the function codes
        r_set_v_layout_1 = QVBoxLayout()
        fx_code_label = QLabel("Function Code")
        r_set_v_layout_1.addWidget(fx_code_label) # Add the label to the vertical layout


        fx_code_items = ["Read Holding Registers", "Read Input registers", "Read Discrete Inputs", "Read Coils"] # Create a list of function codes
        function_code = QComboBox() # Create a drop down list of function codes
        function_code.addItems(fx_code_items) # Add function codes to the dropdown list
        r_set_v_layout_1.addWidget(function_code) # Add function code items to widget

        # Create a horizontal layout for Register address label and its edit box
        r_set_h_layout_2 = QHBoxLayout()
        reg_address_label =  QLabel("Register Address")
        reg_address = QLineEdit()
        r_set_h_layout_2.addWidget(reg_address_label)
        r_set_h_layout_2.addWidget(reg_address)


        # Create a horizontal layout for Register quantity and its edit box
        r_set_h_layout_3 = QHBoxLayout()
        reg_quantity_label = QLabel("Quantity")
        reg_quantity = QLineEdit()
        r_set_h_layout_3.addWidget(reg_quantity_label)
        r_set_h_layout_3.addWidget(reg_quantity)
        

        # Create a button to submit the register setup
        r_set_h_layout_4 = QHBoxLayout()
        rset_submit_button = QPushButton("Submit")
        r_set_h_layout_4.addWidget(rset_submit_button)
        #rset_submit_button.clicked.connect(interface.generate_setup_file)




        # Add all the layouts to the main vertical layout
        rset_main_layout.addLayout(r_set_h_layout_1)
        rset_main_layout.addLayout(r_set_v_layout_1)
        rset_main_layout.addLayout(r_set_h_layout_2)
        rset_main_layout.addLayout(r_set_h_layout_3)
        rset_main_layout.addLayout(r_set_h_layout_4) 
        register_setup_dialog.setLayout(rset_main_layout)
        register_setup_dialog.exec_()      


    


    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    app.exec_()