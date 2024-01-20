"""
This Module provides classes and methods responsible for I/O operations.
It acts as link between the file system and other classes in their modules.
"""

import os
import json
import re

# Variable to store the path to our json file which we use to store register data.
FILE_PATH = ''

# All devices in the json file start with this prefix.
DEVICE_PREFIX = 'device_'

# All registers in the json file start with this prefix
REGISTER_PREFIX = 'register_'

# Constants storing some of the key strings that make up the json file
REGISTERS = 'registers'
REGISTER_ADDRESS = 'address'
CONNECTION_PARAMETERS = 'connection_params'
TCP_PARAMETERS = 'tcp'
RTU_PARAMETERS = 'rtu'


# Set the default path for a windows system.
if os.name == 'nt':
    FILE_PATH = os.path.join(os.getcwd(), 'data', 'register_map_file.json')


# Set the default path for a linux system.
if os.name == 'posix':
    # TODO: Enter path for linux system.
    pass




class FileHandler:
    def __init__(self, path):
        self.path = path
        self.directory = os.path.dirname(self.path)


    def data_directory_exists(self) -> bool:
        return os.path.exists(self.directory)
    

    def data_path_exists(self) -> bool:
        return os.path.exists(self.path)
    

    def create_data_directory(self):
        if not self.data_directory_exists():
            os.mkdir(self.directory)  


    def create_data_file(self):
        with open(self.path, 'w') as file:
            pass


    def create_path_if_not_exists(self):
        self.create_data_directory()
        self.create_data_file()
        

    def get_raw_device_data(self) -> dict:
        if not self.data_path_exists():
            print("Data directory does not exist")
            return None
        with open(self.path, 'r') as file:
            data = json.load(file)
        return data


    def get_device_count(self):
        # If the path for our data does not exist, return
        if not self.data_path_exists():
            print("Data file not found")
            return None
        # Read all data from the stored json file
        data = self.get_raw_device_data()
        if not data:
            return None
        count = 0
        for key in data:
            # Increase the counter if the key contains the device prefix (device_) and the device prefix is followed by some digits.
            if re.match(DEVICE_PREFIX + r'(\d+)', key):
                count += 1
        return count


    
    def get_register_count(self, device_number) -> int:
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        # First find the device with the device number.
        for key in data:
            device = DEVICE_PREFIX + f'{device_number}'
            if re.search(device, key):
                # Now count the number of registers in the device
                count = 0
                for reg in data[device][REGISTERS]:
                    # Increment the count variable if we find this pattern (register_x) where x is a number.
                    if re.match(REGISTER_PREFIX + r'(\d+)', reg):
                        count += 1
        return count



    def get_register_addresses(self, device_number) -> dict:
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        # First find the device with the device number.
        for key in data:
            device = DEVICE_PREFIX + f'{device_number}'
            if re.search(device, key):
                # Now count the number of registers in the device
                # We may not need to use a dictionary here. Maybe a list of the addresses is enough.
                result = dict()
                for reg in data[device][REGISTERS]:
                    result[reg] = data[device][REGISTERS][reg][REGISTER_ADDRESS]
        return result


    def get_connection_params(self, device_number) -> dict: 
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        
        protocol_dict = dict()
        # First find the device with the device number.
        for key in data:
            device = DEVICE_PREFIX + f'{device_number}'
            if re.search(device, key):
                # Loop through the device's connection parameters and store each registered protocol inside the protocol_dict variable.
                for protocol in data[device][CONNECTION_PARAMETERS]:
                    # Store the protocol only if it is not empty.
                    if data[device][CONNECTION_PARAMETERS].get(protocol):
                        protocol_dict[protocol] = data[device][CONNECTION_PARAMETERS].get(protocol)
        return protocol_dict
    

    def get_modbus_protocol(self, device_number) -> list:
        result = self.get_connection_params(device_number)
        return list(result.keys())




    def update_connection_params(self, device_number) -> bool: 
        pass


    def update_register_addresses(self, device_number) -> bool:
        pass


    def update_register_name(self, device_number, register_address) -> bool:
        pass


    def add_device(self, device_number, device_params) -> bool:
        pass


    def delete_register(self, device_number, register_address) -> bool:
        pass


    def __save_connection_params(self, device_number) -> bool: ######################
        pass


    def __save_register_addresses(self, device_number) -> bool: ######################
        pass



