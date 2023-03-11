from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ConnectionException
import json
import os
import  sys





modbus_device_settings = ""


if sys.platform.startswith('win'):
    print('Running on Windows')
    windows_settings_path = os.path.join(os.getcwd(), 'devices','devices_windows.json')
    with open(windows_settings_path, 'r') as f:
          modbus_device_settings = json.load(f)

elif sys.platform.startswith('linux'):
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





for device in modbus_device_settings['devices']['modbus_tcp_devices']:   
    unit_id = modbus_device_settings['devices']['modbus_tcp_devices'][device]['unit_id']
    ip_address = modbus_device_settings['devices']['modbus_tcp_devices'][device]['host']
    port = modbus_device_settings['devices']['modbus_tcp_devices'][device]['port']
    print(unit_id, ip_address, port)
    '''
    try:
        client = ModbusTcpClient(ip_address, port)
        response = client.read_holding_registers(0, 10, unit= unit_id)
        print(f'Response from {device["host"]}:{device["port"]} - {response.registers}')
        client.close()
    except ConnectionException:
        print(f'Failed to connect to {device["host"]}:{device["port"]}')
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




