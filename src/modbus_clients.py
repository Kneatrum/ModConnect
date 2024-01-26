"""
This is an abstract class from which we will inherit when implementing
methods used for connecting to modbus protocols.
"""
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from file_handler import FileHandler
from constants import RTU_METHOD, TCP_METHOD, SERIAL_PORT, BAUD_RATE, PARITY, STOP_BITS, BYTESIZE, TIMEOUT, HOST, PORT


class ModbusClient:
    """
    This is a parent class that encapsulates the 

    methods used to get modbus protocol attributes that are required to 

    create an instance of of a modbus client.
    """

    def __init__(self, device_number):
            self.file_handler = FileHandler()
            self.device_number = device_number
            self.client = self.generate_client()

    def generate_client(self):
        """
        This method should get the device_number's connection parameters 
        
        and passes them as arguments to the specific modbus client's class which in turn returns a client.
        """
        raise NotImplementedError("Subclasses must implement generate_client method")
    




class ModbusRTU(ModbusClient):
    def __init__(self, device_number):
        self.file_handler = FileHandler()
        self.device_number = device_number
        self.client = self.generate_client()
 
    def generate_client(self):
        
        connection_attributes = self.file_handler.get_connection_params(self.device_number)[RTU_METHOD]
        client = ModbusSerialClient(
        method=RTU_METHOD,
        port=connection_attributes[SERIAL_PORT], 
        baudrate=int(connection_attributes[BAUD_RATE]), 
        parity=connection_attributes[PARITY], 
        stopbits=int(connection_attributes[STOP_BITS]),  
        bytesize=int(connection_attributes[BYTESIZE]), 
        timeout=float(connection_attributes[TIMEOUT])
        )
        return client
    
    

class ModbusTCP(ModbusClient):
    def __init__(self, device_number):
        self.file_handler = FileHandler()
        self.device_number = device_number
        self.client = self.generate_client()

    def generate_client(self):
        connection_attributes = self.file_handler.get_connection_params(self.device_number)[TCP_METHOD]
        host = connection_attributes[HOST]
        port = connection_attributes[PORT]
        client = ModbusTcpClient(host, port)
        return client
    