from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import numpy as np
import json
import os
import  sys


modbus_device_settings = ""
rtu_clients_list = []
tcp_clients_list = []

#device_data = {}
device_name = ""


database_path = os.path.join(os.getcwd(), 'database','test.json')
path_to_register_setup = os.path.join(os.getcwd(), 'database','register_map_file.json')


if sys.platform.startswith('win'): # Check if we are running on Windows
    print('Running on Windows')
    windows_settings_path = os.path.join(os.getcwd(), 'devices','devices_windows.json')
    with open(windows_settings_path, 'r') as f:
          modbus_device_settings = json.load(f)

elif sys.platform.startswith('linux'): # Check if we are running on Linux
    print('Running on Linux')
    linux_settings_path = os.path.join(os.getcwd(), 'devices','devices_linux.json')
    with open(linux_settings_path, 'r') as f:
          modbus_device_settings = json.load(f)

else:
    print('Unknown platform')



# print(modbus_device_settings)
# print( "There are " + str(len(modbus_device_settings['devices'])) + " modbus device types connected:" )
# print( "-> ", str(len(modbus_device_settings['devices']['modbus_rtu_devices'])) + " modbus RTU devices" )
# print( "-> ", str(len(modbus_device_settings['devices']['modbus_tcp_devices'])) + " modbus TCP devices" )
# print()


def get_tcp_clients() -> list:
    print( "Modbus TCP devices" )
    
    # Connecting to the Modbus TCP devices
    # Loop through the registered Modbus TCP devices and connect to them
    for device in modbus_device_settings['devices']['modbus_tcp_devices']:   
        client_and_register_group_container = {}  # Create a dictionary to temporarrily store the client and register group information

        IP_ADDRESS = modbus_device_settings['devices']['modbus_tcp_devices'][device]['connection_params']['host']       # Get the IP address
        TCP_PORT = modbus_device_settings['devices']['modbus_tcp_devices'][device]['connection_params']['port']         # Get the port number
        REGISTER_GROUP = modbus_device_settings['devices']['modbus_tcp_devices'][device]['register_group']['group_id']  # Get the register group ID
        #print(IP_ADDRESS, TCP_PORT)   # Print the device information to the console
        tcp_client = ModbusTcpClient(IP_ADDRESS, TCP_PORT)
        
    
        try:
            tcp_client.connect()
            client_and_register_group_container['client'] = tcp_client
            client_and_register_group_container['register_group'] = REGISTER_GROUP
            tcp_clients_list.append(client_and_register_group_container)
            print("Connected to ", tcp_client, "successfully")
        except Exception as e:
            print(f"Connection to ", tcp_client, f"failed {e}")
    return tcp_clients_list
    

    


def get_rtu_clients() -> list:
    print( "Modbus RTU devices" )
    # Connecting to the Modbus RTU devices
    for device in modbus_device_settings['devices']['modbus_rtu_devices']:   
        client_and_register_group_container = {}  # Create a dictionary to temporarrily store the client and register group information

        SERIAL_PORT = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['port']
        BAUDRATE = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['baudrate']
        PARITY = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['parity']
        STOPBITS = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['stopbits']
        BYTESIZE = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['bytesize']
        TIMEOUT = modbus_device_settings['devices']['modbus_rtu_devices'][device]['connection_params']['timeout']

        REGISTER_GROUP = modbus_device_settings['devices']['modbus_rtu_devices'][device]['register_group']['group_id']  # Get the register group ID

        print(SERIAL_PORT, BAUDRATE, PARITY, STOPBITS, BYTESIZE, TIMEOUT)
        rtu_client = ModbusSerialClient(method='rtu',port=SERIAL_PORT,baudrate=BAUDRATE,parity=PARITY,stopbits=STOPBITS,bytesize=BYTESIZE,timeout=TIMEOUT)

        
        try:
            rtu_client.connect()
            client_and_register_group_container['client'] = rtu_client
            client_and_register_group_container['register_group'] = REGISTER_GROUP
            rtu_clients_list.append(client_and_register_group_container)
            print("Connected to Modbus RTU device successfully!")
        except Exception as e:
            print(f"Failed to connect to Modbus client {device+1}: {e}")
    return rtu_clients_list



def read_tcp_registers(client,group_id):
    with open(database_path, 'r') as f:
          data = json.load(f)
    
    register_group_id = "register_group_" + str(group_id) # Get the register group id to identify the registers to read for a specific device

    UNIT_ID = data[register_group_id]['slave_address']['address']
    print("Slave ID", UNIT_ID) 

    for variable in data[register_group_id]['registers']:
        if data[register_group_id]['registers'][variable]['function_code'] == 1:   
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']  
            device_name = device_name+variable 

            # response = client.read_coils(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)


        elif data[register_group_id]['registers'][variable]['function_code'] == 2:
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']  
            device_name = device_name+variable 

            # response = client.read_discrete_inputs(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)


        elif data[register_group_id]['registers'][variable]['function_code'] == 3:
            print("Reading ", variable, ". \nAddress is ",       data['registers'][variable]['address'], ". \nFunction_code is ", data['registers'][variable]['function_code'], "\nQuantity is ",  data['registers'][variable]['quantity'],"\n")                     
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']  
            device_name = device_name+variable 

            # response = client.read_holding_registers(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)


        elif data[register_group_id]['registers'][variable]['function_code'] == 4:
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']  
            device_name = device_name+variable 

            # response = client.read_input_registers(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)


        else:
            print("Unknown function_code")



