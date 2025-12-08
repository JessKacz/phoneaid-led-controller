"""
widgets.py - Componentes customizados da UI
"""
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, pyqtSignal


class LinearLEDPreview(QWidget):
    """
    Widget que exibe a fita de LEDs como uma linha contínua com overlay das letras.
    
    Mostra:
    - Fita linear de LEDs (círculos coloridos)
    - Overlay das letras com ranges (ex: P:00-05)
    - Hover para mostrar número do LED
    """
    
    led_hovered = pyqtSignal(int)  # Emite índice do LED ao fazer hover
    
    def __init__(self, total_leds=92, letter_mapping=None):
        super().__init__()
        self.total_leds = total_leds
        self.letter_mapping = letter_mapping or {}
        self.led_colors = [QColor(0, 0, 0)] * total_leds
        self.hovered_led = None
        
        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #1a1a1a; border-radius: 8px;")
        self.setMouseTracking(True)
        
        # Configurações de desenho
        self.led_diameter = 16
        self.led_spacing = 3
        self.top_margin = 30
        self.label_height = 40
        
    def update_leds(self, colors):
        """Atualiza as cores dos LEDs"""
        if len(colors) == self.total_leds:
            self.led_colors = colors.copy()
            self.update()
    
    def set_total_leds(self, total):
        """Altera a quantidade total de LEDs"""
        self.total_leds = total
        self.led_colors = [QColor(0, 0, 0)] * total
        self.update()
    
    def set_letter_mapping(self, mapping):
        """Atualiza o mapeamento de letras"""
        self.letter_mapping = mapping
        self.update()
    
    def paintEvent(self, event):
        """Desenha a fita linear com overlay das letras"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenha fundo escuro
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        # Calcula posição inicial (centralizado horizontalmente)
        total_width = self.total_leds * (self.led_diameter + self.led_spacing)
        x_offset = max(10, (self.width() - total_width) // 2)
        y_center = self.top_margin
        
        # Desenha cada LED como círculo
        for i, color in enumerate(self.led_colors):
            x = x_offset + i * (self.led_diameter + self.led_spacing)
            y = y_center
            
            # Desenha LED
            painter.fillEllipse(x, y, self.led_diameter, self.led_diameter)
            painter.setBrush(color)
            
            # Contorno do LED (cinza escuro)
            painter.setPen(QPen(QColor(60, 60, 60), 1))
            painter.drawEllipse(x, y, self.led_diameter, self.led_diameter)
            
            # Highlight se está fazendo hover
            if self.hovered_led == i:
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                painter.drawEllipse(x - 2, y - 2, self.led_diameter + 4, self.led_diameter + 4)
        
        # Desenha linha conectando os LEDs
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        for i in range(self.total_leds - 1):
            x1 = x_offset + i * (self.led_diameter + self.led_spacing) + self.led_diameter / 2
            x2 = x_offset + (i + 1) * (self.led_diameter + self.led_spacing) + self.led_diameter / 2
            y_line = y_center + self.led_diameter / 2
            painter.drawLine(int(x1), int(y_line), int(x2), int(y_line))
        
        # Desenha overlay das letras e ranges
        self._draw_letter_overlays(painter, x_offset, y_center)
        
        # Mostra informação do LED em hover
        if self.hovered_led is not None:
            self._draw_led_tooltip(painter, x_offset, y_center)
    
    def _draw_letter_overlays(self, painter, x_offset, y_led):
        """Desenha as caixas e rótulos das letras"""
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        
        for letter, (start, end) in sorted(self.letter_mapping.items()):
            if start >= self.total_leds or end >= self.total_leds:
                continue
            
            x1 = x_offset + start * (self.led_diameter + self.led_spacing) - 5
            x2 = x_offset + (end + 1) * (self.led_diameter + self.led_spacing)
            y_rect = y_led + self.led_diameter + 10
            height = 35
            
            # Desenha caixa semitransparente
            painter.fillRect(int(x1), int(y_rect), int(x2 - x1), int(height), 
                           QColor(100, 150, 200, 60))
            
            # Contorno da caixa
            painter.setPen(QPen(QColor(100, 150, 200), 1))
            painter.drawRect(int(x1), int(y_rect), int(x2 - x1), int(height))
            
            # Rótulo da letra com range (ex: P:00-05)
            label = f"{letter}\n{start:02d}-{end:02d}"
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(int(x1) + 3, int(y_rect) + 3, int(x2 - x1) - 6, int(height) - 3,
                           Qt.AlignCenter, label)
    
    def _draw_led_tooltip(self, painter, x_offset, y_led):
        """Desenha tooltip com número do LED no hover"""
        x = x_offset + self.hovered_led * (self.led_diameter + self.led_spacing) + self.led_diameter / 2
        y = y_led - 25
        
        # Texto
        text = f"LED {self.hovered_led:02d}"
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        
        # Fundo do tooltip
        painter.fillRect(int(x) - 25, int(y), 50, 18, QColor(40, 40, 40))
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(int(x) - 25, int(y), 50, 18)
        
        # Texto
        painter.setPen(QColor(255, 255, 100))
        painter.drawText(int(x) - 25, int(y), 50, 18, Qt.AlignCenter, text)
    
    def mouseMoveEvent(self, event):
        """Detecta qual LED o mouse está sobre"""
        x_offset = max(10, (self.width() - self.total_leds * (self.led_diameter + self.led_spacing)) // 2)
        y_led = self.top_margin
        
        mouse_x = event.x()
        mouse_y = event.y()
        
        # Verifica se o mouse está na área dos LEDs
        if y_led <= mouse_y <= y_led + self.led_diameter:
            # Calcula qual LED
            led_index = (mouse_x - x_offset) / (self.led_diameter + self.led_spacing)
            
            if 0 <= led_index < self.total_leds:
                self.hovered_led = int(led_index)
                self.led_hovered.emit(self.hovered_led)
                self.update()
                return
        
        if self.hovered_led is not None:
            self.hovered_led = None
            self.update()
    
    def leaveEvent(self, event):
        """Remove hover ao sair do widget"""
        if self.hovered_led is not None:
            self.hovered_led = None
            self.update()
