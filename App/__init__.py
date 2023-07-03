from PyQt5.QtWidgets import QApplication
from .windows import MainWindow
from .logs import logger
import os, sys


BASE_DIR = os.getenv('BASE_DIR')


try:
    os.mkdir(os.path.join(BASE_DIR, 'Archived'))
except Exception as e:
    logger.debug(e)

try:
    os.mkdir(os.path.join(BASE_DIR, 'Saved'))
except Exception as e:
    logger.debug(e)

app = QApplication([sys.argv])
window = MainWindow()
app.exec_()