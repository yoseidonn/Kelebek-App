from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

import os, sys


class Display():
    def __init__(self, examsList: QListWidget, filesList: QListWidget, webEngineView: QWebEngineView, buttons: list):
        self.examsList = examsList
        self.filesList = filesList
        self.wev = webEngineView
        self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.menuBtn, self.downloadBtn = buttons
        
        self.currentMode = 'salon_oturma_duzenleri.html'
        self.examItems, self.archiveItems = [], []

        self.set_elw() # Exam list widget
        self.set_alw() # Archive list widget
        self.set_flw() # File list widget of selected exam

        self.set_signals()
        self.set_ui()
        
    def set_signals(self):
        self.examsList.itemClicked.connect(self.el_item_clicked)
        self.filesList.itemClicked.connect(self.fl_item_clicked)
        self.downloadBtn.clicked.connect(self.download)
        
    def set_ui(self):
        #self.downloadBtn.setEnabled(False)
        self.removeBtn.setEnabled(False)
        self.removeAllBtn.setEnabled(False)
        self.removeBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join("Images","icon", "refresh-ccw.svg")))
        self.menuBtn.setIcon(QIcon(os.path.join("Images", "icon", "menu.svg")))
    
    def download(self):
        savePath = self.save_dialog()
        #HTML yazısını çıkar ve _to_save.html ekle
        modText = self.currentMode[0:-5] + "_to_save.html"
        savedFilePath = os.path.join('Saved', self.selectedExamName, modText)
        print(f"[LOG] Saving {savedFilePath} to {savePath}")
        print("[ERROR] Process stopped...")
        
        # save the self.selectedFilePath content as pdf file
        
    def save_dialog(self):
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setWindowTitle("Kaydetme dizini seçiniz")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_() == QFileDialog.Accepted:
            return dialog.selectedFiles()[0]
        
    def refresh_exams(self):
        pass
    
    ### Exam List Widget
    def el_item_clicked(self, item: QListWidgetItem):
        self.selectedExamName = item.text()
        filePath = os.path.join('Saved', self.selectedExamName, self.currentMode)
        with open(filePath, "r", encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)

    def set_elw(self):
        # ExamsListWidget settings
        x = [x[0] for x in os.walk('Saved/')]
        for directory in x:
            dName = directory.split('Saved/')[1]
            if len(dName) != 0:
                item = QListWidgetItem(dName)
                self.examItems.append(item)
                self.examsList.addItem(item)

        if len(self.examItems) != 0:
            lastItem = self.examItems[0]
            lastItem.setSelected(True)
            self.el_item_clicked(lastItem)
                
    ### File List Widget
    def fl_item_clicked(self, item: QListWidgetItem):
        if item.text() == "Salon oturma düzenleri":
            self.currentMode = "salon_oturma_duzenleri.html"
            print(f'[LOG] {self.selectedExamName}-Salon seçildi.')
        elif item.text() == "Sınıf listeleri":
            self.currentMode = "sinif_listeleri.html"
            print(f'[LOG] {self.selectedExamName}-Sınıf seçildi.')

        filePath = os.path.join('Saved', self.selectedExamName, self.currentMode)
        with open(filePath, 'r', encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)

    def set_flw(self):
        self.file1 = QListWidgetItem('Salon oturma düzenleri')
        self.file2 = QListWidgetItem('Sınıf listeleri')
        self.filesList.addItem(self.file1)
        self.filesList.addItem(self.file2)
        self.file1.setSelected(True)
        
    def al_item_clicked(self, item:QListWidgetItem):
        ...
        
    def set_alw(self):  
        # ExamsListWidget settings
        x = [x[0] for x in os.walk('Archived/')]
        for directory in x:
            dName = directory.split('Archived/')[1]
            if len(dName) != 0:
                item = QListWidgetItem(dName)
                self.archiveItems.append(item)
                self.archiveList.addItem(item)

        if len(self.archiveItems) != 0:
            lastItem = self.archiveItems[0]
            lastItem.setSelected(True)
            self.al_item_clicked(lastItem)