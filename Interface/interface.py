from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ConnectionException
import json
import os
import  sys


modbus_device_settings = ""
rtu_client = ""
tcp_client = ""

database_path = os.path.join(os.getcwd(), 'database','test.json')


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



#print(modbus_device_settings)
print( "There are " + str(len(modbus_device_settings['devices'])) + " modbus device types connected:" )
print( "-> ", str(len(modbus_device_settings['devices']['modbus_rtu_devices'])) + " modbus RTU devices" )
print( "-> ", str(len(modbus_device_settings['devices']['modbus_tcp_devices'])) + " modbus TCP devices" )
print()



print( "Modbus TCP devices" )
# Connecting to the Modbus TCP devices
# Loop through the registered Modbus TCP devices and connect to them
for device in modbus_device_settings['devices']['modbus_tcp_devices']:   
    IP_ADDRESS = modbus_device_settings['devices']['modbus_tcp_devices'][device]['host']  # Get the IP address
    TCP_PORT = modbus_device_settings['devices']['modbus_tcp_devices'][device]['port']        # Get the port number
    print(IP_ADDRESS, TCP_PORT)   # Print the device information to the console
    try:
        tcp_client = ModbusTcpClient(IP_ADDRESS, TCP_PORT)
        connection = tcp_client.connect()
        if connection == True: print("Connected to " + IP_ADDRESS + ":" + str(TCP_PORT))
        else: raise Exception('Connection to ' + IP_ADDRESS + ':' + str(TCP_PORT) + 'failed')
    except Exception as e:
        print(e)



print( "Modbus RTU devices" )
# Connecting to the Modbus RTU devices
for device in modbus_device_settings['devices']['modbus_rtu_devices']:   
    SERIAL_PORT = modbus_device_settings['devices']['modbus_rtu_devices'][device]['port']
    BAUDRATE = modbus_device_settings['devices']['modbus_rtu_devices'][device]['baudrate']
    PARITY = modbus_device_settings['devices']['modbus_rtu_devices'][device]['parity']
    STOPBITS = modbus_device_settings['devices']['modbus_rtu_devices'][device]['stopbits']
    BYTESIZE = modbus_device_settings['devices']['modbus_rtu_devices'][device]['bytesize']
    TIMEOUT = modbus_device_settings['devices']['modbus_rtu_devices'][device]['timeout']
    print(SERIAL_PORT, BAUDRATE, PARITY, STOPBITS, BYTESIZE, TIMEOUT)
    try:
        rtu_client = ModbusSerialClient(method='rtu',port=SERIAL_PORT,baudrate=BAUDRATE,parity=PARITY,stopbits=STOPBITS,bytesize=BYTESIZE,timeout=TIMEOUT)
        connection = rtu_client.connect()
        if connection is True:
            print("Connected to Modbus RTU device successfully!")
        else:
            raise Exception("Connection failed!")
    except Exception as e:
        print(e)


def read_registers(client):
    with open(database_path, 'r') as f:
          data = json.load(f)
    UNIT_ID = data['slave_address']['address']
    print(UNIT_ID)
    for variable in data['registers']:
        print(variable)
        print(client)
            #response = client.read_holding_registers(0, 10, unit= UNIT_ID)





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





    































'''
for device in modbus_device_settings:
        print(settings['devices'])
        print(settings['devices']['modbus_rtu_devices'])
        print(settings['devices']['modbus_rtu_devices']['device_1'])
        print()


# Define a list of Modbus TCP devices to connect to
tcp_devices = [
    {'host': '192.168.0.10', 'port': 502},
    {'host': '192.168.0.20', 'port': 502},
    {'host': '192.168.0.30', 'port': 502}
]

# Define a list of Modbus RTU devices to connect to
rtu_devices = [
    {'port': '/dev/ttyUSB0', 'baudrate': 9600},
    {'port': '/dev/ttyUSB1', 'baudrate': 9600},
    {'port': '/dev/ttyUSB2', 'baudrate': 9600}
]

# Connect to each Modbus TCP device and read some data
for device in tcp_devices:
    try:
        client = ModbusTcpClient(device['host'], device['port'])
        response = client.read_holding_registers(0, 10, unit=1)
        print(f'Response from {device["host"]}:{device["port"]} - {response.registers}')
        client.close()
    except ConnectionException:
        print(f'Failed to connect to {device["host"]}:{device["port"]}')

# Connect to each Modbus RTU device and read some data
for device in rtu_devices:
    try:
        client = ModbusSerialClient(method='rtu', port=device['port'], baudrate=device['baudrate'])
        response = client.read_holding_registers(0, 10, unit=1)
        print(f'Response from {device["port"]} - {response.registers}')
        client.close()
    except ConnectionException:
        print(f'Failed to connect to {device["port"]}')

'''




