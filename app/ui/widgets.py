"""
widgets.py - Componentes customizados da UI
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPixmap, QRadialGradient, QPainterPath, QFontMetricsF
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
        # Optional grid positions for LEDs: dict index -> (col, row)
        self.led_grid_positions = None
        self.grid_cols = 0
        self.grid_rows = 0
        self._led_centers = {}
        self.led_radius = 12
        # Optional: positions relative to a letter bounding box {index: (fx, fy)}
        self.led_relative_positions = None
        # letter bboxes computed when drawing letters {letter: (x, y, w, h)}
        self._letter_bboxes = {}
        
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

    def set_led_grid_positions(self, positions, cols=None, rows=None):
        """Define posições 2D dos LEDs como um dicionário {index: (col, row)}.

        Se `cols`/`rows` não forem fornecidos, serão inferidos do maior valor.
        """
        if not positions:
            self.led_grid_positions = None
            self.grid_cols = 0
            self.grid_rows = 0
            self._led_centers = {}
            self.update()
            return

        self.led_grid_positions = positions.copy()
        if cols is None:
            max_col = max((c for _, (c, _) in positions.items()), default=0)
            self.grid_cols = max_col + 1
        else:
            self.grid_cols = cols

        if rows is None:
            max_row = max((r for _, (_, r) in positions.items()), default=0)
            self.grid_rows = max_row + 1
        else:
            self.grid_rows = rows

        self._led_centers = {}
        self.update()

    def set_led_relative_positions(self, positions):
        """Define posições relativas dentro da bounding box da letra: {index: (fx, fy)} onde fx,fy in [0,1].

        Essas posições são usadas preferencialmente ao invés de grid positions quando presentes.
        """
        if not positions:
            self.led_relative_positions = None
        else:
            self.led_relative_positions = positions.copy()
        self.update()
    
    def paintEvent(self, event):
        """Desenha o grid de LEDs ou a fita linear."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Fundo preto
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        # Prioridade: grid > fita linear
        if self.led_grid_positions:
            self._draw_grid_with_led_ids(painter)
        else:
            self._draw_fita_leds(painter)
        
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

    def _draw_leds_grid(self, painter):
        """Desenha LEDs como pixels numa grade com linhas visíveis."""
        available_width = self.width() - 40
        available_height = self.height() - 80
        x_start = 20
        y_start = 40

        cols = max(1, self.grid_cols)
        rows = max(1, self.grid_rows)

        # Tamanho de cada célula do grid
        cell_w = available_width / cols
        cell_h = available_height / rows
        cell_size = min(cell_w, cell_h)

        grid_w = cell_size * cols
        grid_h = cell_size * rows

        offset_x = x_start + (available_width - grid_w) / 2
        offset_y = y_start + (available_height - grid_h) / 2

        # Desenha a grade (linhas de separação entre células)
        painter.setPen(QPen(QColor(50, 50, 50), 0.5))
        for c in range(cols + 1):
            x = offset_x + c * cell_size
            painter.drawLine(int(x), int(offset_y), int(x), int(offset_y + grid_h))
        for r in range(rows + 1):
            y = offset_y + r * cell_size
            painter.drawLine(int(offset_x), int(y), int(offset_x + grid_w), int(y))

        # Desenha cada LED como um pequeno quadrado (pixel) no centro da célula
        self._led_centers = {}
        pixel_size = max(2, int(cell_size * 0.6))
        for idx in range(self.total_leds):
            pos = self.led_grid_positions.get(idx)
            if pos is None:
                continue
            col, row = pos
            cx = offset_x + col * cell_size + cell_size / 2
            cy = offset_y + row * cell_size + cell_size / 2
            self._led_centers[idx] = (cx, cy)

            color = self.led_colors[idx] if idx < len(self.led_colors) else QColor(0, 0, 0)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(20, 20, 20), 0.5))
            painter.drawRect(int(cx - pixel_size/2), int(cy - pixel_size/2), pixel_size, pixel_size)

        # Borda ao redor do grid
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(int(offset_x), int(offset_y), int(grid_w), int(grid_h))

    def _draw_grid_with_led_ids(self, painter):
        """Desenha uma grade estática com números dos LEDs nas posições cartesianas."""
        available_width = self.width() - 40
        available_height = self.height() - 80
        x_start = 20
        y_start = 40

        cols = max(1, self.grid_cols)
        rows = max(1, self.grid_rows)

        # Tamanho de cada célula
        cell_w = available_width / cols
        cell_h = available_height / rows
        cell_size = min(cell_w, cell_h)

        grid_w = cell_size * cols
        grid_h = cell_size * rows

        offset_x = x_start + (available_width - grid_w) / 2
        offset_y = y_start + (available_height - grid_h) / 2

        # Desenha a grade (linhas)
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        for c in range(cols + 1):
            x = offset_x + c * cell_size
            painter.drawLine(int(x), int(offset_y), int(x), int(offset_y + grid_h))
        for r in range(rows + 1):
            y = offset_y + r * cell_size
            painter.drawLine(int(offset_x), int(y), int(offset_x + grid_w), int(y))

        # Desenha os números dos LEDs nas posições corretas
        font = QFont("Arial", max(7, int(cell_size * 0.35)), QFont.Bold)
        painter.setFont(font)
        
        self._led_centers = {}
        for idx, (col, row) in self.led_grid_positions.items():
            cx = offset_x + col * cell_size + cell_size / 2
            cy = offset_y + row * cell_size + cell_size / 2
            self._led_centers[idx] = (cx, cy)

            # Desenha um pequeno círculo colorido
            color = self.led_colors[idx] if idx < len(self.led_colors) else QColor(50, 50, 50)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(150, 150, 150), 0.5))
            led_r = max(2, int(cell_size * 0.25))
            painter.drawEllipse(int(cx - led_r), int(cy - led_r), int(led_r * 2), int(led_r * 2))

            # Desenha o número do LED
            text = str(idx)
            fm = painter.fontMetrics()
            text_w = fm.horizontalAdvance(text)
            text_h = fm.height()
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(int(cx - text_w / 2), int(cy + text_h / 3), text)

        # Borda ao redor da grade
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawRect(int(offset_x), int(offset_y), int(grid_w), int(grid_h))

    def _draw_leds_relative(self, painter):
        """Desenha LEDs como círculos em posições relativas dentro da bounding box da letra."""
        if not self.led_relative_positions or not self._letter_bboxes:
            return

        # assume single letter preview (first mapping key)
        letter = next(iter(self.letter_mapping.keys())) if self.letter_mapping else None
        if not letter or letter not in self._letter_bboxes:
            return

        bx, by, bw, bh = self._letter_bboxes[letter]
        self._led_centers = {}

        for idx, (fx, fy) in self.led_relative_positions.items():
            if idx >= len(self.led_colors):
                continue
            cx = bx + fx * bw
            cy = by + fy * bh
            self._led_centers[idx] = (cx, cy)

            color = self.led_colors[idx]
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(50, 50, 50), 1))
            r = max(6, int(min(bw, bh) * 0.08))
            painter.drawEllipse(int(cx - r), int(cy - r), int(2 * r), int(2 * r))

            # small highlight
            highlight = QColor(255, 255, 255, 90)
            painter.setBrush(QBrush(highlight))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(cx - r/3), int(cy - r/3), int(r/1.5), int(r/1.5))

    def _compute_letter_bboxes(self, painter):
        """Compute and store bounding boxes for letters without drawing them.

        This mirrors the logic used in `_draw_letras_3d` to compute letter positions.
        """
        self._letter_bboxes = {}
        available_width = self.width() - 40
        led_width = available_width / max(1, self.total_leds)
        x_start = 20
        y_fita = self.fita_top

        font = QFont("Arial", self.letra_font_size, QFont.Bold)
        fm = QFontMetricsF(font)

        for letter, (start, end) in self.letter_mapping.items():
            if start >= self.total_leds or end >= self.total_leds:
                continue
            if self.led_grid_positions:
                cols = [c for i, (c, r) in self.led_grid_positions.items() if start <= i <= end]
                rows = [r for i, (c, r) in self.led_grid_positions.items() if start <= i <= end]
                if cols and rows:
                    min_col = min(cols)
                    max_col = max(cols)
                    min_row = min(rows)
                    max_row = max(rows)

                    available_height = self.height() - 80
                    cell_w = available_width / max(1, self.grid_cols)
                    cell_h = available_height / max(1, self.grid_rows)
                    cell_size = min(cell_w, cell_h)

                    x_start_letter = 20 + (available_width - cell_size * self.grid_cols) / 2 + min_col * cell_size
                    x_end_letter = 20 + (available_width - cell_size * self.grid_cols) / 2 + (max_col + 1) * cell_size
                    letter_center_x = (x_start_letter + x_end_letter) / 2
                    letter_center_y = 40 + (available_height - cell_size * self.grid_rows) / 2 + (min_row + max_row + 1) / 2 * cell_size
                    letter_width = x_end_letter - x_start_letter
                else:
                    continue
            else:
                x_start_letter = x_start + start * led_width
                x_end_letter = x_start + (end + 1) * led_width
                letter_center_x = (x_start_letter + x_end_letter) / 2
                letter_center_y = y_fita + self.fita_height / 2
                letter_width = x_end_letter - x_start_letter

            total_h = fm.ascent() + fm.descent()
            bbox_x = x_start_letter
            bbox_y = letter_center_y - total_h / 2
            bbox_w = letter_width
            bbox_h = total_h
            self._letter_bboxes[letter] = (bbox_x, bbox_y, bbox_w, bbox_h)

    def _compute_led_centers(self):
        """Populate `_led_centers` based on current positioning mode without drawing."""
        self._led_centers = {}
        if self.led_relative_positions and self._letter_bboxes:
            # use first letter bbox
            letter = next(iter(self.letter_mapping.keys())) if self.letter_mapping else None
            if not letter or letter not in self._letter_bboxes:
                return
            bx, by, bw, bh = self._letter_bboxes[letter]
            for idx, (fx, fy) in self.led_relative_positions.items():
                cx = bx + fx * bw
                cy = by + fy * bh
                self._led_centers[idx] = (cx, cy)
        elif self.led_grid_positions:
            # compute centers based on grid
            available_width = self.width() - 40
            available_height = self.height() - 80
            x_start = 20
            y_start = 40
            cols = max(1, self.grid_cols)
            rows = max(1, self.grid_rows)
            cell_w = available_width / cols
            cell_h = available_height / rows
            cell_size = min(cell_w, cell_h)
            grid_w = cell_size * cols
            grid_h = cell_size * rows
            offset_x = x_start + (available_width - grid_w) / 2
            offset_y = y_start + (available_height - grid_h) / 2
            for idx in range(self.total_leds):
                pos = self.led_grid_positions.get(idx)
                if pos is None:
                    continue
                col, row = pos
                cx = offset_x + col * cell_size + cell_size / 2
                cy = offset_y + row * cell_size + cell_size / 2
                self._led_centers[idx] = (cx, cy)
        else:
            # linear tape
            available_width = self.width() - 40
            led_width = available_width / max(1, self.total_leds)
            x_start = 20
            y_fita = self.fita_top
            for i in range(self.total_leds):
                x = x_start + i * led_width + led_width / 2
                y = y_fita + self.fita_height / 2
                self._led_centers[i] = (x, y)

    def _draw_glow_layer(self, painter):
        """Renderiza um layer offscreen com glows radiais por LED e pinta sobre o widget."""
        # prefer relative positions when available
        use_relative = bool(self.led_relative_positions and self._letter_bboxes)

        if not self._led_centers and not use_relative:
            return

        size = self.size()
        glow_pix = QPixmap(size)
        glow_pix.fill(Qt.transparent)

        p = QPainter(glow_pix)
        p.setRenderHint(QPainter.Antialiasing)

        # Calcula raio base a partir do tamanho da célula do grid
        available_width = self.width() - 40
        cols = max(1, self.grid_cols)
        cell_w = available_width / cols if cols else 40
        glow_radius = int(max(15, min(50, cell_w * 0.7)))

        if use_relative:
            # map relative positions inside the first letter bbox (we focus on single-letter preview)
            # choose the first letter in mapping
            letter = next(iter(self.letter_mapping.keys())) if self.letter_mapping else None
            if letter and letter in self._letter_bboxes:
                bx, by, bw, bh = self._letter_bboxes[letter]
                for idx, (fx, fy) in self.led_relative_positions.items():
                    if idx >= len(self.led_colors):
                        continue
                    cx = bx + fx * bw
                    cy = by + fy * bh
                    col = self.led_colors[idx]
                    center_color = QColor(col.red(), col.green(), col.blue(), 200)
                    grad = QRadialGradient(cx, cy, glow_radius)
                    grad.setColorAt(0.0, center_color)
                    grad.setColorAt(0.6, QColor(center_color.red(), center_color.green(), center_color.blue(), 120))
                    grad.setColorAt(1.0, QColor(0, 0, 0, 0))
                    p.setBrush(QBrush(grad))
                    p.setPen(Qt.NoPen)
                    p.drawEllipse(int(cx - glow_radius), int(cy - glow_radius), int(glow_radius * 2), int(glow_radius * 2))
        else:
            for idx, (cx, cy) in self._led_centers.items():
                if idx >= len(self.led_colors):
                    continue
                col = self.led_colors[idx]
                center_color = QColor(col.red(), col.green(), col.blue(), 200)
                grad = QRadialGradient(cx, cy, glow_radius)
                grad.setColorAt(0.0, center_color)
                grad.setColorAt(0.6, QColor(center_color.red(), center_color.green(), center_color.blue(), 120))
                grad.setColorAt(1.0, QColor(0, 0, 0, 0))

                p.setBrush(QBrush(grad))
                p.setPen(Qt.NoPen)
                p.drawEllipse(int(cx - glow_radius), int(cy - glow_radius), int(glow_radius * 2), int(glow_radius * 2))

        p.end()

        # desenha o pixmap com normal compositing (glow pode ultrapassar letras)
        painter.drawPixmap(0, 0, glow_pix)
    
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
            if self.led_grid_positions:
                # calcula bounding box a partir dos centros do grid
                cols = [c for i, (c, r) in self.led_grid_positions.items() if start <= i <= end]
                rows = [r for i, (c, r) in self.led_grid_positions.items() if start <= i <= end]
                if cols and rows:
                    min_col = min(cols)
                    max_col = max(cols)
                    min_row = min(rows)
                    max_row = max(rows)

                    available_width = self.width() - 40
                    available_height = self.height() - 80
                    cell_w = available_width / max(1, self.grid_cols)
                    cell_h = available_height / max(1, self.grid_rows)
                    cell_size = min(cell_w, cell_h)

                    x_start_letter = 20 + (available_width - cell_size * self.grid_cols) / 2 + min_col * cell_size
                    x_end_letter = 20 + (available_width - cell_size * self.grid_cols) / 2 + (max_col + 1) * cell_size
                    letter_center_x = (x_start_letter + x_end_letter) / 2
                    letter_center_y = 40 + (available_height - cell_size * self.grid_rows) / 2 + (min_row + max_row + 1) / 2 * cell_size
                    letter_width = x_end_letter - x_start_letter
                    # compute approximate letter bbox for relative positioning
                    fm = QFontMetricsF(font)
                    total_h = fm.ascent() + fm.descent()
                    bbox_x = x_start_letter
                    bbox_y = letter_center_y - total_h / 2
                    bbox_w = letter_width
                    bbox_h = total_h
                    self._letter_bboxes[letter] = (bbox_x, bbox_y, bbox_w, bbox_h)
                else:
                    continue
            else:
                x_start_letter = x_start + start * led_width
                x_end_letter = x_start + (end + 1) * led_width
                letter_center_x = (x_start_letter + x_end_letter) / 2
                letter_center_y = y_fita + self.fita_height / 2
                letter_width = x_end_letter - x_start_letter
                # compute bbox for linear mode as well
                fm = QFontMetricsF(font)
                total_h = fm.ascent() + fm.descent()
                bbox_x = x_start_letter
                bbox_y = letter_center_y - total_h / 2
                bbox_w = letter_width
                bbox_h = total_h
                self._letter_bboxes[letter] = (bbox_x, bbox_y, bbox_w, bbox_h)
            
            # Se estivermos em modo grid, desenhar apenas o contorno (stroke) da letra
            if self.led_grid_positions:
                # cria um path com o texto para poder desenhar o traço (stroke) sem preencher
                path = QPainterPath()
                # calcula baseline para centralizar o texto
                fm = QFontMetricsF(font)
                text_width = fm.horizontalAdvance(letter)
                ascent = fm.ascent()
                descent = fm.descent()
                total_h = ascent + descent
                baseline_x = letter_center_x - text_width / 2
                baseline_y = letter_center_y + (ascent - total_h / 2)
                path.addText(baseline_x, baseline_y, font, letter)

                # desenha sombra/offset leve atrás do contorno para profundidade
                for offset in range(1, 3):
                    shadow_path = QPainterPath()
                    shadow_path.addText(baseline_x + offset, baseline_y + offset, font, letter)
                    painter.setPen(QPen(QColor(0, 0, 0, 80), 6))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(shadow_path)

                # desenha o traço principal (contorno) por cima
                painter.setPen(QPen(QColor(255, 255, 255), 3))
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
            else:
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
        # If grid mode, use cached centers
        if self.led_grid_positions and self._led_centers.get(self.hovered_led):
            cx, cy = self._led_centers[self.hovered_led]
            x_hover = cx
            y_top = int(cy - 30)
            y_bottom = int(cy + self.led_radius)
        else:
            available_width = self.width() - 40
            led_width = available_width / self.total_leds
            x_start = 20
            y_fita = self.fita_top
            x_hover = x_start + (self.hovered_led + 0.5) * led_width
            y_top = y_fita - 30
            y_bottom = int(y_fita + self.fita_height)
        
        # Linha vertical indicadora em amarelo
        painter.setPen(QPen(QColor(255, 255, 0), 3))
        painter.drawLine(int(x_hover), int(y_top), int(x_hover), int(y_bottom + 30))
        
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
        mouse_x = event.x()
        mouse_y = event.y()

        if self.led_grid_positions and self._led_centers:
            # encontra o LED mais próximo dentro de raio
            nearest = None
            nearest_dist = None
            for idx, (cx, cy) in self._led_centers.items():
                dx = mouse_x - cx
                dy = mouse_y - cy
                d2 = dx * dx + dy * dy
                if nearest is None or d2 < nearest_dist:
                    nearest = idx
                    nearest_dist = d2
            if nearest is not None and nearest_dist <= (self.led_radius * 1.5) ** 2:
                if self.hovered_led != nearest:
                    self.hovered_led = nearest
                    self.led_hovered.emit(nearest)
                    self.update()
                return

        # Fallback linear detection
        x_start = 20
        y_fita = self.fita_top
        available_width = self.width() - 40
        led_width = available_width / self.total_leds

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


