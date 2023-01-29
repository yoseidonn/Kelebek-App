from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

import os, sys


class Display():
    def __init__(self, examsList: QListWidget, filesList: QListWidget, webEngineView: QWebEngineView):
        self.examsList = examsList
        self.filesList = filesList
        self.wev = webEngineView
        
        self.currentMode = 'salon_oturma_duzenleri.html'
        self.examItems = []

        self.set_elw()
        self.set_flw()

        self.set_signals()
        
    def set_signals(self):
        self.examsList.itemClicked.connect(self.el_item_clicked)
        self.filesList.itemClicked.connect(self.fl_item_clicked)
        
    ### Exam List Widget
    def el_item_clicked(self, item: QListWidgetItem):
        self.selectedExamName = item.text()
        filePath = os.path.join('Saved', self.selectedExamName, self.currentMode)
        with open(filePath, "r", encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)
        
    def refresh_exams(self):
        pass

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
        print(f'{item.text()}-Salon oturuma düzenleri')
        print(item.text() == "Salon oturuma düzenleri")
        if item.text() == "Salon oturma düzenleri":
            self.currentMode = "salon_oturma_duzenleri.html"
            print("salonlar")
        elif item.text() == "Sınıf listeleri":
            self.currentMode = "sinif_listeleri.html"
            print("siniflar")

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