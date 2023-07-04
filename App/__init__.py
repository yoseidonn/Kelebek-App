from PyQt5.QtWidgets import QApplication
from .windows import MainWindow
from .stylesheets import *
from .logs import logger
import os, sys

BASE_DIR = os.getenv('BASE_DIR')

try:
    os.mkdir(os.path.join(BASE_DIR, 'Archive'))
except Exception as e:
    logger.debug(e)

try:
    os.mkdir(os.path.join(BASE_DIR, 'Active'))
except Exception as e:
    logger.debug(e)


app = QApplication([sys.argv])
try:
    app.setStyleSheet(GlobalStyleSheet)
except:
    pass
window = MainWindow()
app.exec_()