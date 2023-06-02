import typing
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

import os, sys, shutil, pathlib


class Display():
    def __init__(self, toolbox: QToolBox, examsList: QListWidget, archiveList: QListWidget, filesList: QListWidget, webEngineView: QWebEngineView, displayTitle: QLabel, buttons: list, buttonsFrame: QFrame):
        self.toolbox = toolbox
        self.examsList = examsList
        self.archiveList = archiveList
        self.filesList = filesList
        self.wev = webEngineView
        self.displayTitle = displayTitle
        self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.menuBtn, self.downloadBtn = buttons
        self.buttonsFrame = buttonsFrame

        self.currentMode: str = 'salon_oturma_duzenleri.html'
        self.examItems: list[QListWidgetItem] = []
        self.archiveItems: list[QListWidgetItem] = []
        self.isArchived = False
        
        self.set_signals()
        self.set_ui()
        
        self.set_alw() # Archive list widget
        self.set_elw() # Exam list widget
        self.set_flw() # File list widget of selected exam
        
    def set_signals(self):
        self.examsList.itemClicked.connect(self.el_item_clicked)
        self.archiveList.itemClicked.connect(self.al_item_clicked)
        self.filesList.itemClicked.connect(self.fl_item_clicked)
        self.toolbox.currentChanged.connect(self.toolbox_changed)
        
        self.removeBtn.clicked.connect(self.remove_exam)
        self.removeAllBtn.clicked.connect(lambda: self.remove_exam(all = True))
        self.refreshAllBtn.clicked.connect(self.refresh_exams)
        self.menuBtn
        self.downloadBtn.clicked.connect(self.download)
        
    def set_ui(self):
        self.toolbox.setCurrentIndex(0)
        self.removeBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join("Images","icon", "refresh-ccw.svg")))
        self.menuBtn.setIcon(QIcon(os.path.join("Images", "icon", "menu.svg")))

        self.menu = QMenu()
        actArchive = QAction("Arşivle", self.buttonsFrame)
        actDeArchive = QAction("Arşivden çıkar", self.buttonsFrame)
        actRemoveArchive = QAction("Arşivi temizle", self.buttonsFrame)
        self.menu.addAction(actArchive)
        self.menu.addAction(actDeArchive)
        self.menu.addAction(actRemoveArchive)
        self.menuBtn.setMenu(self.menu)
    
        actArchive.triggered.connect(self.archive_exam)
        actDeArchive.triggered.connect(self.de_archive_exam)
        actRemoveArchive.triggered.connect(self.remove_exam_from_archive)
        
    def archive_exam(self):
        mod = self.toolbox.currentIndex()
        print(mod)
        if mod:
            print("[ERROR] You can't archive an exam which is already archived.")
            return
        else:
            for item in self.examItems:
                if item.text() == self.selectedExamName:
                    Item = item
                    break

        modText = "Saved"
        filePath = os.path.join(modText, Item.text())
        
        # Create new folder and move files
        os.mkdir(os.path.join("Archived", Item.text()))
        pathlib.Path(os.path.join(filePath, "salon_oturma_duzenleri.html")).rename(os.path.join('Archived', Item.text(), 'salon_oturma_duzenleri.html'))
        pathlib.Path(os.path.join(filePath, "sinif_listeleri.html")).rename(os.path.join('Archived', Item.text(), 'sinif_listeleri.html'))
        print(f"[FILES TRANSFER] Moved both files into Archived/{Item.text()}")
        
        # Remove old folder
        shutil.rmtree(filePath)
        print(f"[REMOVE] Removing {filePath}.")
        
        # Refresh exams
        self.refresh_exams()
    
    def de_archive_exam(self):
        mod = self.toolbox.currentIndex()
        print(mod)
        if not mod:
            print("[ERROR] You can't de archive an exam which is not archived.")
            return
        else:
            for item in self.archiveItems:
                if item.text() == self.selectedExamName:
                    Item = item
                    break
                
        modText = "Archived"
        filePath = os.path.join(modText, Item.text())
        
        # Create new folder and move files
        os.mkdir(os.path.join("Saved", Item.text()))
        pathlib.Path(os.path.join(filePath, "salon_oturma_duzenleri.html")).rename(os.path.join('Saved', Item.text(), 'salon_oturma_duzenleri.html'))
        pathlib.Path(os.path.join(filePath, "sinif_listeleri.html")).rename(os.path.join('Saved', Item.text(), 'sinif_listeleri.html'))
        print(f"[FILES TRANSFER] Moved both files into Saved/{item.text()}")
        
        # Remove old folder
        shutil.rmtree(filePath)
        print(f"[REMOVE] Removing {filePath}.")
        
        # Refresh exams
        self.refresh_exams()
    
    def remove_exam_from_archive(self):
        pass
    
    def remove_exam(self, all = False):
        base_dir = "Saved" if self.toolbox.currentIndex() == 0 else "Archived"
        if all:
            dialog = SelectWhichToRemove()
            shutil.rmtree(os.path.join("Saved"))
            os.mkdir("Saved")
            return
        try:
            if self.isArchived:
                print("[REMOVE] Unable to remove an archived exam.")
                return
                dialog = ConfirmRemoveArchivedExam()
            elif not self.isArchived:
                print(f"[LOG] Removing {os.path.join(base_dir, self.selectedExamName)}")
                print(f"[LOG] Archived: {self.isArchived}")
                shutil.rmtree(os.path.join(base_dir, self.selectedExamName))
            else:
                print("[LOG] Remove cancelled.")
                
        except Exception as e:
            print(f"[ERROR] Can not find exam to remove at: {os.path.join(base_dir, self.selectedExamName)}")
            print(f"[LOG] {e}")
            
    def download(self):
        savePath = self.save_dialog()
        #HTML yazısını çıkar ve _to_save.html ekle
        modText = self.currentMode[0:-5] + "_to_save.html"
        savedFilePath = os.path.join('Saved', self.selectedExamName, modText)
        print(f"[DOWNLOAD] Saving {savedFilePath} to {savePath}")
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
        self.examsList.clear()
        self.archiveList.clear()
        self.examItems: list[QListWidgetItem] = []
        self.archiveItems: list[QListWidgetItem] = []
        if self.toolbox.currentIndex():
            self.set_elw()
            self.set_alw()
        else:
            self.set_alw()
            self.set_elw()
            
        print("[REFRESH] Refreshing Exams and Archived Exams.")
    
    def toolbox_changed(self, index: int):
        print(f"[MOD CHANGED] Index {index}")
        try:
            self.al_item_clicked(self.archiveItems[0]) if index else self.el_item_clicked(self.examItems[0])
        except:
            pass
        
    ### Exam List Widget
    def el_item_clicked(self, item: QListWidgetItem):
        self.isArchived = False
        item.setSelected(True)
        self.selectedExamName = item.text()
        filePath = os.path.join(f'Saved', self.selectedExamName, self.currentMode)
        with open(filePath, "r", encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)
        
        mod = "Salon oturma düzenleri" if self.currentMode == "salon_oturma_duzenleri.html" else "Sınıf listeleri"
        self.displayTitle.setText("{0} - {1}".format(self.selectedExamName, mod))
        
    # ExamsListWidget settings
    def set_elw(self):
        x = [x[0] for x in os.walk('Saved/')]
        for directory in x:
            dName = directory.split('Saved/')[1]
            if len(dName) != 0:
                item = QListWidgetItem(dName)
                self.examItems.append(item)
                self.examsList.addItem(item)

        if len(self.examItems) != 0:
            firstItem = self.examItems[0]
            firstItem.setSelected(True)
            self.el_item_clicked(firstItem)
                
    def al_item_clicked(self, item:QListWidgetItem):
        self.isArchived = True
        item.setSelected(True)
        self.selectedExamName = item.text()
        filePath = os.path.join(f'Archived', self.selectedExamName, self.currentMode)
        with open(filePath, "r", encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)
        
        mod = "Salon oturma düzenleri" if self.currentMode == "salon_oturma_duzenleri.html" else "Sınıf listeleri"
        self.displayTitle.setText("{} - {}".format(self.selectedExamName, mod))

    # ExamsListWidget settings
    def set_alw(self):
        x = [x[0] for x in os.walk('Archived/')]
        for directory in x:
            dName = directory.split('Archived/')[1]
            if len(dName) != 0:
                item = QListWidgetItem(dName)
                self.archiveItems.append(item)
                self.archiveList.addItem(item)

        if len(self.archiveItems) != 0:
            firstItem = self.archiveItems[0]
            firstItem.setSelected(True)
            self.al_item_clicked(firstItem)
            
    ### File List Widget
    def fl_item_clicked(self, item: QListWidgetItem):
        if item.text() == "Salon oturma düzenleri":
            self.currentMode = "salon_oturma_duzenleri.html"
            #print(f'[ITEM SELECTED] {self.selectedExamName} - Salon seçildi.')
        elif item.text() == "Sınıf listeleri":
            self.currentMode = "sinif_listeleri.html"
            #print(f'[ITEM SELECTED] {self.selectedExamName} - Sınıf seçildi.')

        base_dir = "Saved" if self.toolbox.currentIndex() == 0 else "Archived"
        filePath = os.path.join(base_dir, self.selectedExamName, self.currentMode)
        with open(filePath, 'r', encoding="utf-8") as file:
            htmlContent = file.read()
        self.wev.setHtml(htmlContent)
        
        mod = "Salon oturma düzenleri" if self.currentMode == "salon_oturma_duzenleri.html" else "Sınıf listeleri"
        self.displayTitle.setText("{} - {}".format(self.selectedExamName, mod))

    def set_flw(self):
        self.file1 = QListWidgetItem('Salon oturma düzenleri')
        self.file2 = QListWidgetItem('Sınıf listeleri')
        self.filesList.addItem(self.file1)
        self.filesList.addItem(self.file2)
        self.file1.setSelected(True)
        
        
class ConfirmRemoveArchivedExam(QDialog):
    def __init__(self, single = True, all = False, normal = True, archived = False):
        super().__init__()
        loadUi(os.path.join("Forms", "arsiv_silme_onay_dialog.ui"))
    
class SelectWhichToRemove(QDialog):
    def __init__(self):
        super().__init__()
        loadUi