def read_rtu_registers(client,group_id):
    with open(database_path, 'r') as f:
          data = json.load(f)

    register_group_id = "register_group_" + str(group_id) # Get the register group id to identify the registers to read for a specific device

    UNIT_ID = data[register_group_id]['slave_address']['address']  # Get the slave address
    print("Slave ID", UNIT_ID)

    for variable in data[register_group_id]['registers']:
        if data[register_group_id]['registers'][variable]['function_code'] == 1:
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']  
            device_name = device_name+variable 


            # response = client.read_coils(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)

        elif data[register_group_id]['registers'][variable]['function_code'] == 2:
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']

            # response = client.read_discrete_inputs(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)

        elif data[register_group_id]['registers'][variable]['function_code'] == 3:
            print("Reading ", variable, ". \nAddress is ",       data['registers'][variable]['address'], ". \nFunction_code is ", data['registers'][variable]['function_code'], "\nQuantity is ",  data['registers'][variable]['quantity'],"\n")              
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']

            # response = client.read_holding_registers(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)

        elif data[register_group_id]['registers'][variable]['function_code'] == 4:
            address = data[register_group_id]['registers'][variable]['address']
            quantity = data[register_group_id]['registers'][variable]['quantity']

            # response = client.read_input_registers(address, quantity, unit= UNIT_ID)
            # decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.Big, wordorder=Endian.Big)
            # data = decoder.decode_16bit_uint()
            #device_data.update(device_name=data)

        else:
            print("Unknown function_code")

# This function receives user input and default register parameters from gui.py file as a dictionary
def generate_setup_file(input_list):
    print(input_list)

    # Creating a path to store our register structure
    working_directory  = os.getcwd() 
    folder_path = 'database'
    filename = 'register_map_file.json'
    filepath = os.path.join(working_directory,folder_path,filename)

    # Get the quantity of registers to poll from. 
    reg_quantity = input_list["quantity"]
    group_id = input_list["register_group"]
    register_group = "register_group_" + str(group_id)
    unit_id = str(input_list["slave_address"])
    

    with open(filepath, 'w') as f:

        parent_data = {}

        # Loop through the list of registers entered by the user
        for i in range(int(reg_quantity)):
            parent_key = "register_" + str(i+1)  # This is the initial  name assigned to the variable that will be read from the register. The user will be allowed to rename the register later. 
            parent_value = {} 
            # Assigning values to all the registr attributes
            parent_value["address"] = int(input_list["registers"]["address"]) + i # If the user wants to read say 10 registers after register 1000, this line of code increments the addresses to register number 1011
            parent_value["Register_name"] = input_list["registers"]["Register_name"] 
            parent_value["function_code"] = input_list["registers"]["function_code"]
            parent_value["Units"] = input_list["registers"]["Units"]
            parent_value["Gain"] = input_list["registers"]["Gain"]
            parent_value["Data_type"] = input_list["registers"]["Data_type"]
            parent_value["Access_type"] = input_list["registers"]["Access_type"]
            parent_data[parent_key] = parent_value 

        json.dump({register_group: {'slave_address':unit_id, 'registers':parent_data}},f) # Appenining the register attributes with the json structure
        
        print("JSON file created!")

def check_for_existing_register_setup() -> bool:
        if os.path.isfile(path_to_register_setup):
            return True
        else:
            return False




            


'''
    response = client.read_coils(0, 10, unit= unit_id)
    response = client.read_discrete_inputs(0, 10, unit= unit_id)
    response = client.read_holding_registers(0, 10, unit= unit_id)
    response = client.read_input_registers(0, 10, unit= unit_id)

    response = client.write_coil(0, 1, unit= unit_id)
    response = client.write_register(0, 1, unit= unit_id)
    response = client.write_registers(0, 1, unit= unit_id)
    response = client.write_discrete_input(0, 1, unit= unit_id)
    response = client.write_register_input(0, 1, unit= unit_id)

    UNIT_ID = modbus_device_settings['devices']['modbus_tcp_devices'][device]['unit_id']  # Get the unit id
    UNIT_ID = modbus_device_settings['devices']['modbus_rtu_devices'][device]['unit_id']
    response = client.read_holding_registers(0, 10, unit= unit_id)
    print(f'Response from {device["host"]}:{device["port"]} - {response.registers}')
    

'''

# my_tcp_list = get_tcp_clients()
# print(my_tcp_list[0].get('client'))
# print(my_tcp_list[0].get('register_group'))
# print(my_tcp_list[1].get('client'))
# print(my_tcp_list[1].get('register_group'))
# print(my_tcp_list[2].get('client'))
# print(my_tcp_list[2].get('register_group'))
# print(my_tcp_list[3].get('client'))
# print(my_tcp_list[3].get('register_group'))

# my_rtu_list = get_rtu_clients()
# print(my_rtu_list[0].get('client'))
# print(my_rtu_list[0].get('register_group'))
# print(my_rtu_list[1].get('client'))
# print(my_rtu_list[1].get('register_group'))
# print(my_rtu_list[2].get('client'))
# print(my_rtu_list[2].get('register_group'))

# for client in rtu_clients_list:
#     read_rtu_registers(client)

# for client in tcp_clients_list:
#     read_tcp_registers(client)

