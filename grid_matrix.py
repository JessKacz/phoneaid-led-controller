from PyQt5.QtWidgets import (
    QWidget, QApplication, QGridLayout
)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt
import sys

# ------------------------------------------------
# Função para gerar nomes de colunas estilo Excel
# ------------------------------------------------
def excel_column_name(n):
    name = ""
    while True:
        n, remainder = divmod(n, 26)
        name = chr(65 + remainder) + name
        if n == 0:
            break
        n -= 1
    return name

# ------------------------------------------------
# Widget da célula
# ------------------------------------------------
class CellWidget(QWidget):
    def __init__(self, cell_id):
        super().__init__()
        self.cell_id = cell_id
        self.setFixedSize(20, 20)
        self.hover = False
        self.selected = False
        self.fill_color = QColor(40, 40, 40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # fundo
        painter.setBrush(QBrush(self.fill_color))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(0, 0, self.width(), self.height())

        # hover highlight
        if self.hover:
            painter.setPen(QPen(QColor(255, 255, 0), 2))
            painter.drawRect(1, 1, self.width() - 3, self.height() - 3)

        # seleção (ciano)
        if self.selected:
            painter.setPen(QPen(QColor(0, 255, 255), 2))
            painter.drawRect(1, 1, self.width() - 3, self.height() - 3)

    def enterEvent(self, event):
        self.hover = True
        self.update()

    def leaveEvent(self, event):
        self.hover = False
        self.update()

# ------------------------------------------------
# Widget da Matriz
# ------------------------------------------------
class GridMatrix(QWidget):
    def __init__(self, rows=8, cols=53):
        super().__init__()
        self.setWindowTitle("PhoneAid LED Matrix Preview")
        self.rows = rows
        self.cols = cols
        self.resize(900, 300)

        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        self.setLayout(self.grid)

        self.cells = {}
        self.selection_order = []  # <<< ORDEM REAL DA SELEÇÃO

        # cria células
        for x in range(rows):
            for y in range(cols):
                col_name = excel_column_name(y)
                cell_id = f"{col_name}{x+1}"

                cell = CellWidget(cell_id)
                self.cells[cell_id] = cell

                cell.mousePressEvent = lambda e, cid=cell_id: self.on_click(e, cid)
                cell.enterEvent = lambda e, cid=cell_id, c=cell: self.on_hover(e, cid, c)

                self.grid.addWidget(cell, x, y)

    # ----------------------------------------
    # Hover → exibir ID no título da janela
    # ----------------------------------------
    def on_hover(self, event, cell_id, cell_widget):
        cell_widget.hover = True
        cell_widget.update()
        self.setWindowTitle(f"Cell: {cell_id}")

    # ----------------------------------------
    # Clique → seleciona / multi-seleciona
    # ----------------------------------------
    def on_click(self, event, cell_id):
        ctrl = event.modifiers() & Qt.ControlModifier

        if ctrl:
            # toggle
            if cell_id in self.selection_order:
                self.selection_order.remove(cell_id)
                self.cells[cell_id].selected = False
            else:
                self.selection_order.append(cell_id)
                self.cells[cell_id].selected = True

        else:
            # clique simples: limpa tudo e deixa só 1
            for cid in self.selection_order:
                self.cells[cid].selected = False

            self.selection_order = [cell_id]
            self.cells[cell_id].selected = True

        # atualizar estilos
        for cid in self.cells:
            self.cells[cid].update()

        # copiar na ordem EXATA
        clipboard = QApplication.clipboard()
        if len(self.selection_order) == 1:
            clipboard.setText(self.selection_order[0])
        else:
            clipboard.setText(str(self.selection_order))

        self.update()

# ------------------------------------------------
# LAUNCHER
# ------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = GridMatrix()
    w.show()
    sys.exit(app.exec_())
