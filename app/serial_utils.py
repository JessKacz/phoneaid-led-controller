"""
serial_utils.py - Utilitários simplificados para comunicação serial com Arduino
"""
import serial
import serial.tools.list_ports


def get_available_ports():
    """Retorna lista de portas seriais disponíveis"""
    return [port.device for port in serial.tools.list_ports.comports()]


def open_serial_port(port, baudrate=9600, timeout=1):
    """
    Abre uma conexão serial com Arduino.
    
    Args:
        port: Nome da porta (ex: COM3, /dev/ttyUSB0)
        baudrate: Velocidade de transmissão (padrão: 9600)
        timeout: Timeout em segundos
    
    Returns:
        serial.Serial ou None se falhar
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        return ser
    except Exception as e:
        print(f"Erro ao abrir porta {port}: {e}")
        return None


def close_serial_port(ser):
    """Fecha conexão serial"""
    if ser and ser.is_open:
        ser.close()
