"""
effects_tab.py - Aba de editor de efeitos com preview linear
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QColorDialog, QSlider, QSizePolicy,
    QCheckBox, QSpinBox, QMessageBox, QGroupBox
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime

from app.config_manager import load_config, save_config
from app.presets_manager import PresetsManager
from app.ui.widgets import LinearLEDPreview


class EffectsTab(QWidget):
    """
    Aba para edição de efeitos com preview linear em tempo real.
    Permite salvar até 12 presets mensais.
    """
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.total_leds = self.config.get("total_leds", 92)
        self.letter_mapping = {k.upper(): v for k, v in self.config.get("letters", {}).items()}
        
        self.presets_manager = PresetsManager()
        self.current_preset = self.presets_manager.get_active_preset()
        
        # Cores selecionadas
        self.color1 = QColor(255, 0, 0)
        self.color2 = QColor(0, 0, 255)
        
        # Estado da animação
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview_animation)
        self.wave_index = 0
        self.blink_state = True
        self.virtual_leds = [QColor(0, 0, 0) for _ in range(self.total_leds)]
        
        self._init_ui()
        self._load_preset_data()
    
    def _init_ui(self):
        """Inicializa interface"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)
        
        self.setStyleSheet("""
            QPushButton {
                min-width: 200px;
                padding: 8px;
                font-size: 13px;
                background-color: #e6f0ff;
                border: 1px solid #99c2ff;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #cce0ff;
            }
            QPushButton:disabled {
                background-color: #f2f2f2;
                color: #a6a6a6;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        
        # ===== Seção: Seleção de Preset =====
        layout.addWidget(QLabel("Selecione o efeito de luz:"))
        self.preset_selector = QComboBox()
        self.preset_selector.addItems([f"Mês {i}: {m}" for i, m in enumerate(PresetsManager.MONTHS, 1)])
        self.preset_selector.currentIndexChanged.connect(self._on_preset_changed)
        layout.addWidget(self.preset_selector)
        
        # ===== Seção: Tipo de Efeito =====
        effect_group = QGroupBox("🎨 Tipo de Efeito")
        effect_layout = QHBoxLayout()
        
        self.effect_dropdown = QComboBox()
        self.effect_dropdown.addItems(["Cor sólida", "Gradiente", "Onda"])
        self.effect_dropdown.currentIndexChanged.connect(self._on_effect_type_changed)
        self.effect_dropdown.setFixedWidth(150)
        
        effect_layout.addWidget(QLabel("Tipo:"))
        effect_layout.addWidget(self.effect_dropdown)
        effect_layout.addStretch()
        
        effect_group.setLayout(effect_layout)
        layout.addWidget(effect_group)
        
        # ===== Seção: Cores =====
        color_group = QGroupBox("🎨 Configuração de Cores")
        color_layout = QVBoxLayout()
        
        # Cor 1
        color1_row = QHBoxLayout()
        self.color1_btn = QPushButton("Selecionar Cor 1")
        self.color1_btn.clicked.connect(self._select_color1)
        self.color1_preview = QLabel()
        self.color1_preview.setFixedSize(40, 30)
        self.color1_preview.setStyleSheet("background-color: rgb(255, 0, 0); border: 2px solid #333;")
        color1_row.addWidget(self.color1_btn)
        color1_row.addWidget(self.color1_preview)
        color1_row.addStretch()
        color_layout.addLayout(color1_row)
        
        # Cor 2
        color2_row = QHBoxLayout()
        self.color2_btn = QPushButton("Selecionar Cor 2")
        self.color2_btn.clicked.connect(self._select_color2)
        self.color2_preview = QLabel()
        self.color2_preview.setFixedSize(40, 30)
        self.color2_preview.setStyleSheet("background-color: rgb(0, 0, 255); border: 2px solid #333;")
        color2_row.addWidget(self.color2_btn)
        color2_row.addWidget(self.color2_preview)
        color2_row.addStretch()
        color_layout.addLayout(color2_row)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # ===== Seção: Velocidade =====
        speed_group = QGroupBox("⚡ Velocidade")
        speed_layout = QHBoxLayout()
        
        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["Lento", "Médio", "Rápido", "Turbo"])
        self.speed_dropdown.setFixedWidth(120)
        self.speed_dropdown.currentIndexChanged.connect(self._on_preview_update)
        
        speed_layout.addWidget(QLabel("Velocidade:"))
        speed_layout.addWidget(self.speed_dropdown)
        speed_layout.addStretch()
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # ===== Seção: Largura da Onda =====
        wave_group = QGroupBox("〰️ Parâmetros da Onda")
        wave_layout = QHBoxLayout()
        
        self.wave_width_label = QLabel("Largura (LEDs):")
        self.wave_width_slider = QSlider(Qt.Horizontal)
        self.wave_width_slider.setMinimum(1)
        self.wave_width_slider.setMaximum(self.total_leds)
        self.wave_width_slider.setValue(self.total_leds // 4)
        self.wave_width_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.wave_width_slider.sliderMoved.connect(self._on_preview_update)
        
        self.wave_width_value = QLabel(str(self.wave_width_slider.value()))
        
        wave_layout.addWidget(self.wave_width_label)
        wave_layout.addWidget(self.wave_width_slider, stretch=1)
        wave_layout.addWidget(self.wave_width_value)
        
        wave_group.setLayout(wave_layout)
        self.wave_group = wave_group
        layout.addWidget(wave_group)
        
        # ===== Preview Linear =====
        preview_label = QLabel("🎬 Preview da Fita de LEDs")
        preview_label.setFont(QFont("Arial", 11, QFont.Bold))
        layout.addWidget(preview_label)
        
        self.led_preview = LinearLEDPreview(self.total_leds, self.letter_mapping)
        layout.addWidget(self.led_preview)
        
        # ===== Botões de Ação =====
        action_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("👁️ Visualizar Efeito")
        self.preview_btn.clicked.connect(self._start_animation)
        
        self.save_btn = QPushButton("💾 Salvar como Preset")
        self.save_btn.clicked.connect(self._save_preset)
        
        action_layout.addWidget(self.preview_btn)
        action_layout.addWidget(self.save_btn)
        layout.addLayout(action_layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Conecta mudanças de configuração
        self._on_effect_type_changed()
    
    def _on_preset_changed(self):
        """Carrega dados do preset selecionado"""
        mes = self.preset_selector.currentIndex() + 1
        preset = self.presets_manager.get_preset(mes)
        if preset:
            self.current_preset = preset
            self._load_preset_data()
    
    def _load_preset_data(self):
        """Carrega dados do preset atual na interface"""
        if not self.current_preset:
            return
        
        # Tipo de efeito
        effect_type = self.current_preset.get("tipo", "Cor sólida")
        index = self.effect_dropdown.findText(effect_type)
        if index >= 0:
            self.effect_dropdown.setCurrentIndex(index)
        
        # Cores
        color1_hex = self.current_preset.get("color1", "#FF0000")
        color2_hex = self.current_preset.get("color2", "#0000FF")
        self.color1 = QColor(color1_hex)
        self.color2 = QColor(color2_hex)
        self.color1_preview.setStyleSheet(f"background-color: {color1_hex}; border: 2px solid #333;")
        self.color2_preview.setStyleSheet(f"background-color: {color2_hex}; border: 2px solid #333;")
        
        # Velocidade
        speed = self.current_preset.get("velocidade", "Médio")
        index = self.speed_dropdown.findText(speed)
        if index >= 0:
            self.speed_dropdown.setCurrentIndex(index)
        
        # Largura da onda
        wave_width = self.current_preset.get("wave_width", self.total_leds // 4)
        self.wave_width_slider.setValue(wave_width)
        self.wave_width_value.setText(str(wave_width))
        
        self._on_preview_update()
    
    def _on_effect_type_changed(self):
        """Mostra/esconde controles baseado no tipo de efeito"""
        effect_type = self.effect_dropdown.currentText()
        
        # Cor 2 só aparece em Gradiente e Onda
        self.color2_btn.setVisible(effect_type in ["Gradiente", "Onda"])
        self.color2_preview.setVisible(effect_type in ["Gradiente", "Onda"])
        
        # Onda width slider só em Onda
        self.wave_group.setVisible(effect_type == "Onda")
        
        self._on_preview_update()
    
    def _on_preview_update(self):
        """Atualiza preview sem animar (parado)"""
        self.timer.stop()
        self.wave_index = 0
        self.blink_state = True
        self._generate_led_colors()
        self.led_preview.update_leds(self.virtual_leds)
    
    def _select_color1(self):
        """Abre diálogo de cor para Cor 1"""
        color = QColorDialog.getColor(self.color1, self, "Selecionar Cor 1")
        if color.isValid():
            self.color1 = color
            self.color1_preview.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #333;")
            self._on_preview_update()
    
    def _select_color2(self):
        """Abre diálogo de cor para Cor 2"""
        color = QColorDialog.getColor(self.color2, self, "Selecionar Cor 2")
        if color.isValid():
            self.color2 = color
            self.color2_preview.setStyleSheet(f"background-color: {color.name()}; border: 2px solid #333;")
            self._on_preview_update()
    
    def _start_animation(self):
        """Inicia animação do efeito"""
        self.timer.stop()
        self.wave_index = 0
        self.blink_state = True
        
        effect_type = self.effect_dropdown.currentText()
        speed_label = self.speed_dropdown.currentText()
        delay_map = {"Lento": 300, "Médio": 150, "Rápido": 70, "Turbo": 30}
        delay = delay_map.get(speed_label, 150)
        
        # Apenas Onda anima; outros efeitos são estáticos
        if effect_type == "Onda":
            self.timer.start(delay)
        else:
            self._generate_led_colors()
            self.led_preview.update_leds(self.virtual_leds)
    
    def update_preview_animation(self):
        """Chamado pelo timer para atualizar animação"""
        self._generate_led_colors()
        self.led_preview.update_leds(self.virtual_leds)
    
    def _generate_led_colors(self):
        """Gera array de cores dos LEDs baseado no efeito selecionado"""
        effect_type = self.effect_dropdown.currentText()
        
        if effect_type == "Cor sólida":
            self.virtual_leds = [self.color1] * self.total_leds
        
        elif effect_type == "Gradiente":
            self.virtual_leds = []
            for i in range(self.total_leds):
                t = i / max(1, self.total_leds - 1)
                r = int(self.color1.red() * (1 - t) + self.color2.red() * t)
                g = int(self.color1.green() * (1 - t) + self.color2.green() * t)
                b = int(self.color1.blue() * (1 - t) + self.color2.blue() * t)
                self.virtual_leds.append(QColor(r, g, b))
        
        elif effect_type == "Onda":
            wave_width = self.wave_width_slider.value()
            self.virtual_leds = []
            for i in range(self.total_leds):
                relative_pos = (i - self.wave_index) % self.total_leds
                if relative_pos < wave_width:
                    blend = 1 - (relative_pos / wave_width)
                else:
                    blend = 0
                r = int(self.color1.red() * blend + self.color2.red() * (1 - blend))
                g = int(self.color1.green() * blend + self.color2.green() * (1 - blend))
                b = int(self.color1.blue() * blend + self.color2.blue() * (1 - blend))
                self.virtual_leds.append(QColor(r, g, b))
            
            if self.timer.isActive():
                self.wave_index = (self.wave_index + 1) % self.total_leds
    
    def _save_preset(self):
        """Salva o efeito atual como preset"""
        mes = self.preset_selector.currentIndex() + 1
        
        effect_data = {
            "tipo": self.effect_dropdown.currentText(),
            "color1": self.color1.name(),
            "color2": self.color2.name(),
            "velocidade": self.speed_dropdown.currentText(),
            "wave_width": self.wave_width_slider.value(),
            "descricao": f"Efeito salvo em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        }
        
        self.presets_manager.update_preset(mes, effect_data)
        self.presets_manager.set_active_preset(mes)
        
        QMessageBox.information(
            self,
            "Sucesso",
            f"Efeito salvo no mês {mes} ({PresetsManager.MONTHS[mes-1]}) com sucesso!"
        )
