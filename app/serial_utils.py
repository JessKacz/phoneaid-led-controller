# app/serial_utils.py

import serial
import serial.tools.list_ports

def get_available_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_to_arduino(port, baudrate=9600):
    return serial.Serial(port, baudrate, timeout=1)
