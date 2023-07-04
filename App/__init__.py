from PyQt5.QtWidgets import QApplication
from .windows import MainWindow
from .logs import logger
import os, sys
import qdarktheme

BASE_DIR = os.getenv('BASE_DIR')


try:
    os.mkdir(os.path.join(BASE_DIR, 'Archived'))
except Exception as e:
    logger.debug(e)

try:
    os.mkdir(os.path.join(BASE_DIR, 'Saved'))
except Exception as e:
    logger.debug(e)

try:
    with open(os.path.join(BASE_DIR, "App", "Themes", "styles.css"), "r", encoding="utf-8") as f:
        styles = f.read()
except Exception as e:
    styles = ""
    logger.error(f"{str(e)}\nCannot find App/Themes/styles.css")

app = QApplication([sys.argv])
app.setStyleSheet(styles)
qdarktheme.setup_theme("auto")
window = MainWindow()
app.exec_()