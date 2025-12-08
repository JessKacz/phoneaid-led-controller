"""
connection_monitor.py - Monitor de conexão Arduino em thread background
"""
import serial
import serial.tools.list_ports
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal


class ArduinoMonitor(QObject):
    """
    Monitor que roda em thread background checando status de conexão com Arduino.
    Emite sinais quando a conexão muda de estado.
    """
    
    connection_changed = pyqtSignal(bool)  # True = conectado, False = desconectado
    status_updated = pyqtSignal(str)  # Mensagem de status atualizada
    
    def __init__(self, check_interval=2):
        super().__init__()
        self.check_interval = check_interval
        self.is_running = True
        self.current_port = None
        self.is_connected = False
        
        # Inicia thread de monitoramento
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Loop que roda em background checando conexão"""
        while self.is_running:
            try:
                self._check_connection()
            except Exception as e:
                self.status_updated.emit(f"⚠️ Erro ao checar conexão: {str(e)}")
            time.sleep(self.check_interval)
    
    def _check_connection(self):
        """Verifica se Arduino está conectado"""
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        
        if self.current_port is None:
            # Nenhuma porta selecionada
            if self.is_connected:
                self.is_connected = False
                self.connection_changed.emit(False)
                self.status_updated.emit("🔴 Nenhuma porta selecionada")
        else:
            # Temos uma porta selecionada
            if self.current_port in available_ports:
                if not self.is_connected:
                    self.is_connected = True
                    self.connection_changed.emit(True)
                    self.status_updated.emit(f"🟢 Conectado em {self.current_port}")
            else:
                if self.is_connected:
                    self.is_connected = False
                    self.connection_changed.emit(False)
                    self.status_updated.emit(f"⚪ Arduino desconectado de {self.current_port}")
                    self.current_port = None
    
    def set_port(self, port):
        """Define qual porta monitorar"""
        self.current_port = port
        self._check_connection()
    
    def get_available_ports(self):
        """Retorna lista de portas disponíveis"""
        return [p.device for p in serial.tools.list_ports.comports()]
    
    def stop(self):
        """Para o monitoramento"""
        self.is_running = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
