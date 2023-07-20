from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from dotenv import load_dotenv

from App import database
from App.logs import logger

import os


load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")


class SchoolInformationsFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "okul_bilgileri_frame.ui"), self)

        self.set_signals()
        self.set_ui()
        self.set_ts()

        self.draw_texts(schoolName=True, managerName=True, typee=True)
        self.draw_table()
        self.set_ui()
        
    def set_ui(self):
        self.schoolNameButtons = [self.schoolNameSaveBtn, self.schoolNameDiscardBtn]
        self.managerNameButtons = [self.managerNameSaveBtn, self.managerNameDiscardBtn]
        self.typeNameButtons = [self.typeNameSaveBtn, self.typeNameDiscardBtn]
        [btn.setVisible(False) for btn in self.schoolNameButtons]
        [btn.setVisible(False) for btn in self.managerNameButtons]
        [btn.setVisible(False) for btn in self.typeNameButtons]
    
    def set_signals(self):
        self.schoolNameIn.textChanged.connect(lambda: self.update_buttons_visibility(schoolName = True))
        self.managerNameIn.textChanged.connect(lambda: self.update_buttons_visibility(managerName = True))
        self.typeCombo.currentIndexChanged.connect(lambda: self.update_buttons_visibility(typee = True))

        self.schoolNameSaveBtn.clicked.connect(lambda: self.update_text_changes(mod="save", schoolName=True))
        self.managerNameSaveBtn.clicked.connect(lambda: self.update_text_changes(mod="save", managerName=True))
        self.typeNameSaveBtn.clicked.connect(lambda: self.update_text_changes(mod="save", typee=True))
        self.schoolNameDiscardBtn.clicked.connect(lambda: self.update_text_changes(mod="disc", schoolName=True))
        self.managerNameDiscardBtn.clicked.connect(lambda: self.update_text_changes(mod="disc", managerName=True))
        self.typeNameDiscardBtn.clicked.connect(lambda: self.update_text_changes(mod="disc", typee=True))

    def validate_text(self, widget, new_text):
        widget = self.schoolNameIn if not widget else self.managerNameIn
        label = self.schoolNameLabel if not widget else self.managerNameLabel
        warning_message = "İstenmeyen karakter(ler): {}"
        un_wanted_chars = [*"!'^+%&/=?_\"()[]<>{}.,"]
        un_wanted_chars2 = []
        if any([char in new_text for char in un_wanted_chars]):
            modified_text = new_text
            for char in un_wanted_chars:
                if char in new_text:
                    un_wanted_chars2.append(char)
                    modified_text = modified_text.replace(char, "")

            widget.setText(modified_text)
            label.setText(warning_message.format(", ".join(un_wanted_chars2)))
            label.setVisible(True)

        else:
            label.setVisible(False)
            
    def update_buttons_visibility(self, schoolName = False, managerName = False, typee = False):
        if schoolName:
            self.validate_text("1", self.schoolNameIn.text())
            [btn.setVisible(True) for btn in self.schoolNameButtons]
        
        elif managerName:
            self.validate_text("2", self.managerNameIn.text())
            [btn.setVisible(True) for btn in self.managerNameButtons]
            
        elif typee:
            [btn.setVisible(True) for btn in self.typeNameButtons]

    def update_text_changes(self, mod = False, schoolName = False, managerName = False, typee = False):
        if mod == "save":
            if schoolName:
                schoolName = self.schoolNameIn.text().upper().strip()
                managerName = self.infos[1]
                typee = self.infos[2]

                database.update_all_infos(schoolName, managerName, typee)
                self.draw_texts(schoolName = True)
                [btn.setVisible(False) for btn in self.schoolNameButtons]
                
            elif managerName:
                schoolName = self.infos[0]
                managerName = self.managerNameIn.text().upper().strip()
                typee = self.infos[2]
                
                database.update_all_infos(schoolName, managerName, typee)
                self.draw_texts(managerName = True)
                [btn.setVisible(False) for btn in self.managerNameButtons]
            
            elif typee:
                schoolName = self.infos[0]
                managerName = self.infos[1]
                typee = self.typeCombo.currentText().upper().strip()
                
                self.draw_texts(typee = True)
                database.update_all_infos(schoolName, managerName, typee)
                [btn.setVisible(False) for btn in self.typeNameButtons]
        
        elif mod == "disc":
            self.draw_texts(schoolName=schoolName, managerName=managerName, typee=typee)

            if schoolName:
                [btn.setVisible(False) for btn in self.schoolNameButtons]
                
            elif managerName:
                [btn.setVisible(False) for btn in self.managerNameButtons]
            
            elif typee:
                [btn.setVisible(False) for btn in self.typeNameButtons]

    def draw_texts(self, schoolName = False, managerName = False, typee = False):
        self.infos = database.get_all_infos()
        schoolNameText = self.infos[0]
        managerNameText = self.infos[1]
        typeNameText = self.infos[2]
        if schoolName:
            self.schoolNameIn.setText(schoolNameText)

        if managerName:
            self.managerNameIn.setText(managerNameText)
            
        if typee and typeNameText == "Lise":
            self.typeCombo.setCurrentIndex(0)
        elif typee and typeNameText == "Ortaokul":
            self.typeCombo.setCurrentIndex(1)
        
    def draw_table(self):
        infos = database.get_table_infos()
                
        for rowIndex in range(len(infos)):
            values = infos[rowIndex].split(",")
            for colIndex in range(len(values)):
                item = QTableWidgetItem(values[colIndex])
                self.table.setItem(rowIndex, colIndex, item)
            
    def set_ts(self):
        """
        Set the 'table settings'.
        """
        self.table.setColumnCount(5)
        self.table.setRowCount(3)
        columnHeaders = ["Toplam", "9'lar", "10'lar", "11'ler", "12'ler"]
        rowHeaders = ["Sınıf sayısı", "Öğrenci Sayısı", "Salon sayısı"]
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.setVerticalHeaderLabels(rowHeaders)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        