import sys
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon

from app.ui.effects_tab import EffectsTab
from app.ui.config_tab import ConfigTab
from app.ui.installer_tab import InstallerTab

import ctypes
myappid = u'com.phoneaid.control.leds'  # nome único do app
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(ROOT_PATH, "app")
ASSETS_PATH = os.path.join(ROOT_PATH, "assets")
ICON_PATH = os.path.join(ASSETS_PATH, "icon_phoneaid.png")

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)
if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PHONEAID - Controle de LEDs")
        self.setGeometry(200, 100, 900, 600)

        # Define ícone na barra superior da janela
        self.setWindowIcon(QIcon(ICON_PATH))

        tabs = QTabWidget()
        self.installer_tab = InstallerTab()

        tabs.addTab(self.installer_tab, "Instalador")
        tabs.addTab(ConfigTab(), "Configurar LEDs")
        tabs.addTab(EffectsTab(), "Efeitos")

        self.setCentralWidget(tabs)

    # Removido: get_serial_port - não necessário mais


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Define ícone também na barra de tarefas
    app.setWindowIcon(QIcon(ICON_PATH))

    main_win = MainApp()
    main_win.show()
    sys.exit(app.exec_())
