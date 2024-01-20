"""
This module will be called upon when the user needs to connect
to a modbus RTU device. 

"""

import serial.tools.list_ports

class SerialPorts:
    def __init__(self):
        pass

    # This method returns a list of available ports.
    def get_available_ports() -> list:
        available_ports = list(serial.tools.list_ports.comports())
        port_list = []
        if not available_ports:
            print("No ports available.")
            return None
        else:
            for port in available_ports:
                port_list.append(port.device)
            return port_list