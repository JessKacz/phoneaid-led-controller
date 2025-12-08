# app/ui/installer_tab.py
import os
import serial.tools.list_ports
import subprocess
import serial
import json

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox,
    QProgressBar, QApplication, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from app.config_manager import load_config

class InstallerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.confirm_upload = False
        self.compilation_successful = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.setStyleSheet("""
            QLabel { font-size: 15px; }
            QPushButton {
                min-width: 250px; max-width: 250px;
                padding: 6px; font-size: 14px;
                background-color: #e6f0ff;
                border: 1px solid #99c2ff;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #cce0ff; }
            QPushButton:disabled { background-color: #f2f2f2; color: #a6a6a6; }
            QProgressBar {
                height: 18px; border-radius: 5px;
                text-align: center; font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50; border-radius: 5px;
            }
            QComboBox { padding: 4px; font-size: 13px; }
        """)

        self.title = QLabel("<b>🔌 Instalar firmware no Arduino</b>")
        self.title.setFont(QFont("Arial", 15, QFont.Bold))
        self.layout.addWidget(self.title)

        self.port_label = QLabel("Selecione a porta do Arduino:")
        self.layout.addWidget(self.port_label)

        port_row = QHBoxLayout()
        self.port_dropdown = QComboBox()
        self.refresh_button = QPushButton("🔄 Atualizar portas")
        self.connect_button = QPushButton("🔗 Conectar")

        port_row.addWidget(self.port_dropdown)
        port_row.addWidget(self.refresh_button)
        port_row.addWidget(self.connect_button)
        self.layout.addLayout(port_row)

        self.status_label = QLabel("Status: ⚪ Desconectado")
        self.layout.addWidget(self.status_label)

        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.manual_connect)
        self.refresh_ports()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(10000)

        self.layout.addSpacerItem(QSpacerItem(10, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.layout.addWidget(self._divider())
        self.layout.addSpacerItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        compile_row = QHBoxLayout()
        self.compile_button = QPushButton("⚙️ Compilar Configurações")
        self.compile_button.setFixedWidth(250)
        self.compile_button.clicked.connect(self.compile_config)
        self.compile_progress = QProgressBar()
        self.compile_progress.setValue(0)
        self.compile_progress.setFixedHeight(18)

        compile_row.addWidget(self.compile_button)
        compile_row.addWidget(self.compile_progress)
        self.layout.addLayout(compile_row)

        self.compile_message = QLabel("")
        self.layout.addWidget(self.compile_message)

        self.layout.addSpacerItem(QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.layout.addWidget(self._divider())
        self.layout.addSpacerItem(QSpacerItem(10, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        upload_row = QHBoxLayout()
        self.upload_button = QPushButton("⬆️ Enviar firmware para o Arduino")
        self.upload_button.setFixedWidth(250)
        self.upload_button.setEnabled(False)
        self.upload_button.clicked.connect(self.upload_firmware)
        self.upload_progress = QProgressBar()
        self.upload_progress.setValue(0)
        self.upload_progress.setFixedHeight(18)

        upload_row.addWidget(self.upload_button)
        upload_row.addWidget(self.upload_progress)
        self.layout.addLayout(upload_row)

        self.upload_message = QLabel("")
        self.layout.addWidget(self.upload_message)

        self.layout.addSpacerItem(QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.layout.addWidget(self._divider())

        self.refresh_page_button = QPushButton("🔄 Atualizar página")
        self.refresh_page_button.setFixedWidth(250)
        self.layout.addWidget(self.refresh_page_button)
        self.refresh_page_button.clicked.connect(self.reset_page)

        self.setLayout(self.layout)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def refresh_ports(self):
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)
        if not ports:
            self.port_dropdown.addItem("Nenhuma porta encontrada")

    def manual_connect(self):
        selected_port = self.port_dropdown.currentText()
        if "Nenhuma porta" in selected_port or not selected_port:
            QMessageBox.warning(self, "Erro", "Nenhuma porta selecionada.")
            self.serial_port = None
            return
        self.serial_port = selected_port
        self.check_connection()

    def check_connection(self):
        if not self.serial_port:
            self.status_label.setText("Status: ⚪ Desconectado")
            return
        try:
            with serial.Serial(self.serial_port, 9600, timeout=1) as s:
                self.status_label.setText(f"Status: 🟢 Conectado em {self.serial_port}")
        except Exception:
            self.status_label.setText("Status: ⚪ Desconectado")

    def compile_config(self):
        self.compile_progress.setValue(10)
        config = load_config()
        leds = config.get("total_leds", 0)
        effect = config.get("effect", {})

        firmware_dir = os.path.join("firmware")
        os.makedirs(firmware_dir, exist_ok=True)

        # Limpa firmware anterior
        for file in os.listdir(firmware_dir):
            if file.endswith(".ino"):
                os.remove(os.path.join(firmware_dir, file))

        # Monta código base
        code = f"""
#include <FastLED.h>
#define NUM_LEDS {leds}
#define DATA_PIN 6
CRGB leds[NUM_LEDS];

void setup() {{
  FastLED.addLeds<WS2812, DATA_PIN, GRB>(leds, NUM_LEDS);
}}

void loop() {{
"""

        if effect.get("type") == "Cor sólida":
            color = self._parse_color(effect.get("color1", "#FF0000"))
            code += f"""
  fill_solid(leds, NUM_LEDS, CRGB({color[0]}, {color[1]}, {color[2]}));
  FastLED.show();
  delay(100);
}}
"""
        elif effect.get("type") == "Gradiente":
            color1 = self._parse_color(effect.get("color1", "#FF0000"))
            color2 = self._parse_color(effect.get("color2", "#0000FF"))
            code += f"""
  for (int i = 0; i < NUM_LEDS; i++) {{
    float t = float(i) / float(NUM_LEDS - 1);
    uint8_t r = uint8_t({color1[0]} * (1.0 - t) + {color2[0]} * t);
    uint8_t g = uint8_t({color1[1]} * (1.0 - t) + {color2[1]} * t);
    uint8_t b = uint8_t({color1[2]} * (1.0 - t) + {color2[2]} * t);
    leds[i] = CRGB(r, g, b);
  }}
  FastLED.show();
  delay(100);
}}
"""
        elif effect.get("type") == "Onda":
            color1 = self._parse_color(effect.get("color1", "#FF0000"))
            color2 = self._parse_color(effect.get("color2", "#0000FF"))
            speed = effect.get("speed", "Turbo")
            delay_ms = 300 if speed == "Lento" else 150 if speed == "Médio" else 70 if speed == "Rápido" else 30
            wave_width = effect.get("wave_width", leds//2)
            code += f"""
  static uint8_t waveIndex = 0;
  for (int i = 0; i < NUM_LEDS; i++) {{
    int relativePos = (i - waveIndex + NUM_LEDS) % NUM_LEDS;
    float blend = (relativePos < {wave_width}) ? (1.0 - float(relativePos) / {wave_width}) : 0.0;
    uint8_t r = uint8_t({color1[0]} * blend + {color2[0]} * (1.0 - blend));
    uint8_t g = uint8_t({color1[1]} * blend + {color2[1]} * (1.0 - blend));
    uint8_t b = uint8_t({color1[2]} * blend + {color2[2]} * (1.0 - blend));
    leds[i] = CRGB(r, g, b);
  }}
  FastLED.show();
  delay({delay_ms});
  waveIndex = (waveIndex + 1) % NUM_LEDS;
}}
"""

        output_path = os.path.join(firmware_dir, "firmware.ino")
        with open(output_path, "w") as f:
            f.write(code)

        self.compile_progress.setValue(40)

        compile_proc = subprocess.run(
            ["arduino-cli", "compile", "--fqbn", "arduino:avr:uno", firmware_dir],
            capture_output=True, text=True
        )

        if compile_proc.returncode == 0:
            self.compile_progress.setValue(100)
            self.upload_button.setEnabled(True)
            self.compilation_successful = True
            QTimer.singleShot(2000, self.show_compile_success)
        else:
            self.compile_progress.setValue(0)
            QMessageBox.critical(self, "Erro na compilação", compile_proc.stderr)
            self.upload_button.setEnabled(False)
            self.compilation_successful = False

    def _parse_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def show_compile_success(self):
        self.compile_message.setText("✅ Compilação pronta para envio.")
        self.compile_progress.setValue(0)

    def upload_firmware(self):
        port = self.serial_port
        if not self.compilation_successful:
            QMessageBox.warning(self, "Erro", "Compile o código antes de fazer o upload.")
            return
        if not self.confirm_upload:
            QMessageBox.information(self, "Confirmação", "Clique novamente para confirmar o envio.")
            self.confirm_upload = True
            return
        if "Nenhuma porta" in port or not port:
            QMessageBox.warning(self, "Erro", "Nenhuma porta selecionada.")
            return

        try:
            self.upload_button.setEnabled(False)
            self.upload_progress.setValue(20)
            QApplication.processEvents()

            upload_proc = subprocess.Popen([
                "arduino-cli", "upload",
                "-p", port,
                "--fqbn", "arduino:avr:uno",
                "firmware"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            while upload_proc.poll() is None:
                QApplication.processEvents()

            stdout, stderr = upload_proc.communicate()
            if upload_proc.returncode == 0:
                self.upload_progress.setValue(100)
                QTimer.singleShot(2000, self.show_upload_success)
            else:
                self.upload_progress.setValue(0)
                QMessageBox.critical(self, "Erro no Upload", f"Erro ao enviar o firmware:\n\n{stderr.decode()}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro durante o upload:\n{str(e)}")
            self.upload_progress.setValue(0)

        finally:
            self.confirm_upload = False
            self.upload_button.setEnabled(True)

    def show_upload_success(self):
        self.upload_message.setText("✅ Firmware enviado com sucesso.")
        self.upload_progress.setValue(0)

    def reset_page(self):
        self.compile_progress.setValue(0)
        self.compile_message.setText("")
        self.upload_progress.setValue(0)
        self.upload_message.setText("")
        self.compilation_successful = False
        self.confirm_upload = False
