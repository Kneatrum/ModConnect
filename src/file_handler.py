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
        FUNCTION_CODE, REGISTER_TEMPLATE












class FileHandler:




    def __init__(self):
        self.file_path = FILE_PATH
        self.directory = os.path.dirname(self.file_path)


    def data_directory_exists(self) -> bool:
        return os.path.exists(self.directory)
    

    def data_path_exists(self) -> bool:
        return os.path.exists(self.file_path)
    

    def create_data_directory(self):
        if not self.data_directory_exists():
            os.mkdir(self.directory)  
            self.create_data_file()


    def create_data_file(self):
        with open(self.file_path, 'w') as file:
            pass


    def create_path_if_not_exists(self):
        self.create_data_directory()
        

    def get_raw_device_data(self) -> dict:
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
        # If the path for our data does not exist, return
        if not self.data_path_exists():
            print("Data file not found")
            return None
        # Read all data from the stored json file
        data = self.get_raw_device_data()
        if not data:
            return 0
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
        count = 0
        for key in data:
            device = DEVICE_PREFIX + f'{device_number}'
            if re.search(device, key):
                # Now count the number of registers in the device
                for reg in data[device][REGISTERS]:
                    # Increment the count variable if we find this pattern (register_x) where x is a number.
                    if re.match(REGISTER_PREFIX + r'(\d+)', reg):
                        count += 1
        return count


    def get_register_attributes(self, device_number: int, list_of_variables: list) -> dict:
        """
        This method returns a dictionary containing a list of the 
        register name and the address.

        args:
            device_number: This is used as the unique identifier for the stored devices.

        returns:
            dictionary: A dictionary with the register key and a list containing the name and the register address.

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
        for key in data:
            device = DEVICE_PREFIX + f'{device_number}'
            if re.search(device, key):
                # Now count the number of registers in the device
                # We may not need to use a dictionary here. Maybe a list of the addresses is enough.
                result = dict()
                for reg in data[device][REGISTERS]:
                    temp_dict = {}
                    for item in list_of_variables:
                        temp_dict[item] = data[device][REGISTERS][reg][item]
                    result[reg] = temp_dict
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
        result = self.get_connection_params(device_number)
        return list(result.keys())




    def update_connection_params(self, device_number) -> bool: 
        pass


    def update_register_details(self, device_number, user_input) -> bool:
        print(user_input)
        existing_register_count = self.get_register_count(device_number)
        data = self.get_raw_device_data()
        if not data:
            return None
        device = DEVICE_PREFIX + f'{device_number}'
        quantity = int(user_input['quantity']) 

        for i in range(quantity) :
            temp_dict = dict()

            # If the existing register count is 1 for example, the next should be 2. Hence the additional of 1
            temp_key = REGISTER_PREFIX + str(existing_register_count + i + 1) 
            
            # Make a temporary copy of the registers template
            temp_register_template = copy.copy(REGISTER_TEMPLATE)

            # Assign values to the keys that we are interested in for now 
            temp_register_template[REGISTER_ADDRESS] =  user_input[REGISTERS][REGISTER_ADDRESS] + i  # If the user wants to read say 10 registers after register 1000, this line of code increments the addresses to register number 1011
            temp_register_template[FUNCTION_CODE] = user_input[REGISTERS][FUNCTION_CODE]
            temp_dict[temp_key] = temp_register_template
            data[device][REGISTERS].update(temp_dict)

        # Finally, save the new configuration
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)


    def update_register_name(self, device_number, register_address) -> bool:
    # update_register_name(device_id:int, row:int, name:str):
    # target_register = "register_" + str(row+1)
    # # Read the register setup file
    # data = read_register_setup_file()
    # data["device_" + str(device_id)]['registers'][target_register].update({'Register_name':name})
    # with open(path_to_register_setup, 'w') as f:
    #     json.dump(data, f, indent=4)
        pass



    """
    This method receives a dictionary representing a new device from the user
    and appends it to the existing configuration or writes it directly to
    the file if it's a new device.
    """
    def add_device(self, user_input) -> bool:
        # If there is no existing device, write the new device into the json file.
        if self.get_device_count() == 0:
            with open(self.file_path, 'w') as file:
                json.dump(user_input, file)
        # There are existing devices, so we need to read the whole configuration file and append the new one to it, then save it again.
        else:
            data = self.get_raw_device_data()
            data.update(user_input)
            with open(self.file_path, 'w') as file:
                json.dump(data, file)




    def delete_register(self, device_number, register_address) -> bool:
        pass


    def __save_connection_params(self, device_number) -> bool: ######################
        pass


    def __save_register_data(self, user_input:dict) -> bool: ######################
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

            # Update the existing json file with the new register parameters

        # print("JSON file created!")
        pass

