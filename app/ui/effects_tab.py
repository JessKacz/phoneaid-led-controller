from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QColorDialog, QGraphicsDropShadowEffect,
    QSlider, QSizePolicy, QCheckBox
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QTimer, Qt
from app.led_controller import send_command
from app.config_manager import load_config, save_config

class EffectsTab(QWidget):
    def __init__(self, get_serial_port):
        super().__init__()
        self.get_serial_port = get_serial_port
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(20)

        self.setStyleSheet("""
            QPushButton {
                min-width: 250px;
                max-width: 250px;
                padding: 6px;
                font-size: 16px;
                background-color: #e6f0ff;
                border: 1px solid #99c2ff;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #cce0ff;
            }
            QPushButton:disabled {
                background-color: #f2f2f2;
                color: #a6a6a6;
            }
        """)

        self.config = load_config()
        self.total_leds = self.config.get("total_leds", 70)
        self.letter_mapping = {k.upper(): v for k, v in self.config.get("letters", {}).items()}

        self.label = QLabel("Escolha o efeito de luz:")
        self.label.setFont(QFont("Arial", 12, QFont.Bold))
        self.layout.addWidget(self.label)

        self.letter_labels = []
        self.letters = "PHONEAID"
        self.letter_container = QHBoxLayout()
        for char in self.letters:
            lbl = QLabel(char)
            lbl.setFont(QFont("Arial", 42, QFont.Bold))
            lbl.setStyleSheet("color: white; padding: 10px; background-color: transparent;")
            effect = QGraphicsDropShadowEffect()
            effect.setOffset(0)
            effect.setBlurRadius(40)
            effect.setColor(QColor(0, 0, 0))
            lbl.setGraphicsEffect(effect)
            self.letter_labels.append((char.upper(), lbl, effect))
            self.letter_container.addWidget(lbl)
        self.layout.addLayout(self.letter_container)

        # Linha do tipo de efeito e checkbox piscar
        self.effect_dropdown = QComboBox()
        self.effect_dropdown.addItems(["Cor sólida", "Gradiente", "Onda"])
        self.effect_dropdown.currentIndexChanged.connect(self.update_color_inputs)
        self.effect_dropdown.setFixedWidth(200)
        self.effect_dropdown.setFixedHeight(26)
        self.effect_dropdown.setFont(QFont("Arial", 10))

        self.blink_checkbox = QCheckBox("Piscar")
        self.blink_checkbox.stateChanged.connect(self.update_color_inputs)

        self.blink_speed_dropdown = QComboBox()
        self.blink_speed_dropdown.addItems(["Lento", "Médio", "Rápido", "Turbo"])
        self.blink_speed_dropdown.setFixedWidth(120)
        self.blink_speed_dropdown.setFixedHeight(26)
        self.blink_speed_dropdown.setFont(QFont("Arial", 10))

        self.blink_alternate_checkbox = QCheckBox("Piscar Alternado")

        effect_row = QHBoxLayout()
        effect_row.setAlignment(Qt.AlignLeft)
        effect_row.addWidget(self.effect_dropdown)
        effect_row.addSpacing(10)
        effect_row.addWidget(self.blink_checkbox)
        effect_row.addSpacing(10)
        effect_row.addWidget(self.blink_speed_dropdown)
        effect_row.addSpacing(10)
        effect_row.addWidget(self.blink_alternate_checkbox)
        self.layout.addLayout(effect_row)

        self.color1_btn = QPushButton("Cor 1")
        self.color1_btn.clicked.connect(self.select_color1)
        self.color1_preview = QLabel()
        self.color1_preview.setFixedSize(30, 20)
        self.color1_preview.setStyleSheet("background-color: rgb(255, 0, 0); border: 1px solid #999;")

        self.color2_btn = QPushButton("Cor 2")
        self.color2_btn.clicked.connect(self.select_color2)
        self.color2_preview = QLabel()
        self.color2_preview.setFixedSize(30, 20)
        self.color2_preview.setStyleSheet("background-color: rgb(0, 0, 255); border: 1px solid #999;")

        self.colors_column = QVBoxLayout()
        color1_row = QHBoxLayout()
        color1_row.addWidget(self.color1_btn)
        color1_row.addWidget(self.color1_preview)
        self.colors_column.addLayout(color1_row)

        color2_row = QHBoxLayout()
        color2_row.addWidget(self.color2_btn)
        color2_row.addWidget(self.color2_preview)
        self.colors_column.addLayout(color2_row)
        self.colors_column.setSpacing(12)

        color_block = QHBoxLayout()
        color_block.setAlignment(Qt.AlignLeft)
        color_block.addLayout(self.colors_column)
        self.layout.addLayout(color_block)

        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["Lento", "Médio", "Rápido", "Turbo"])
        self.speed_dropdown.setFixedWidth(120)
        self.speed_dropdown.setFixedHeight(26)
        self.speed_dropdown.setFont(QFont("Arial", 10))
        speed_row = QHBoxLayout()
        speed_row.setAlignment(Qt.AlignLeft)
        speed_row.addWidget(self.speed_dropdown)
        self.layout.addLayout(speed_row)

        self.wave_width_label = QLabel("Largura da Onda (LEDs):")
        self.wave_width_label.setFixedHeight(24)
        self.wave_width_label.setFont(QFont("Arial", 11))

        self.wave_width_slider = QSlider(Qt.Horizontal)
        self.wave_width_slider.setMinimum(1)
        self.wave_width_slider.setMaximum(self.total_leds)
        self.wave_width_slider.setValue(self.total_leds // 2)
        self.wave_width_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        wave_row = QHBoxLayout()
        wave_row.setAlignment(Qt.AlignLeft)
        wave_row.addWidget(self.wave_width_label)
        wave_row.addSpacing(10)
        wave_row.addWidget(self.wave_width_slider, stretch=1)
        self.layout.addLayout(wave_row)

        self.visualize_btn = QPushButton("👁️ Visualizar Efeito")
        self.visualize_btn.clicked.connect(self.apply_effect)
        self.layout.addWidget(self.visualize_btn, alignment=Qt.AlignLeft)

        self.save_btn = QPushButton("💾 Salvar Efeito")
        self.save_btn.clicked.connect(self.save_effect_config)
        self.layout.addWidget(self.save_btn, alignment=Qt.AlignCenter)

        self.saved_info_label = QLabel("")
        self.saved_info_label.setFont(QFont("Arial", 8))
        self.saved_info_label.setTextFormat(Qt.RichText)
        self.layout.addWidget(self.saved_info_label)

        self.color1 = QColor(255, 0, 0)
        self.color2 = QColor(0, 0, 255)

        self.timer = QTimer()
        self.setLayout(self.layout)
        self.update_color_inputs()
        self.timer.timeout.connect(self.animate_effect_frame)

        self.current_effect = None
        self.wave_index = 0
        self.blink_state = True
        self.virtual_leds = [QColor(0, 0, 0) for _ in range(self.total_leds)]

    def update_color_inputs(self):
        effect = self.effect_dropdown.currentText()
        is_onda = effect == "Onda"
        is_grad = effect == "Gradiente"
        is_solid = effect == "Cor sólida"
        blink_enabled = is_grad or is_solid
        self.color2_btn.setVisible(effect in ["Gradiente", "Onda"])
        self.color2_preview.setVisible(effect in ["Gradiente", "Onda"])
        self.speed_dropdown.setVisible(is_onda)
        self.wave_width_label.setVisible(is_onda)
        self.wave_width_slider.setVisible(is_onda)
        self.blink_checkbox.setVisible(blink_enabled)
        self.blink_speed_dropdown.setVisible(blink_enabled and self.blink_checkbox.isChecked())
        self.blink_alternate_checkbox.setVisible(is_grad and self.blink_checkbox.isChecked())

    def select_color1(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color1 = color
            self.color1_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")

    def select_color2(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color2 = color
            self.color2_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")

    def apply_effect(self):
        self.timer.stop()
        self.wave_index = 0
        self.blink_state = True
        self.current_effect = self.effect_dropdown.currentText()

        delay = 300
        if self.blink_checkbox.isChecked():
            speed = self.blink_speed_dropdown.currentText()
            delay = 300 if speed == "Lento" else 150 if speed == "Médio" else 70 if speed == "Rápido" else 30
            self.timer.start(delay)
        elif self.current_effect == "Onda":
            speed = self.speed_dropdown.currentText()
            delay = 300 if speed == "Lento" else 150 if speed == "Médio" else 70 if speed == "Rápido" else 30
            self.timer.start(delay)
        else:
            self.animate_effect_frame()

    def animate_effect_frame(self):
        if self.current_effect == "Cor sólida":
            if self.blink_checkbox.isChecked():
                color = self.color1 if self.blink_state else QColor(0, 0, 0)
                for _, _, e in self.letter_labels:
                    e.setColor(color)
                self.blink_state = not self.blink_state
            else:
                for _, _, e in self.letter_labels:
                    e.setColor(self.color1)

        elif self.current_effect == "Gradiente":
            if self.blink_checkbox.isChecked():
                if self.blink_alternate_checkbox.isChecked():
                    color = self.color1 if self.blink_state else self.color2
                    for _, _, e in self.letter_labels:
                        e.setColor(color)
                else:
                    leds = [QColor(0, 0, 0)] * self.total_leds if not self.blink_state else []
                    if self.blink_state:
                        for i in range(self.total_leds):
                            t = i / max(1, self.total_leds - 1)
                            r = int(self.color1.red() * (1 - t) + self.color2.red() * t)
                            g = int(self.color1.green() * (1 - t) + self.color2.green() * t)
                            b = int(self.color1.blue() * (1 - t) + self.color2.blue() * t)
                            leds.append(QColor(r, g, b))
                    self.virtual_leds = leds
                    self.update_preview_from_leds()
                self.blink_state = not self.blink_state
            else:
                for i in range(self.total_leds):
                    t = i / max(1, self.total_leds - 1)
                    r = int(self.color1.red() * (1 - t) + self.color2.red() * t)
                    g = int(self.color1.green() * (1 - t) + self.color2.green() * t)
                    b = int(self.color1.blue() * (1 - t) + self.color2.blue() * t)
                    self.virtual_leds[i] = QColor(r, g, b)
                self.update_preview_from_leds()

        elif self.current_effect == "Onda":
            segment_length = self.wave_width_slider.value()
            for i in range(self.total_leds):
                relative_pos = (i - self.wave_index) % self.total_leds
                if relative_pos < segment_length:
                    blend = 1 - (relative_pos / segment_length)
                else:
                    blend = 0
                r = int(self.color1.red() * blend + self.color2.red() * (1 - blend))
                g = int(self.color1.green() * blend + self.color2.green() * (1 - blend))
                b = int(self.color1.blue() * blend + self.color2.blue() * (1 - blend))
                self.virtual_leds[i] = QColor(r, g, b)
            self.wave_index = (self.wave_index + 1) % self.total_leds
            self.update_preview_from_leds()

    def update_preview_from_leds(self):
        for char, label, effect in self.letter_labels:
            if char not in self.letter_mapping:
                continue
            start, end = self.letter_mapping[char]
            leds = self.virtual_leds[start:end+1]
            if leds:
                avg_r = sum(c.red() for c in leds) // len(leds)
                avg_g = sum(c.green() for c in leds) // len(leds)
                avg_b = sum(c.blue() for c in leds) // len(leds)
                effect.setColor(QColor(avg_r, avg_g, avg_b))

    def save_effect_config(self):
        # TODO: incluir persistência dos flags de piscar se necessário
        pass
