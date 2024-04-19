"""
This Module provides classes and methods responsible for I/O operations.
It acts as link between the file system and other classes in their modules.
"""

import os
import json
import re
import copy
from constants import SLAVE_ADDRESS, \
        DEVICE_NAME, CONNECTION_PARAMETERS,  \
        DEVICE_PREFIX, REGISTERS, REGISTER_ADDRESS, \
        REGISTER_NAME, REGISTER_PREFIX, FILE_PATH, \
        FUNCTION_CODE, REGISTER_TEMPLATE, DEFAULT_METHOD, \
        REGISTER_QUANTITY, MAX_DEVICES, MAX_REGISTERS, HIDDEN_STATUS, resource_path












class FileHandler:




    def __init__(self):
        self.file_path = resource_path(FILE_PATH)
        self.directory = os.path.dirname(self.file_path)
        self.max_devices = MAX_DEVICES


    def data_directory_exists(self) -> bool:
        """
        This method checks if the data directory exists.

        Args:
            None

        returns:
            bool: True if the data directory exists and false otherwise.
        """
        return os.path.exists(self.directory)
    

    def data_path_exists(self) -> bool:
        """
        This method simply checks if the path to our json file exists.

        arguments: 
            None

        returns:
            bool: True if the path to our json file exists or False otherwise.
        """
        return os.path.exists(self.file_path)
    

    def create_data_directory(self):
        """
        This method checks if the data directory exists and creates it if it does not exist

        then it creates the json data file.

        arguments:
            None

        returns:
            None
        """
        if not self.data_directory_exists():
            os.mkdir(self.directory)  
            self.create_data_file()


    def create_data_file(self):
        with open(self.file_path, 'w') as file:
            pass


    def create_path_if_not_exists(self):
        self.create_data_directory()
        

    def get_raw_device_data(self) -> dict:
        """
        This method returns all register data stored in our json file.

        arguments:
            None

        returns:
            data (dict): A dictionary full of register data or an empty dictionary if no data is available. 
        """
        if not self.data_path_exists():
            print("Data directory does not exist")
            return {}
        try:
            with open(self.file_path, 'r') as file:
                # Check if there is content in the file
                content = file.read()
            if not content:
                print("File is empty")
                return {}
            data = json.loads(content)
            return data
        except FileNotFoundError:
            print("File not found")
            return {}
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding: {e}")
            return {}
        

    def save_device_data(self, data):
        """
        This method takes in the register data and saves it into
        the register data file.

        arguments: 
            data (dict): The register data

        returns:
            bool: True if successful in saving the register data or False otherwise

        """
        try:
            with open(self.file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except TypeError as e:
            print(f"Error serializing data to json: {e}")
            return False
        except IOError as e:
            print(f"Error Writing to file: {e}")
            return False
        

    def get_slave_address(self, device_number) -> int:
        if not self.data_path_exists():
            print("Data path does not exist")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        device = DEVICE_PREFIX + f'{device_number}'
        return data.get(device, {}).get(SLAVE_ADDRESS, None)
    

    def get_device_name(self, device_number) -> str:
        if not self.data_path_exists():
            print("Data path does not exist")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        device = DEVICE_PREFIX + f'{device_number}'
        return data.get(device, {}).get(DEVICE_NAME, None)



    def get_device_count(self):
        """
        This method returns the number of all devices that are registered.

        arguments: 
            None

        returns:
            count (int): The total number of devices.
        """
        # If the path for our data does not exist, return
        if not self.data_path_exists():
            print("Data file not found")
            return 0
        # Read all data from the stored json file
        data = self.get_raw_device_data()
        if not data:
            return 0
        device_count = len(data.keys())
        return device_count


    def get_string_device_tags(self):
        """
        This method returns all devices keys that are registered.

        arguments: 
            None

        returns:
            device_keys (list): A list containing all device keys.
        """
        # If the path for our data does not exist, return
        if not self.data_path_exists():
            print("Data file not found")
            return 0
        # Read all data from the stored json file
        data = self.get_raw_device_data()
        if not data:
            return None
        device_keys = data.keys()
        return device_keys


    
    def get_register_count(self, device_number) -> int:
        """
        This method returns the number of registers in a specific device

        argument: 
            device_number (int): The device number. This is always a unique number
        
        returns:
            count (int): The number of registers in the device.
        """
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        
        device = f'{DEVICE_PREFIX}{device_number}'
        count = len(data[device][REGISTERS])
        return count


    def get_register_attributes(self, device_number: int, *args) -> dict:
        """
        This method returns a dictionary containing a list of the 
        specified register attributes

        args:
            device_number: This is used as the unique identifier for the stored devices.
            list_of_attributes (list): A list of register attributes

        returns:
            dictionary: A dictionary containing the register attributes.

        Example:
        register_1: [register_name, register_address]
        """
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None
        # First find the device with the device number.
        device = f'{DEVICE_PREFIX}{device_number}'

        result = {}
        for address in data[device][REGISTERS]:
            temp_dict = {} 
            for register_attribute in args:
                temp_dict[register_attribute] = data[device][REGISTERS][address][register_attribute]
            result[address] = temp_dict
        return result
   


    def get_registers_to_read(self, device_number: int) -> dict:
        """
        This method returns a dictionary registers and their attributes. 
        
        args:
            device_number (int): This is used as the unique identifier for the stored devices.

        returns:
            result (dict): A dictionary containing the register address as the key and function codes as the value.

        Example:
            result = {
                '10': {'function_code': 3}, 
                '11': {'function_code': 3}, 
                '12': {'function_code': 3} 
            }
        """
        if not self.data_path_exists():
            print("Data path not found")
            return None
        data = self.get_raw_device_data()
        if not data:
            return None

        device = f'{DEVICE_PREFIX}{device_number}'
        result = dict()
        for register in data[device][REGISTERS]:
                temp_dict = {}
                temp_dict[FUNCTION_CODE] = data[device][REGISTERS][register].get(FUNCTION_CODE)
                result[register] = temp_dict
        return result


    def get_connection_params(self, device_number: int) -> dict: 
        """
        This method reads the stored json data from the default filepath 
        and gets the connection parameters. eg: RTU and/or TCP

        args:
            device_number: This is used as the unique identifier for the stored devices.

        returns:
            dictionary: A dictionary of the available protocols as the key 
            and its connection parameters as the value. 
            
        Example:
        {'tcp': {'host': '127.0.0.1', 'port': 503}}
        """
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
        """
        This method returns a list of all modbus protocol methods registered in a specific device.

        arguments: 
            device_number (int): The device number (always unique)

        returns:
            list: A list of all modbus protocol methods registered.
        """
        result = self.get_connection_params(device_number)
        if not result:
            return None
        return list(result.keys())




    def update_connection_params(self, device_number) -> bool: 
        pass


    def get_existing_register_addresses(self, device_number):
        """
        This method returns all devices keys that are registered.

        arguments: 
            device_number (int): The unique device number

        returns:
            addresses (list): A list containing all the registers in a particular device
        """
        # If the path for our data does not exist, return
        if not self.data_path_exists():
            print("Data file not found")
            return 0
        # Read all data from the stored json file
        data = self.get_raw_device_data()
        if not data:
            return None
        
        device = f'{DEVICE_PREFIX}{device_number}'
        addresses = data[device][REGISTERS].keys()
        addresses = [int(value) for value in addresses]
        return  addresses



    def update_register_details(self, device_number, user_input) -> bool:
        """
        This method adds new registers to a specific device's window or table widget.

        arguments:
            device_number (int): The device number (always unique)
            user_input (dict): A dictionary containing all the register data gathered from the user.

        returns:
            bool: True if the the register was added successfully or false otherwise
        """
        data = self.get_raw_device_data()
        if not data:
            return None
        device = f'{DEVICE_PREFIX}{device_number}'
        existing_addresses =  self.get_existing_register_addresses(device_number)
        print("User input", user_input)
        quantity = int(user_input[REGISTER_QUANTITY]) 
        start_address = int(user_input[REGISTER_ADDRESS]) 
        for i in range(quantity):
            address = start_address + i
            if address not in existing_addresses:
                temp_dict = dict()
                temp_register_template = copy.copy(REGISTER_TEMPLATE)
                temp_register_template[FUNCTION_CODE] = user_input[FUNCTION_CODE]
                temp_dict[address] = temp_register_template
                data[device][REGISTERS].update(temp_dict)
            else:
                # Show a notification to the user that some registers were existing  and have been discarded
                print(f'Register {address} is a duplicate and has been discarded')
        
        # Finally, save the new configuration
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)
        self.save_device_data(data)


    def update_register_name(self, device_number, register_address, register_name) -> bool:
        """
        This method updates simply assigns a name to a register address.
        
        arguments:
            device_number (int): The device number (always unique)
            register_address (str): The register address in its string representation
            register_name (str): The name of the register in its string representation

        returns:
            bool: True if the the register was renamed successfully or false otherwise

        """
        data = self.get_raw_device_data()
        if not data:
            return None
        device = f'{DEVICE_PREFIX}{device_number}'
        data[device][REGISTERS][register_address][REGISTER_NAME] = register_name
        # Save the new configuration
        if self.save_device_data(data):
            return True
        return False



    def add_device(self, user_input) -> int:
        """
        This method receives a dictionary representing a new device from the user
        
        and appends it to the existing configuration or writes it directly to
        
        the file if it's a new device.
        """
     
        device_count = self.get_device_count()
        
        if device_count >= MAX_DEVICES:
            print("You have reached the maximum number of devices")
            return 0

        new_tag = self.generate_new_device_tag()

        if device_count < 1:
            if new_tag:
                user_input = {f'{DEVICE_PREFIX}{new_tag}': user_input}
                if self.save_device_data(user_input):
                    return new_tag
                return 0

        elif device_count < MAX_DEVICES:
            data = self.get_raw_device_data()
            if new_tag:
                user_input = {f'{DEVICE_PREFIX}{new_tag}': user_input}
                data.update(user_input)
                if self.save_device_data(data):
                    return new_tag
                return 0


    def delete_device(self, device_number):
        data = self.get_raw_device_data()
        if not data:
            return None
        delete_tag = f'{DEVICE_PREFIX}{device_number}'
        del data[delete_tag]
        self.save_device_data(data)
        

    def update_hidden_status(self, device_number, new_status):
        device_tag = f'{DEVICE_PREFIX}{device_number}'
        data = self.get_raw_device_data()
        if not data:
            return None
        old_status = data[device_tag].get(HIDDEN_STATUS)
        # print("Old status",old_status)
        if old_status is not None and old_status != new_status:
            data[device_tag][HIDDEN_STATUS] = new_status
            # print("New status",data[device_tag][HIDDEN_STATUS])
            self.save_device_data(data)


    def get_hidden_status(self, device_number):
        device_tag = f'{DEVICE_PREFIX}{device_number}'
        data = self.get_raw_device_data()
        if not data:
            return None
        status = data[device_tag].get(HIDDEN_STATUS)
        if status is not None:
            return status
        return None


    
    def get_hidden_devices(self):
        """
        Returns a list of all hidden devices.

        args: 
            None

        returns: 
            hidden_devices (list): a list of all hidden device numbers.

        """
        hidden_devices = []
        data = self.get_raw_device_data()
        if not data:
            return None
        for key in data.keys():
            if data[key].get(HIDDEN_STATUS) is not None and data[key].get(HIDDEN_STATUS) == True:
                hidden_devices.append(int(re.findall(r'\d+', key)[0]))
        return hidden_devices



    def generate_new_device_tag(self, prefix_activated=False):
        """
        Generate a new and unique device tag.

        args:
            prefix_activated (bool): Will be False by default or if no parameter is passed in.
            
                If True, the new device tag will be of this format: 'device_x' where x is an integer)
            
                If False, the new device tag will just be an integer x.

                x will always be a unique number

        """
        new_device_number = None
        existing_tags = self.get_int_device_tags()

        if not existing_tags:
            new_device_number = 1
        else:
            for number in range(1, MAX_DEVICES + 1):
                if not number in existing_tags:
                    new_device_number = number
                    break
        
        if isinstance(new_device_number, int):
            if prefix_activated:
                return f'{DEVICE_PREFIX}{new_device_number}'
            else:
                return new_device_number
        else:
            return None


    def get_int_device_tags(self):
        string_device_tags = self.get_string_device_tags()
        if string_device_tags:
            return [int(re.findall(r'\d+', item)[0]) for item in string_device_tags if re.findall(r'\d+', item)]
        else: return None

    def delete_registers(self, device_number, addresses) -> bool:
        """
        This method receives a list of addresses and deletes them.

        arguments:
            device_number (int): The unique device number whose registers we want to delete

            addresses (list): A list of registers to delete
        
        """
        if not isinstance(device_number, int) and device_number > 0:
            print("Please enter a positive number.")
            return False
        
        
        device = f'{DEVICE_PREFIX}{device_number}'

        data = self.get_raw_device_data()
        if not data:
            return False
        
        for address in addresses:
            del data[device][REGISTERS][str(address)]

        self.save_device_data(data)


    def __save_connection_params(self, device_number) -> bool: ######################
        pass


    def get_default_modbus_method(self, device_number) -> bool: 
        """
        This method returns the default modbus method

        arguments: 
            Device number.

        returns:
            The default modbus method (rtu or tcp), or None if it has not been defined.
        """
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
                # Get and return the default modbus method
                default_method = data[device].get(DEFAULT_METHOD)
                return default_method
        return None
    

    def set_default_modbus_method(self, device_number: int, default_method: str) -> bool:
        """
        This method sets the default modbus method.

        arguments:
            device_number (int): The device number. Acts as a unique identifier in the json file.

            default_method (str): The default modbus method to be set. Can be either 'tcp' or 'rtu'.

        return:
            None
        """ 
        data = self.get_raw_device_data()
        if not data:
            return False
        device = DEVICE_PREFIX + f'{device_number}'

        data[device][DEFAULT_METHOD] = default_method

        # Finally, save new modbus method
        if self.save_device_data(data):
            return True
        
        return False


