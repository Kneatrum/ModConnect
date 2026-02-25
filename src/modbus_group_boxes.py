
from serial_ports import SerialPorts

from PyQt5.QtWidgets import  QGroupBox, QVBoxLayout, QLabel, \
    QLineEdit, QComboBox, QHBoxLayout


from constants import NO_COM_PORTS, PARITY_ITEMS, STOP_BIT_ITEMS, BAUD_RATE_ITEMS, \
        BYTESIZE_ITEMS, TIMEOUT_ITEMS



class RtuGroupBox(QGroupBox):
    """
    Create a QGroupBox for the "Modbus RTU" elements
    
    """
    def __init__(self, title, parent=None):
        super(RtuGroupBox, self).__init__(title, parent)
        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        self.rtu_custom_name_layout = QHBoxLayout()
        self.rtu_custom_name_label = QLabel("Custom Name")
        self.rtu_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus RTU"
        self.rtu_custom_name_layout.addWidget(self.rtu_custom_name_label)
        self.rtu_custom_name_layout.addWidget(self.rtu_custom_name)

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
        if self.com_port_items:
            self.com_ports.addItems(self.com_port_items)  # Add com ports to the dropdown list for "Modbus RTU"
            com_ports_layout.addWidget(self.com_ports)  # Add com ports to the widget for "Modbus RTU"
        else: 
            self.com_ports.addItem(NO_COM_PORTS)  # Add com ports to the dropdown list for "Modbus RTU"
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
        self.timeout_label = QLabel("Timeout") # Add the label to the horizontal
        timeout_layout.addWidget(self.timeout_label)  # Add the label to the horizontal layout


        # Create a list of byte size options
        self.timeout_options = QComboBox()  # Create a drop-down list of the seconds.
        self.timeout_options.addItems(TIMEOUT_ITEMS)  # Add the timeout options to the dropdown list.
        timeout_layout.addWidget(self.timeout_options)  # Add the timeout options to the widget.

        # Create a vertical layout for the elements inside the "Modbus RTU" group box
        modbus_rtu_group_box_layout = QVBoxLayout()
        modbus_rtu_group_box_layout.addLayout(self.rtu_custom_name_layout)
        modbus_rtu_group_box_layout.addLayout(rtu_slave_id_layout)
        modbus_rtu_group_box_layout.addLayout(com_ports_layout)
        modbus_rtu_group_box_layout.addLayout(baud_rate_layout)
        modbus_rtu_group_box_layout.addLayout(parity_layout)
        modbus_rtu_group_box_layout.addLayout(stop_bits_layout)
        modbus_rtu_group_box_layout.addLayout(byte_size_layout)
        modbus_rtu_group_box_layout.addLayout(timeout_layout)

        # Set the layout of the "Modbus RTU" group box
        self.setLayout(modbus_rtu_group_box_layout)
        self.resize(300,300)

    def set_custom_name_invisible(self, status):
        status = not status
        self.rtu_custom_name_label.setVisible(status)
        self.rtu_custom_name.setVisible(status)

    def set_slave_address_invisible(self, status):
        status = not status
        self.rtu_slave_id_label.setVisible(status)
        self.rtu_slave_id.setVisible(status)



class TcpGroupBox(QGroupBox):
        # Create a QGroupBox for the "Set" elements
    def __init__(self, title, parent=None):
        super(TcpGroupBox, self).__init__(title, parent)

        # Create the first horizontal layout and a provison for assigning a custom name to the "Modbus TCP" device
        tcp_custom_name_layout = QHBoxLayout()
        self.tcp_custom_name_label = QLabel("Custom Name")
        self.tcp_custom_name = QLineEdit()

        # Add label and slave widgets to the first horizontal layout for "Modbus TCP"
        tcp_custom_name_layout.addWidget(self.tcp_custom_name_label)
        tcp_custom_name_layout.addWidget(self.tcp_custom_name)

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
        self.setLayout(modbust_tcp_group_box_layout)
        self.resize(300, 300)

    def set_custom_name_invisible(self, status):
        status = not status
        self.tcp_custom_name_label.setVisible(status)
        self.tcp_custom_name.setVisible(status)

    def set_slave_address_invisible(self, status):
        status = not status
        self.tcp_slave_id_label.setVisible(status)
        self.tcp_slave_id.setVisible(status)