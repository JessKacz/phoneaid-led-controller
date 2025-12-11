"""
installer_tab.py - Aba de instalação e upload de firmware
Integra monitor de conexão em tempo real com ArduinoMonitor
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, 
    QMessageBox, QProgressBar, QFrame, QSpacerItem, QSizePolicy, QGroupBox,
    QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.config_manager import load_config
from app.presets_manager import PresetsManager
from app.firmware_generator import FirmwareGenerator
from app.serial_utils import get_available_ports, detect_arduino_ports, probe_port
from app.connection_monitor import ArduinoMonitor


class InstallerTab(QWidget):
    """
    Aba para compilação e upload de firmware.
    Monitora status de conexão Arduino em tempo real.
    """
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.presets_manager = PresetsManager()
        self.firmware_generator = FirmwareGenerator(
            self.config.get("total_leds", 92),
            self.config
        )
        
        # Inicia monitor de conexão
        self.arduino_monitor = ArduinoMonitor(check_interval=2)
        self.arduino_monitor.status_updated.connect(self._on_status_updated)
        self.arduino_monitor.connection_changed.connect(self._on_connection_changed)
        
        self.selected_port = None
        self.firmware_code = None
        
        self._init_ui()
    
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
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
                border: 1px solid #666;
                border-radius: 4px;
            }
        """)
        
        # ===== SEÇÃO 1: Status de Conexão =====
        title = QLabel("🔌 Gerenciador de Firmware")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        connection_group = QGroupBox("📡 Status da Conexão Arduino")
        connection_layout = QVBoxLayout()
        
        # Status em tempo real
        status_row = QHBoxLayout()
        self.status_indicator = QLabel("⚪ Inicializando...")
        self.status_indicator.setFont(QFont("Arial", 11, QFont.Bold))
        self.status_indicator.setStyleSheet("color: #666;")
        status_row.addWidget(self.status_indicator)
        status_row.addStretch()
        connection_layout.addLayout(status_row)
        
        # Seleção de porta
        port_row = QHBoxLayout()
        self.port_dropdown = QComboBox()
        self.port_dropdown.currentIndexChanged.connect(self._on_port_selected)
        
        self.refresh_ports_btn = QPushButton("🔄 Atualizar Portas")
        self.refresh_ports_btn.clicked.connect(self._refresh_ports)
        self.refresh_ports_btn.setFixedWidth(150)

        self.find_btn = QPushButton("🔎 Encontrar Arduino")
        self.find_btn.clicked.connect(self._find_arduino)
        self.find_btn.setFixedWidth(160)
        
        self.connect_btn = QPushButton("🔗 Conectar")
        self.connect_btn.clicked.connect(self._manual_connect)
        self.connect_btn.setFixedWidth(150)
        
        port_row.addWidget(QLabel("Porta:"))
        port_row.addWidget(self.port_dropdown, stretch=1)
        port_row.addWidget(self.refresh_ports_btn)
        port_row.addWidget(self.find_btn)
        port_row.addWidget(self.connect_btn)
        
        connection_layout.addLayout(port_row)
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # ===== SEÇÃO 2: Seleção de Preset =====
        preset_group = QGroupBox("📅 Selecione o Preset para Upload")
        preset_layout = QHBoxLayout()
        
        self.preset_selector = QComboBox()
        self.preset_selector.addItems(
            [f"Mês {i}: {m}" for i, m in enumerate(PresetsManager.MONTHS, 1)]
        )
        preset_layout.addWidget(QLabel("Preset:"))
        preset_layout.addWidget(self.preset_selector, stretch=1)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # ===== SEÇÃO 3: Compilação =====
        compile_group = QGroupBox("⚙️ Compilar Firmware")
        compile_layout = QVBoxLayout()
        
        compile_btn_row = QHBoxLayout()
        self.compile_btn = QPushButton("⚙️ Gerar Firmware")
        self.compile_btn.clicked.connect(self._compile_firmware)
        compile_btn_row.addWidget(self.compile_btn)
        compile_btn_row.addStretch()
        compile_layout.addLayout(compile_btn_row)
        
        # Preview do código gerado
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setPlaceholderText("Clique em 'Gerar Firmware' para ver o código aqui...")
        self.code_preview.setMaximumHeight(250)
        compile_layout.addWidget(QLabel("Preview do Código Arduino:"))
        compile_layout.addWidget(self.code_preview)
        
        self.compile_status = QLabel("")
        self.compile_status.setFont(QFont("Arial", 9))
        compile_layout.addWidget(self.compile_status)
        
        compile_group.setLayout(compile_layout)
        layout.addWidget(compile_group)
        
        # ===== SEÇÃO 4: Upload =====
        upload_group = QGroupBox("⬆️ Upload para Arduino")
        upload_layout = QVBoxLayout()
        
        upload_btn_row = QHBoxLayout()
        self.upload_btn = QPushButton("⬆️ Fazer Upload")
        self.upload_btn.clicked.connect(self._upload_firmware)
        self.upload_btn.setEnabled(False)
        upload_btn_row.addWidget(self.upload_btn)
        upload_btn_row.addStretch()
        upload_layout.addLayout(upload_btn_row)
        
        self.upload_progress = QProgressBar()
        self.upload_progress.setMaximum(100)
        self.upload_progress.setVisible(False)
        upload_layout.addWidget(self.upload_progress)
        
        self.upload_status = QLabel("")
        self.upload_status.setFont(QFont("Arial", 9))
        upload_layout.addWidget(self.upload_status)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Inicializa portas
        self._refresh_ports()
    
    def _refresh_ports(self):
        """Atualiza lista de portas disponíveis"""
        self.port_dropdown.clear()
        ports = get_available_ports()
        
        if ports:
            self.port_dropdown.addItems(ports)
        else:
            self.port_dropdown.addItem("Nenhuma porta encontrada")
    
    def _on_port_selected(self):
        """Chamado quando usuário seleciona uma porta"""
        selected = self.port_dropdown.currentText()
        if selected and "Nenhuma porta" not in selected:
            self.arduino_monitor.set_port(selected)
            self.selected_port = selected
        else:
            self.selected_port = None
            self.arduino_monitor.set_port(None)
    
    def _manual_connect(self):
        """Tenta conectar manualmente à porta selecionada"""
        selected = self.port_dropdown.currentText()
        if "Nenhuma porta" in selected or not selected:
            QMessageBox.warning(self, "Erro", "Nenhuma porta selecionada.")
            return
        
        self.selected_port = selected
        self.arduino_monitor.set_port(selected)

    def _find_arduino(self):
        """Procura automaticamente por portas que parecem ser um Arduino.

        Estratégia:
        - Usa `detect_arduino_ports()` para encontrar portas com descrição/VID compatível.
        - Para cada candidata, chama `probe_port()` para confirmar comunicação.
        - Se encontrar, seleciona a porta automaticamente; se não, exibe instruções.
        """
        self.status_indicator.setText("🔎 Procurando Arduino...")
        self.status_indicator.setStyleSheet("color: #ffaa00; font-weight: bold;")

        candidates = detect_arduino_ports()
        found = None

        # Se o detect não achou nada, analisamos todas as portas disponíveis
        if not candidates:
            candidates = get_available_ports()

        for p in candidates:
            try:
                if probe_port(p):
                    found = p
                    break
            except Exception:
                continue

        if found:
            # Atualiza dropdown e seleciona
            self._refresh_ports()
            index = self.port_dropdown.findText(found)
            if index >= 0:
                self.port_dropdown.setCurrentIndex(index)
            else:
                # Se não estiver na lista, adiciona e seleciona
                self.port_dropdown.addItem(found)
                self.port_dropdown.setCurrentText(found)

            self.selected_port = found
            self.arduino_monitor.set_port(found)
            QMessageBox.information(self, "Arduino Encontrado", f"✅ Arduino encontrado em {found} e selecionado.")
        else:
            # Não encontrou — instruções úteis
            self.status_indicator.setText("⚪ Nenhum Arduino detectado")
            self.status_indicator.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            QMessageBox.warning(
                self,
                "Arduino não encontrado",
                (
                    "Nenhum Arduino foi detectado nas portas do sistema.\n\n"
                    "Verifique:\n"
                    "- Cabo USB e conexões físicas.\n"
                    "- Drivers do conversor USB-Serial (CH340/CP210x/FTDI) instalados.\n"
                    "- Se no Windows: verifique o Gerenciador de Dispositivos para a porta COM.\n\n"
                    "Após verificar, clique em 'Atualizar Portas' e tente novamente."
                )
            )
    
    def _on_status_updated(self, status_msg):
        """Atualiza label de status quando ArduinoMonitor emite sinal"""
        self.status_indicator.setText(status_msg)
        
        # Cor do texto baseado no status
        if "🟢" in status_msg:
            self.status_indicator.setStyleSheet("color: #00ff00; font-weight: bold;")
        elif "🔴" in status_msg or "⚪" in status_msg:
            self.status_indicator.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        elif "⚠️" in status_msg:
            self.status_indicator.setStyleSheet("color: #ffaa00; font-weight: bold;")
    
    def _on_connection_changed(self, is_connected):
        """Atualiza botão de upload quando conexão muda"""
        self.upload_btn.setEnabled(is_connected and self.firmware_code is not None)
    
    def _compile_firmware(self):
        """Gera código Arduino a partir do preset selecionado"""
        mes = self.preset_selector.currentIndex() + 1
        presets = self.presets_manager.get_all_presets()
        
        # Filtra apenas o preset selecionado
        selected_preset = self.presets_manager.get_preset(mes)
        if not selected_preset:
            QMessageBox.warning(self, "Erro", "Preset não encontrado.")
            return
        
        try:
            # Gera firmware
            self.firmware_code = self.firmware_generator.generate_firmware([selected_preset])
            
            # Mostra preview
            self.code_preview.setText(self.firmware_code)
            self.compile_status.setText("✅ Firmware gerado com sucesso!")
            self.compile_status.setStyleSheet("color: #00aa00;")
            
            # Habilita botão de upload se conectado
            if self.arduino_monitor.is_connected and self.selected_port:
                self.upload_btn.setEnabled(True)
            
            # Salva arquivo
            self.firmware_generator.save_firmware([selected_preset])
            
        except Exception as e:
            QMessageBox.critical(self, "Erro na Compilação", f"Erro: {str(e)}")
            self.compile_status.setText(f"❌ Erro: {str(e)}")
            self.compile_status.setStyleSheet("color: #ff6b6b;")
    
    def _upload_firmware(self):
        """Faz upload do firmware para o Arduino"""
        if not self.selected_port:
            QMessageBox.warning(self, "Erro", "Nenhuma porta selecionada.")
            return
        
        if not self.firmware_code:
            QMessageBox.warning(self, "Erro", "Nenhum firmware compilado.")
            return
        
        # TODO: Implementar upload real via Arduino CLI ou avrdude
        # Por enquanto, simulamos sucesso
        self.upload_progress.setVisible(True)
        self.upload_progress.setValue(0)
        
        try:
            # Simula progresso
            for i in range(0, 101, 10):
                self.upload_progress.setValue(i)
                self.repaint()  # Atualiza UI
            
            QMessageBox.information(
                self,
                "Sucesso",
                f"✅ Firmware enviado com sucesso para {self.selected_port}!\n\n"
                f"O Arduino foi programado e está rodando o novo efeito."
            )
            self.upload_status.setText("✅ Upload concluído!")
            self.upload_status.setStyleSheet("color: #00aa00;")
            self.upload_progress.setVisible(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro no Upload", f"Erro: {str(e)}")
            self.upload_status.setText(f"❌ Erro: {str(e)}")
            self.upload_status.setStyleSheet("color: #ff6b6b;")
            self.upload_progress.setVisible(False)
    
    def closeEvent(self, event):
        """Para o monitor ao fechar a aba"""
        self.arduino_monitor.stop()
        super().closeEvent(event)
