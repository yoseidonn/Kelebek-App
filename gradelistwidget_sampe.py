from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_ui()
        self.set_signals()
        
        self.checkboxes = list()
        self.lastCheckbox = None
        self.show()

    def set_ui(self):
        self.layout = QVBoxLayout()
        self.centralwidget = QWidget()
        self.centralwidget.setLayout(self.layout)
        self.setCentralWidget(self.centralwidget)

        self.lw = QListWidget()
        
        buttonslayout = QHBoxLayout()
        self.addBtn = QPushButton("+")
        self.deleteBtn = QPushButton("-")
        buttonslayout.addWidget(self.addBtn)
        buttonslayout.addWidget(self.deleteBtn)
        self.layout.addLayout(buttonslayout)
        self.layout.addWidget(self.lw)
        
    def set_signals(self):
        self.addBtn.clicked.connect(self.add_new_box)
        self.deleteBtn.clicked.connect(self.delete_last_box)
        
    def add_new_box(self):
        item = QListWidgetItem()
        checkbox = QCheckBox(f"İşaretle {len(self.checkboxes) + 1}", self)
        checkbox.stateChanged.connect(lambda: self.changed(checkbox))
        self.checkboxes.append(checkbox)
        self.lastCheckbox = checkbox
        
        self.lw.addItem(item)
        self.lw.setItemWidget(item, checkbox)
        
    def delete_last_box(self):
        if self.lastCheckbox is not None:
            pass

    def changed(self, checkbox: QCheckBox):
        print(checkbox, checkbox.text())

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()