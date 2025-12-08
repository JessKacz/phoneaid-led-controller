"""
widgets.py - Componentes customizados da UI
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QRect


class LinearLEDPreview(QWidget):
    """
    Widget que exibe a fita de LEDs passando ATRÁS das letras em alto relevo.
    
    Simula fisicamente:
    - Fita de LEDs contínua por trás
    - Letras em alto relevo (3D) na frente
    - Cores dos LEDs visíveis através das aberturas das letras
    - Preview realista do projeto físico
    """
    
    led_hovered = pyqtSignal(int)
    
    def __init__(self, total_leds=92, letter_mapping=None):
        super().__init__()
        self.total_leds = total_leds
        self.letter_mapping = letter_mapping or {}
        self.led_colors = [QColor(0, 0, 0)] * total_leds
        self.hovered_led = None
        
        self.setMinimumHeight(280)
        self.setStyleSheet("background-color: #000000;")
        self.setMouseTracking(True)
        
        # Configurações de desenho
        self.fita_height = 100
        self.fita_top = 60
        self.letra_font_size = 100
        self.letra_depth = 8  # Profundidade do efeito 3D
        
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
        """Desenha a fita de LEDs com letras em alto relevo na frente"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Fundo preto (carcaça)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Desenha a fita de LEDs POR TRÁS
        self._draw_fita_leds(painter)
        
        # Desenha as letras 3D POR CIMA (alto relevo)
        self._draw_letras_3d(painter)
        
        # Desenha hover info se necessário
        if self.hovered_led is not None:
            self._draw_hover_info(painter)
    
    def _draw_fita_leds(self, painter):
        """Desenha a fita de LEDs apenas nas regiões das letras (acompanhando o mapeamento)"""
        available_width = self.width() - 40
        led_width = available_width / self.total_leds
        x_start = 20
        y_fita = self.fita_top
        
        # Desenha a fita contínua (ajuste na largura do último LED para não perder pixels)
        for i in range(self.total_leds):
            x = x_start + i * led_width
            next_x = x_start + (i + 1) * led_width

            # Largura calculada dinamicamente para prevenir perda do último LED
            width = max(1, int(round(next_x - x)))
            rect = QRect(int(x), int(y_fita), width, self.fita_height)

            # Preenche com a cor do LED
            painter.fillRect(rect, self.led_colors[i])

            # Divisão sutil entre pixels
            painter.setPen(QPen(QColor(30, 30, 30), 0.5))
            painter.drawLine(int(x), int(y_fita), int(x), int(y_fita + self.fita_height))
        
        # Borda da fita
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.drawRect(int(x_start), int(y_fita), int(available_width), self.fita_height)
    
    def _draw_letras_3d(self, painter):
        """Desenha as letras em alto relevo (3D) sobre a fita"""
        available_width = self.width() - 40
        led_width = available_width / self.total_leds
        x_start = 20
        y_fita = self.fita_top
        
        # Font grande para as letras
        font = QFont("Arial", self.letra_font_size, QFont.Bold)
        font.setStyleStrategy(QFont.PreferAntialias)
        painter.setFont(font)
        
        # Respeita a ordem definida no mapeamento (não ordenar alfabeticamente)
        for letter, (start, end) in self.letter_mapping.items():
            if start >= self.total_leds or end >= self.total_leds:
                continue
            
            # Calcula posição da letra
            x_start_letter = x_start + start * led_width
            x_end_letter = x_start + (end + 1) * led_width
            letter_center_x = (x_start_letter + x_end_letter) / 2
            letter_center_y = y_fita + self.fita_height / 2
            letter_width = x_end_letter - x_start_letter
            
            # Desenha sombra/profundidade (efeito 3D - sombra inferior direita)
            for offset in range(1, self.letra_depth + 1):
                alpha = int(100 * (1 - offset / self.letra_depth))
                shadow_color = QColor(0, 0, 0, alpha)
                painter.setPen(shadow_color)
                painter.setFont(font)
                x_shadow = letter_center_x + offset
                y_shadow = letter_center_y + offset
                # Desenha sombra dentro da região da letra
                rect_shadow = QRect(int(x_start_letter), int(y_shadow - 40), int(letter_width), 100)
                painter.drawText(rect_shadow, Qt.AlignCenter, letter)
            
            # Desenha a letra frente iluminada
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.setFont(font)
            rect_main = QRect(int(x_start_letter), int(letter_center_y - 50), int(letter_width), 120)
            painter.drawText(rect_main, Qt.AlignCenter, letter)
            
            # Destaque na parte superior (efeito de brilho 3D)
            highlight_color = QColor(200, 200, 200)
            painter.setPen(QPen(highlight_color))
            rect_highlight = QRect(int(x_start_letter) - 2, int(letter_center_y - 52), int(letter_width), 120)
            painter.drawText(rect_highlight, Qt.AlignCenter, letter)
    
    def _draw_hover_info(self, painter):
        """Desenha informação de qual LED está sendo observado"""
        available_width = self.width() - 40
        led_width = available_width / self.total_leds
        x_start = 20
        y_fita = self.fita_top
        
        x_hover = x_start + (self.hovered_led + 0.5) * led_width
        y_top = y_fita - 30
        
        # Linha vertical indicadora em amarelo
        painter.setPen(QPen(QColor(255, 255, 0), 3))
        painter.drawLine(int(x_hover), int(y_top), int(x_hover), int(y_fita + self.fita_height + 30))
        
        # Número do LED
        text = f"LED {self.hovered_led}"
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 0)))
        
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        painter.drawText(int(x_hover - text_width / 2), int(y_top - 5), text)
    
    def mouseMoveEvent(self, event):
        """Detecta qual LED o mouse está sobre"""
        x_start = 20
        y_fita = self.fita_top
        available_width = self.width() - 40
        led_width = available_width / self.total_leds
        
        mouse_x = event.x()
        mouse_y = event.y()
        
        # Verifica se o mouse está sobre a fita
        if y_fita <= mouse_y <= y_fita + self.fita_height:
            if x_start <= mouse_x <= x_start + available_width:
                # Calcula qual LED
                led_index = int((mouse_x - x_start) / led_width)
                if 0 <= led_index < self.total_leds:
                    self.hovered_led = led_index
                    self.led_hovered.emit(led_index)
                    self.update()
                    return
        
        # Se não está sobre a fita, remove o hover
        if self.hovered_led is not None:
            self.hovered_led = None
            self.update()
    
    def leaveEvent(self, event):
        """Limpa hover ao sair do widget"""
        if self.hovered_led is not None:
            self.hovered_led = None
            self.update()


