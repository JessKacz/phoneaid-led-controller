# widgets.py — preview LED com seleção ordenada + hover bonito
# Quadrados 20x20 com bordas arredondadas + info discreta abaixo

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QRect


# -----------------------------------------
# Excel-like column naming
# -----------------------------------------
def excel_column_name(n):
    name = ""
    while True:
        n, remainder = divmod(n, 26)
        name = chr(65 + remainder) + name
        if n == 0:
            break
        n -= 1
    return name


# -----------------------------------------
# LED Cell
# -----------------------------------------
class LEDCell(QWidget):
    def __init__(self, cell_id, parent_matrix):
        super().__init__()
        self.parent_matrix = parent_matrix
        self.cell_id = cell_id
        self.hover = False
        self.selected = False
        self.color = QColor(40, 40, 40)

        self.setFixedSize(20, 20)

    def set_color(self, qcolor):
        self.color = qcolor
        self.update()

    def enterEvent(self, event):
        self.hover = True
        self.update()
        self.parent_matrix._show_hover_id(self.cell_id)

    def leaveEvent(self, event):
        self.hover = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRect(0, 0, self.width(), self.height())

        # fundo — bordas arredondadas suaves
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRoundedRect(rect, 4, 4)

        # hover
        if self.hover:
            painter.setPen(QPen(QColor(255, 255, 0), 2))
            painter.drawRoundedRect(rect.adjusted(1, 1, -2, -2), 4, 4)

        # seleção
        if self.selected:
            painter.setPen(QPen(QColor(0, 255, 255), 2))
            painter.drawRoundedRect(rect.adjusted(1, 1, -2, -2), 4, 4)


# -----------------------------------------
# LED Matrix
# -----------------------------------------
class LEDMatrix(QWidget):

    def __init__(self, rows=8, cols=53):
        super().__init__()

        self.rows = rows
        self.cols = cols

        self.cells = {}
        self.selection_order = []

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        # grade
        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        main_layout.addLayout(self.grid)

        # label discreta embaixo — NUNCA mexe no tamanho da matriz
        self.label_info = QLabel(" ")
        self.label_info.setStyleSheet("""
            font-size: 10px;
            color: #666;
        """)
        self.label_info.setAlignment(Qt.AlignLeft)
        self.label_info.setMinimumHeight(16)

        main_layout.addWidget(self.label_info)

        # construir a matriz
        for r in range(rows):
            for c in range(cols):
                col_name = excel_column_name(c)
                cell_id = f"{col_name}{r+1}"

                cell = LEDCell(cell_id, parent_matrix=self)
                self.cells[cell_id] = cell

                cell.mousePressEvent = lambda e, cid=cell_id: self._click(e, cid)

                self.grid.addWidget(cell, r, c)

    # -----------------------------------------
    # Hover info no título
    # -----------------------------------------
    def _show_hover_id(self, cid):
        self.setWindowTitle(f"Hover: {cid}")

    # -----------------------------------------
    # Clique ordenado
    # -----------------------------------------
    def _click(self, event, cid):
        ctrl = event.modifiers() & Qt.ControlModifier

        if ctrl:
            if cid in self.selection_order:
                self.selection_order.remove(cid)
                self.cells[cid].selected = False
            else:
                self.selection_order.append(cid)
                self.cells[cid].selected = True
        else:
            for old in self.selection_order:
                self.cells[old].selected = False
                self.cells[old].update()

            self.selection_order = [cid]
            self.cells[cid].selected = True

        self._refresh_selection_label()

        # copiar para clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(
            self.selection_order[0]
            if len(self.selection_order) == 1
            else str(self.selection_order)
        )

        self.update()

    # -----------------------------------------
    # Atualiza info discreta
    # -----------------------------------------
    def _refresh_selection_label(self):
        if len(self.selection_order) == 0:
            self.label_info.setText(" ")
        elif len(self.selection_order) == 1:
            self.label_info.setText(f"1 LED: {self.selection_order}")
        else:
            self.label_info.setText(
                f"{len(self.selection_order)} LEDs: {self.selection_order}"
            )

    # -----------------------------------------
    # APIs futuras
    # -----------------------------------------
    def set_cell_color(self, cid, qcolor):
        if cid in self.cells:
            self.cells[cid].set_color(qcolor)

    def clear_all_colors(self):
        for c in self.cells.values():
            c.set_color(QColor(40, 40, 40))

    def apply_color_map(self, color_dict):
        for cid, col in color_dict.items():
            if cid in self.cells:
                self.cells[cid].set_color(col)

    def apply_led_array(self, array_2d):
        for r in range(self.rows):
            for c in range(self.cols):
                cid = f"{excel_column_name(c)}{r+1}"
                self.cells[cid].set_color(array_2d[r][c])
