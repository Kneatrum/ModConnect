# Modbus Tool using Pyqt5.
Developing a user-friendly Modbus tool that helps users to interface with several Modbus slave devices at once, allowing effortless reading from and writing to their respective Modbus addresses.

# General Features
1. Connect to **multiple** Modbus TCP/IP servers.

2. Connect to **multiple** Modbus RTU servers using the RS485 communication protocols.

3. Read **coils**, **discrete inputs**, **holding registers**.

5. Write **single coil**, **multiple coils** and **single registers**.

# UI Features
1.  **Device Creation Simplification**: Streamlined process for creating Modbus devices within the application, facilitating quick setup and configuration.
    
2.  **Efficient Register Management**: Seamless integration for adding and managing registers within a device, enabling straightforward organization and access to device data.
 
3.  **Custom Device Labeling**: Ability to assign personalized labels or names to individual devices, enhancing clarity and usability when working with multiple devices.
    
4.  **Device Configuration Persistence**: Capability to save configured devices for later use, allowing users to store and recall device configurations effortlessly, thereby promoting efficiency and convenience in repetitive tasks


# Prerequisites
* Python 3.12
* Pyqt5
* pymodbus
* pyserial
* sip


# Installation

1.  Clone this repository:
 ```
 git clone https://github.com/Kneatrum/Modbus-PyQt-App.git
 ```
2. Install dependencies:
 ```
 pip install -r requirements.txt
 ```

# Usage

1. Run the application:
```
python main.py
```
