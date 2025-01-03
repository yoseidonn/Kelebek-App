from PyQt5.QtWidgets import QApplication, QMessageBox
import qdarktheme.base
import qdarktheme.dist
import qdarktheme.qtpy
import qdarktheme.util
from .logs import logger
from .main_window import MainWindow
from .database import *
import qdarktheme
import os, sys

BASE_DIR = os.getenv('BASE_DIR')

os.makedirs(os.path.join(BASE_DIR, 'Archived'), exist_ok=True)

os.makedirs(os.path.join(BASE_DIR, 'Saved'), exist_ok=True)

os.makedirs(os.path.join(BASE_DIR, 'Temp'), exist_ok=True)

try:
    with open(os.path.join(BASE_DIR, "App", "Themes", "styles.css"), "r", encoding="utf-8") as f:
        styles = f.read()
except Exception as e:
    styles = ""
    logger.error(f"{str(e)}\nCannot find App/Themes/styles.css")


app = QApplication([sys.argv])
app.setStyleSheet(styles)

theme = get_theme()
qdarktheme.setup_theme(theme)

window = MainWindow()
sys.exit(app.exec_())