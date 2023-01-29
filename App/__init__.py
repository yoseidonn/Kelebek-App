from PyQt5.QtWidgets import QApplication
from .windows import MainWindow
import os, sys

app = QApplication([sys.argv])
window = MainWindow()
app.exec_()