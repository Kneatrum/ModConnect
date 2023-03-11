from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ConnectionException

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
