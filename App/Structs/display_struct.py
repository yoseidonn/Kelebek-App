from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

import os, sys, shutil


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
        
        self.set_elw() # Exam list widget
        self.set_alw() # Archive list widget
        self.set_flw() # File list widget of selected exam
        
    def set_signals(self):
        self.examsList.itemClicked.connect(self.el_item_clicked)
        self.archiveList.itemClicked.connect(self.al_item_clicked)
        self.filesList.itemClicked.connect(self.fl_item_clicked)
        self.toolbox.currentChanged.connect(self.toolbox_changed)
        
        self.removeBtn.clicked.connect(self.remove_exam)
        self.removeAllBtn.clicked.connect(lambda: self.remove_exam(all = True))
        self.downloadBtn.clicked.connect(self.download)
        
    def set_ui(self):
        self.toolbox.setCurrentIndex(0)
        self.removeBtn.setEnabled(False)
        self.removeAllBtn.setEnabled(False)
        self.removeBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join("Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join("Images","icon", "refresh-ccw.svg")))
        self.menuBtn.setIcon(QIcon(os.path.join("Images", "icon", "menu.svg")))

        self.menu = QMenu()
        actArchive = QAction("Arsivle", self.buttonsFrame)
        artDeArchive = QAction("Arsivden cikar", self.buttonsFrame)
        actRemoveArchive = QAction("Arsivi temizle", self.buttonsFrame)
        QAction()
        self.menu.addAction(actArchive)
        self.menu.addAction(artDeArchive)
        self.menu.addAction(actRemoveArchive)
        self.menuBtn.setMenu(self.menu)
    
    def remove_exam(self, all = False):
        dialog = ConfirmRemoveArchivedExam()
        base_dir = "Saved" if self.toolbox.currentIndex() == 0 else "Archived"
        if all:
            shutil.rmtree(os.path.join("Saved"))
            os.mkdir("Saved")
            return
        try:
            if self.isArchived:
                dialog = QDialog()
            if not self.isArchived or dialog.confirmed:
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
        pass
    
    def toolbox_changed(self, index: int):
        print(f"[MOD CHANGED] Index {index}")
        self.al_item_clicked(self.archiveItems[0]) if index else self.el_item_clicked(self.examItems[0])
        
    ### Exam List Widget
    def el_item_clicked(self, item: QListWidgetItem):
        self.isArchived = False
        item.setSelected(True)
        self.selectedExamName = item.text()
        print(f"[ITEM SELECTED] {item.text()}")
        base_dir = "Saved" if self.toolbox.currentIndex() == 0 else "Archived"
        filePath = os.path.join(f'{base_dir}', self.selectedExamName, self.currentMode)
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
            lastItem = self.examItems[0]
            lastItem.setSelected(True)
            self.el_item_clicked(lastItem)
                
    def al_item_clicked(self, item:QListWidgetItem):
        self.isArchived = True
        item.setSelected(True)
        self.selectedExamName = item.text()
        print(f"[ITEM SELECTED] {item.text()}")
        base_dir = "Saved" if self.toolbox.currentIndex() == 0 else "Archived"
        filePath = os.path.join(f'{base_dir}', self.selectedExamName, self.currentMode)
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

        if len(self.examItems) != 0:
            lastItem = self.examItems[0]
            lastItem.setSelected(True)
            self.el_item_clicked(lastItem)
            
    ### File List Widget
    def fl_item_clicked(self, item: QListWidgetItem):
        if item.text() == "Salon oturma düzenleri":
            self.currentMode = "salon_oturma_duzenleri.html"
            print(f'[ITEM SELECTED] {self.selectedExamName} - Salon seçildi.')
        elif item.text() == "Sınıf listeleri":
            self.currentMode = "sinif_listeleri.html"
            print(f'[ITEM SELECTED] {self.selectedExamName} - Sınıf seçildi.')

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
        loadUi(os.path.join("Forms", "sinav_silme_onay_dialog.ui"))