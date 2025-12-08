# app/led_controller.py

def send_command(serial_port, command):
    if serial_port and serial_port.is_open:
        serial_port.write((command + '\n').encode("utf-8"))
