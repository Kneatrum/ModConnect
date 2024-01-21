"""
This is an abstract class from which we will inherit when implementing
methods used for connecting to modbus protocols.
"""


class ModbusProtocol:
    def __init__(self, client):
        self.client = client



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
    def __init__(self, client, unit=None):
        super().__init__(client)
        if unit is not None:
            self.unit = unit
        
        
class ModbusTCP(ModbusProtocol):
    def __init__(self, client, unit=None):
        super().__init__(self, client)
        if unit is not None:
            self.unit = unit