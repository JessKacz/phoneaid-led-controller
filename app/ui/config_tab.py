from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox,
    QHBoxLayout, QGroupBox, QPushButton, QMessageBox, QToolButton
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from app.config_manager import load_config, save_config

class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.layout = QVBoxLayout()

        # Linha de título + botão de informação
        info_layout = QHBoxLayout()
        info_label = QLabel("Configurar LEDs")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(info_label)

        info_button = QToolButton()
        info_button.setIcon(QIcon("assets/info_icon.png"))  # Usando seu ícone aqui
        info_button.setIconSize(QSize(20, 20))
        info_button.setStyleSheet("QToolButton { border: none; padding-left: 5px; }")
        info_button.setToolTip(
            "Para melhores efeitos visuais (como gradiente e onda), recomenda-se que cada letra tenha entre 8 a 10 LEDs.\n"
            "Letras com poucos LEDs podem apresentar efeitos limitados ou cores pouco perceptíveis.\n"
            "Considere ajustar a quantidade de LEDs físicos na fachada para obter o efeito desejado."
        )
        info_layout.addWidget(info_button)
        info_layout.addStretch()

        self.layout.addLayout(info_layout)
        self.layout.addSpacing(10)

        # Campo de configuração do total de LEDs
        self.total_leds_box = QSpinBox()
        self.total_leds_box.setMaximum(999)
        self.total_leds_box.setValue(self.config["total_leds"])
        self.layout.addWidget(QLabel("Quantidade total de LEDs:"))
        self.layout.addWidget(self.total_leds_box)

        self.letter_boxes = {}

        # Campos de configuração de LEDs por letra
        for letter in "PHONEAID":
            group = QGroupBox(f"Letra {letter}")
            hbox = QHBoxLayout()
            start_box = QSpinBox()
            start_box.setMaximum(999)
            end_box = QSpinBox()
            end_box.setMaximum(999)
            if letter in self.config["letters"]:
                start_box.setValue(self.config["letters"][letter][0])
                end_box.setValue(self.config["letters"][letter][1])
            hbox.addWidget(QLabel("Início:"))
            hbox.addWidget(start_box)
            hbox.addWidget(QLabel("Fim:"))
            hbox.addWidget(end_box)
            group.setLayout(hbox)
            self.layout.addWidget(group)
            self.letter_boxes[letter] = (start_box, end_box)

        # Botão de salvar configuração
        self.save_btn = QPushButton("Salvar Mapeamento")
        self.save_btn.clicked.connect(self.save_config)
        self.layout.addWidget(self.save_btn)

        self.setLayout(self.layout)

    def save_config(self):
        self.config["total_leds"] = self.total_leds_box.value()
        self.config["letters"] = {
            letter: [box[0].value(), box[1].value()]
            for letter, box in self.letter_boxes.items()
        }
        save_config(self.config)
        QMessageBox.information(self, "Configuração", "Mapeamento salvo com sucesso!")
