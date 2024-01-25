"""
This is an abstract class from which we will inherit when implementing
methods used for connecting to modbus protocols.
"""
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from file_handler import FileHandler
from constants import RTU_METHOD, TCP_METHOD, SERIAL_PORT, BAUD_RATE, PARITY, STOP_BITS, BYTESIZE, TIMEOUT, HOST, PORT


class ModbusProtocol:
    def __init__(self):
        self.client = None


    def connect_to_client(self):
        if not self.is_connected():
            self.client.connect()
    

    def disconnect_from_client(self):
        self.client.close()


    def is_connected(self):
        if self.client.is_socket_open():
            return True
        return False

    



class ModbusRTU(ModbusProtocol):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
 
    def generate_client(self, device_number):
        connection_attributes = self.file_handler.get_connection_params(device_number)[RTU_METHOD]
        self.client = ModbusSerialClient(
            method=RTU_METHOD,
            port=connection_attributes[SERIAL_PORT], 
            baudrate=int(connection_attributes[BAUD_RATE]), 
            parity=connection_attributes[PARITY], 
            stopbits=int(connection_attributes[STOP_BITS]),  
            bytesize=int(connection_attributes[BYTESIZE]), 
            timeout=connection_attributes[TIMEOUT]
            )
        return self.client

class ModbusTCP(ModbusProtocol):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()

    def generate_client(self, device_number):
        connection_attributes = self.file_handler.get_connection_params(device_number)[TCP_METHOD]
        host = connection_attributes[HOST]
        port = connection_attributes[PORT]
        self.client = ModbusTcpClient(host, port)
        return self.client
    