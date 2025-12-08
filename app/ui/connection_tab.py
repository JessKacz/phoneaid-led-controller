from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from app.serial_utils import get_available_ports, connect_to_arduino

class ConnectionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.serial_port = None

        layout = QVBoxLayout()

        self.label = QLabel("Selecione a porta do Arduino:")
        layout.addWidget(self.label)

        self.port_dropdown = QComboBox()
        self.refresh_ports()
        layout.addWidget(self.port_dropdown)

        self.refresh_button = QPushButton("🔄 Atualizar portas")
        self.refresh_button.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_button)

        self.connect_button = QPushButton("Conectar")
        self.connect_button.clicked.connect(self.connect_to_selected_port)
        layout.addWidget(self.connect_button)

        self.status_label = QLabel("Status: Desconectado")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def refresh_ports(self):
        self.port_dropdown.clear()
        ports = get_available_ports()
        self.port_dropdown.addItems(ports if ports else ["Nenhuma porta encontrada"])

    def connect_to_selected_port(self):
        selected = self.port_dropdown.currentText()
        if "Nenhuma porta" in selected:
            QMessageBox.warning(self, "Erro", "Nenhuma porta selecionada.")
            return
        try:
            self.serial_port = connect_to_arduino(selected)
            self.status_label.setText(f"Status: Conectado em {selected}")
        except Exception as e:
            QMessageBox.critical(self, "Erro de conexão", str(e))
