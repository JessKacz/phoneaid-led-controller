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


def detect_arduino_ports():
    """Tenta identificar portas que parecem ser um Arduino pela descrição/VID/PID.

    Retorna lista de portas candidatas (ex: ['COM3', 'COM4']).
    """
    candidates = []
    for p in serial.tools.list_ports.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "arduino" in desc or "arduino" in hwid:
            candidates.append(p.device)
        # Detecta chips comuns (CH340, cp210x, ftdi)
        elif any(x in desc for x in ("ch340", "cp210", "ftdi", "usb serial")) or any(x in hwid for x in ("ch340", "cp210", "ftdi")):
            candidates.append(p.device)
    return candidates


def probe_port(port, baudrate=9600, timeout=1):
    """Tenta abrir a porta e verificar se ela responde minimamente.

    Estratégia:
    - Abre a porta (se possível) e aguarda por bytes durante `timeout` segundos.
    - Se abrir com sucesso e for possível ler/ escrever sem erro, considera-se válida.

    Retorna True se a porta parecer válida para uso com Arduino, False caso contrário.
    """
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
    except Exception:
        return False

    try:
        # Flush input/output
        try:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
        except Exception:
            pass

        # Tenta ler alguns bytes (caso o dispositivo emita alguma coisa)
        try:
            data = ser.read(ser.in_waiting or 1)
        except Exception:
            data = b''

        # Se conseguimos abrir a porta e não tivemos erro ao ler, consideramos a porta válida.
        ser.close()
        return True
    except Exception:
        try:
            ser.close()
        except Exception:
            pass
        return False
