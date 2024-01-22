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
REGISTER_NAME = 'register_name'
REGISTER_ADDRESS = 'address'
CONNECTION_PARAMETERS = 'connection_params'
TCP_PARAMETERS = 'tcp'
RTU_PARAMETERS = 'rtu'




class FileHandler:

    # Set the default path for a windows system.
    if os.name == 'nt':
        FILE_PATH = os.path.join(os.getcwd(), 'data', 'register_map_file.json')


    # Set the default path for a linux system.
    if os.name == 'posix':
        # TODO: Enter path for linux system.
        pass


    def __init__(self):
        self.file_path = self.FILE_PATH
        self.directory = os.path.dirname(self.file_path)


    def data_directory_exists(self) -> bool:
        return os.path.exists(self.directory)
    

    def data_path_exists(self) -> bool:
        return os.path.exists(self.file_path)
    

    def create_data_directory(self):
        if not self.data_directory_exists():
            os.mkdir(self.directory)  


    def create_data_file(self):
        with open(self.file_path, 'w') as file:
            pass


    def create_path_if_not_exists(self):
        self.create_data_directory()
        self.create_data_file()
        

    def get_raw_device_data(self) -> dict:
        if not self.data_path_exists():
            print("Data directory does not exist")
            return None
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        return data
    

    def get_slave_address(self, device_number) -> int:
        if not self.data_path_exists():
            print("Data path does not exist")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        device = DEVICE_PREFIX + f'{device_number}'
        return data.get(device, {}).get('slave_address', None)
    

    def get_device_name(self, device_number) -> str:
        if not self.data_path_exists():
            print("Data path does not exist")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        device = DEVICE_PREFIX + f'{device_number}'
        return data.get(device, {}).get('device_name', None)



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


    """
    This method returns a register_x dictionary containing a list of the 
    register name and the address.
    Example:
    register_1: [register_name, register_address]
    """
    def get_register_names_and_addresses(self, device_number) -> dict:
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
                    result[reg] = list(data[device][REGISTERS][reg][REGISTER_NAME], data[device][REGISTERS][reg][REGISTER_ADDRESS])
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
    # update_register_name(device_id:int, row:int, name:str):
    # target_register = "register_" + str(row+1)
    # # Read the register setup file
    # data = read_register_setup_file()
    # data["device_" + str(device_id)]['registers'][target_register].update({'Register_name':name})
    # with open(path_to_register_setup, 'w') as f:
    #     json.dump(data, f, indent=4)
        pass




    def add_device(self, user_input) -> bool:
        # print(user_input)
        # Get the quantity of registers to poll from. 
        # reg_quantity = user_input_dict["quantity"]
        # device_id = user_input_dict["device"]
        # device = "device_" + str(device_id)
        # unit_id = str(user_input_dict["slave_address"])
        # with open(path_to_register_setup, 'w') as f:
        #     parent_data = {}
        #     register_data = {}
        #     # Loop through the list of registers entered by the user
        #     for i in range(int(reg_quantity)):
        #         parent_key = "register_" + str(i+1)  # This is the initial  name assigned to the variable that will be read from the register. The user will be allowed to rename the register later. 
        #         parent_value = {} 
        #         # Assigning values to all the registr attributes
        #         # parent_value["address"] = int(user_input_dict["registers"]["address"]) + i # If the user wants to read say 10 registers after register 1000, this line of code increments the addresses to register number 1011
        #         # parent_value["Register_name"] = user_input_dict["registers"]["Register_name"] 
        #         # parent_value["function_code"] = user_input_dict["registers"]["function_code"]
        #         # parent_value["Units"] = user_input_dict["registers"]["Units"]
        #         # parent_value["Gain"] = user_input_dict["registers"]["Gain"]
        #         # parent_value["Data_type"] = user_input_dict["registers"]["Data_type"]
        #         # parent_value["Access_type"] = user_input_dict["registers"]["Access_type"]
        #         # parent_data[parent_key] = parent_value 
        #     json.dump({device: {'slave_address':unit_id, 'registers':parent_data}},f) # Appenining the register attributes with the json structure
        #     register_data[parent_key] = parent_value 
        #     json.dump({device: {'slave_address':unit_id, 'registers':register_data}},f) # Appenining the register attributes with the json structure
        #     print("JSON file created!")
        pass




    def delete_register(self, device_number, register_address) -> bool:
        pass


    def __save_connection_params(self, device_number) -> bool: ######################
        pass


    def save_register_data(self, user_input:dict) -> bool: ######################
        # device_id = user_input_dict["device"]
        # reg_quantity = user_input_dict["quantity"]
        # # Read the register setup file
        # data = read_register_setup_file()
        # # Loop through the list of registers entered by the user and update the the register setup file
        # for i in range(int(reg_quantity)):
        #     existing_register_count = register_count_under_device(data,device_id) # Find the number of registers that exist
        #     # print("Existing register count {}".format(existing_register_count))
        #     new_register_start = "register_" + str(existing_register_count + 1) # If x registers exist, the next register will be x+1
        #     # print("New register start {}".format(new_register_start))
        #     parent_value = {} 
        #     # Assigning values to all the registr attributes
        #     parent_value["address"] = int(user_input_dict["registers"]["address"]) + i # If the user wants to read say 10 registers after register 1000, this line of code increments the addresses to register number 1011
        #     parent_value["Register_name"] = user_input_dict["registers"]["Register_name"] 
        #     parent_value["function_code"] = user_input_dict["registers"]["function_code"]
        #     parent_value["Units"] = user_input_dict["registers"]["Units"]
        #     parent_value["Gain"] = user_input_dict["registers"]["Gain"]
        #     parent_value["Data_type"] = user_input_dict["registers"]["Data_type"]
        #     parent_value["Access_type"] = user_input_dict["registers"]["Access_type"] 

        #     # Update the existing json file with the new register parameters
        #     data["device_" + str(device_id)]['registers'].update({new_register_start:parent_value})
        #     with open(path_to_register_setup, 'w') as f:
        #         json.dump(data, f, indent=4)
        # print("JSON file created!")
        pass

