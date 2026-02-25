'''
This module stores all the constants used in the code.
'''

import os, sys

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2 # Or _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Variable to store the path to our json file which we use to store register data.
FILE_PATH = ''

if os.name == 'nt':
    # Set the default path for a windows system.
    FILE_PATH = os.path.join(os.getcwd(), 'data', 'register_map_file.json')

if os.name == 'posix':
    # Set the default path for a linux system.
    # TODO: Enter path for linux system.
    FILE_PATH = ''


# Json file constants.
DEVICE_PREFIX = 'device_'
DEVICE_NAME = 'device_name'
SLAVE_ADDRESS = 'slave_address'
CONNECTION_PARAMETERS = 'connection_params'
TCP_PARAMETERS = 'tcp'
RTU_PARAMETERS = 'rtu'
HOST = 'host'
PORT = 'port'
SERIAL_PORT = 'serial_port'
BAUD_RATE = 'baudrate'
PARITY = 'parity'
STOP_BITS = 'stopbits'
BYTESIZE = 'bytesize'
TIMEOUT = 'timeout'
REGISTERS = 'registers'
REGISTER_PREFIX = 'register_'
REGISTER_ADDRESS = 'address'
REGISTER_NAME = 'register_name'
REGISTER_QUANTITY = 'quantity'
FUNCTION_CODE = 'function_code'
UNITS = 'units'
GAIN = 'gain'
DATA_TYPE = 'data_type'
ACCESS_TYPE = 'access_type'
HIDDEN_STATUS = 'hidden_status'



REGISTER_TEMPLATE = {
    REGISTER_NAME: "",
    FUNCTION_CODE: 0,
    UNITS: "N/A",
    GAIN: 0,
    DATA_TYPE: "N/A",
    ACCESS_TYPE: "R/O"
}

# Modbus RTU settings
PARITY_ITEMS = ['N','E','O','M','S'] # N=None, E=Even, O=Odd, M=Mark, S=Space
STOP_BIT_ITEMS = ["1","1.5","2"]
BAUD_RATE_ITEMS = ["9600","14400","19200","38400","57600","115200"]
BYTESIZE_ITEMS = ["8","7"]
TIMEOUT_ITEMS = ["1","2","3"]


REGISTER_PROPERTIES = {
    REGISTER_NAME: "", 
    FUNCTION_CODE: 1,
    UNITS: "",
    GAIN: 1,
    DATA_TYPE: "",
    ACCESS_TYPE: "",
}

READ_FUNCTION_CODES = {
    "READ_COILS (01)": 1,
    "READ_DISCRETE_INPUTS (02)": 2,
    "READ_HOLDING_REGISTERS (03)": 3,
    "READ_INPUT_REGISTERS (04)": 4
}

WRITE_FUNCTION_CODES = {
    "WRITE_SINGLE_COIL (05)": 5,
    "WRITE_SINGLE_REGISTER (06)": 6,
    "WRITE_MULTIPLE_COILS (15)": 15,
    "WRITE_MULTIPLE_REGISTERS (16)": 16
}

TCP_METHOD = "tcp"
RTU_METHOD = "rtu"
DEFAULT_METHOD = "default_method"
DEFAULT_MODBUS_PORT = 502

SELECT_ACTION = "Select Action"
ADD_REGISTERS = "Add Registers"
REMOVE_REGISTERS = "Remove Registers"
CONNECT = "Connect"
DISCONNECT = "Disconnect"
HIDE_DEVICE = "Hide Device"
DELETE_DEVICE = "Delete Device"

ACTION_ITEMS = [SELECT_ACTION, ADD_REGISTERS, REMOVE_REGISTERS, CONNECT, HIDE_DEVICE, DELETE_DEVICE]

SELECT_ACTION_ID = 0
ADD_REGISTERS_ID = 1
REMOVE_REGISTERS_ID = 2
CONNECT_ID = 3
HIDE_DEVICE_ID = 4
DELETE_DEVICE_ID = 5


STATUS = "status"
WIDGET = "widget"

CONNECTED = "Connected"
DISCONNECTED = "Disconnected"

LIGHT_GREEN = "rgb(144, 238, 144)"
GRAY = "rgb(219,220,220)"

MAX_DEVICES = 5
MAX_REGISTERS = 20

NO_COM_PORTS = "No COM ports available"