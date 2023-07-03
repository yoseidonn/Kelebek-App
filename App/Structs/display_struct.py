import typing
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest
import os, sys, shutil, pathlib, datetime
from App import logs
from App.logs import logger

BASE_DIR = os.environ["BASE_DIR"]

class Display():
    def __init__(self, toolBoxes: list[QToolBox], listWidgets: list[QListWidget], webEngineView: QWebEngineView, displayTitle: QLabel, buttons: list, buttonsFrame: QFrame):
        self.examsToolBox, self.filesToolBox = toolBoxes
        self.activeList, self.archiveList, self.classroomList, self.gradeList = listWidgets
        
        self.wev = webEngineView
        self.displayTitle = displayTitle
        self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.menuBtn, self.downloadBtn = buttons
        self.buttonsFrame = buttonsFrame

        self.activeItems: list[QListWidgetItem] = []
        self.archiveItems: list[QListWidgetItem] = []
        self.isArchived = False
        
        self.set_signals()
        self.set_ui()
        
        self.set_archive_list_widget() # Archive list widget
        self.set_active_list_widget() # Exam list widget
        self.set_classroom_list_widget() # Classroom list widget of selected exam
        self.set_grade_list_widget() # Grade list widget of selected exam
        
    def set_signals(self):
        self.examsList.itemClicked.connect(self.el_item_clicked)
        self.archiveList.itemClicked.connect(self.al_item_clicked)
        self.examsToolbox.currentChanged.connect(self.exams_toolbox_changed)
        
        self.removeBtn.clicked.connect(self.remove_exam)
        self.removeAllBtn.clicked.connect(lambda: self.remove_exam(all = True))
        self.refreshAllBtn.clicked.connect(self.refresh_exams)
        self.downloadBtn.clicked.connect(self.download)
        
    def set_ui(self):
        self.examsToolbox.setCurrentIndex(0)
        self.removeBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images","icon", "refresh-ccw.svg")))
        self.menuBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "menu.svg")))

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
        actRemoveArchive.triggered.connect(lambda: self.remove_exam_from_archive(all=True))
        
    def archive_exam(self):
        mod = self.examsToolbox.currentIndex()
        if mod:
            logger.info("You can't archive an exam which is already archived.")
            return
        else:
            for item in self.examItems:
                if item.text() == self.selectedExamName:
                    Item = item
                    break

        modText = "Saved"
        try:
            filePath = os.path.join(BASE_DIR, modText, Item.text())
        except Exception as e:
            logger.error(e)
            return
        try:
            # Create new folder and move files
            os.mkdir(os.path.join("Archived", Item.text()))
            pathlib.Path(os.path.join(filePath, "salon_oturma_duzenleri.html")).rename(os.path.join(BASE_DIR, 'Archived', Item.text(), 'salon_oturma_duzenleri.html'))
            pathlib.Path(os.path.join(filePath, "sinif_listeleri.html")).rename(os.path.join(BASE_DIR,'Archived', Item.text(), 'sinif_listeleri.html'))
            logger.info(f"Moved both files into Archived/{Item.text()}")
            
            # Remove old folder
            shutil.rmtree(filePath)
            logger.info(f"Removing {filePath}.")
            
        except Exception as e:
            logger.error(str(e))
        
        # Refresh exams
        self.refresh_exams()
    
    def de_archive_exam(self):
        mod = self.examsToolbox.currentIndex()
        if not mod:
            logger.error("You can't de archive an exam which is not archived.")
            return
        else:
            for item in self.archiveItems:
                if item.text() == self.selectedExamName:
                    Item = item
                    break
                
        modText = "Archived"
        try:
            filePath = os.path.join(BASE_DIR, modText, Item.text())
        except Exception as e:
            logger.info(e)
            return
        try:
            # Create new folder and move files
            os.mkdir(os.path.join("Saved", Item.text()))
            pathlib.Path(os.path.join(filePath, "salon_oturma_duzenleri.html")).rename(os.path.join(BASE_DIR, 'Saved', Item.text(), 'salon_oturma_duzenleri.html'))
            pathlib.Path(os.path.join(filePath, "sinif_listeleri.html")).rename(os.path.join(BASE_DIR, 'Saved', Item.text(), 'sinif_listeleri.html'))
            logger.info(f"Moved both files into Saved/{item.text()}")
            
            # Remove old folder
            shutil.rmtree(filePath)
            logger.info(f"Removing {filePath}.")
            
        except Exception as e:
            logger.error(str(e))
                
        # Refresh exams
        self.refresh_exams()
    
    def remove_exam_from_archive(self, all=False):
        base_dir = "Saved" if self.examsToolbox.currentIndex() == 0 else "Archived"
        if all and self.examItems:
            result = ConfirmRemoveExam(text="Bu işlem 'tüm arşivlenmiş sınavları' silecektir. Geri alınamaz.").result()
            if not result:
                print("Cancelled")
                return
            
            shutil.rmtree(os.path.join(BASE_DIR, "Archived"))
            os.mkdir(os.path.join(BASE_DIR, "Archived"))
            
        else:
            result = ConfirmRemoveExam(text="Bu işlem 'arşivdeki seçili sınavı' silecektir. Geri alınamaz.").result()
            if not result:
                print("Cancelled")
                return
            
            logger.info(f"Removing {os.path.join(BASE_DIR, base_dir, self.selectedExamName)}")
            logger.info(f"Is archived: {self.isArchived}")
            try:
                shutil.rmtree(os.path.join(BASE_DIR, base_dir, self.selectedExamName))
            except Exception as e:
                logger.error(str(e))
        
        self.refresh_exams()
    
    def remove_exam(self, all = False):
        base_dir = "Saved" if self.examsToolbox.currentIndex() == 0 else "Archived"
        if all and self.examItems:
            result = ConfirmRemoveExam(text="Bu işlem 'tüm aktif sınavları' silecektir. Geri alınamaz.").result()
            if not result:
                print("Cancelled")
                return
            
            shutil.rmtree(os.path.join(BASE_DIR, "Saved"))
            os.mkdir(os.path.join(BASE_DIR, "Saved"))
            self.refresh_exams()
            return
        try:
            # Arşivden sil
            if self.isArchived and self.archiveItems:
                self.remove_exam_from_archive()

            # Kayıtlardan sil
            elif not self.isArchived and self.examItems:
                result = ConfirmRemoveExam(text="Bu işlem 'seçili aktif sınavı' silecektir. Geri alınamaz.").result()
                if not result:
                    print("Cancelled")
                    return
            
                logger.info(f"Removing {os.path.join(BASE_DIR, base_dir, self.selectedExamName)}")
                logger.info(f"Is archived: {self.isArchived}")
                try:
                    shutil.rmtree(os.path.join(BASE_DIR, base_dir, self.selectedExamName))
                except Exception as e:
                    logger.error(str(e))

            # Bilinmeyen dosya
            else:
                logger.info("Remove cancelled.")

            self.refresh_exams()
               
        except Exception as e:
            logger.error(str(e))
            logger.error(f"Can not find exam to remove at: {os.path.join(BASE_DIR, base_dir, self.selectedExamName)}")
            
    def download(self):
        savePath = self.save_dialog()
        #HTML yazısını çıkar ve _to_save.html ekle
        modText = self.currentMode[0:-5] + "_to_save.html"
        savedFilePath = os.path.join(BASE_DIR, 'Saved', self.selectedExamName, modText)
        logger.info(f"Saving {savedFilePath} to {savePath}")
        logger.error("Process stopped... Not implemented")
        
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
        if self.examsToolbox.currentIndex():
            self.set_elw()
            self.set_alw()
        else:
            self.set_alw()
            self.set_elw()
            
        logger.info("[REFRESH] Refreshed Exams and Archived Exams.")
    
    def exams_toolbox_changed(self, index: int):
        try:
            self.al_item_clicked(self.archiveItems[0]) if index else self.el_item_clicked(self.examItems[0])
        except Exception as e:
            logger.error(str(e))
            
    def set_archive_list_widget(self):
        # Archive list widget
        examDirs = [dir[0] for dir in os.walk('Saved/')]
        for directory in examDirs:
            directory_name = directory.split('Saved/')[1]
            if len(directory_name) != 0:
                item = QListWidgetItem(directory_name)
                self.activeItems.append(item)
                self.activeList.addItem(item)

        if len(self.activeItems) != 0:
            firstItem = self.activeItems[0]
            firstItem.setSelected(True)
            self.active_list_item_clicked(firstItem)
    
    def set_active_list_widget(self):
        # Active list widget
        examDirs = [dir[0] for dir in os.walk('Saved/')]
        for directory in examDirs:
            dName = directory.split('Saved/')[1]
            if len(dName) != 0:
                item = QListWidgetItem(dName)
                self.examItems.append(item)
                self.examsList.addItem(item)

        if len(self.examItems) != 0:
            firstItem = self.examItems[0]
            firstItem.setSelected(True)
            self.el_item_clicked(firstItem)

    def set_classroom_list_widget(self):
        # Classroom list widget
        pass

    def set_grade_list_widget(self):
        # Grade list widget
        pass


    ### Exam List Widget
    def actives_item_clicked(self, item: QListWidgetItem):
        self.isArchived = False
        item.setSelected(True)
        self.selectedExamName = item.text()
        filePath = os.path.join(BASE_DIR, 'Saved', self.selectedExamName, self.currentMode)
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                htmlContent = file.read()
        except Exception as e:
            logger.error(str(e))
            htmlContent = "<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1>"
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
        filePath = os.path.join(BASE_DIR, 'Archived', self.selectedExamName, self.currentMode)
        try:
            with open(filePath, "r", encoding="utf-8") as file:
                htmlContent = file.read()
                
        except Exception as e:
            logger.error(str(e))
            htmlContent = "<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1>"
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

        base_dir = "Saved" if self.examsToolbox.currentIndex() == 0 else "Archived"
        try:
            filePath = os.path.join(BASE_DIR, base_dir, self.selectedExamName, self.currentMode)
        except Exception as e:
            logger.debug(str(e))
        try:
            with open(filePath, 'r', encoding="utf-8") as file:
                htmlContent = file.read()
        except Exception as e:
            logger.error(str(e))
            htmlContent = "<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1>"

        self.wev.setHtml(htmlContent)
        
        mod = "Salon oturma düzenleri" if self.currentMode == "salon_oturma_duzenleri.html" else "Sınıf listeleri"
        self.displayTitle.setText("{} - {}".format(self.selectedExamName, mod))

    def set_flw(self):
        self.file1 = QListWidgetItem('Salon oturma düzenleri')
        self.file2 = QListWidgetItem('Sınıf listeleri')
        self.file1.setSelected(True)
        
        
class ConfirmRemoveExam(QDialog):
    def __init__(self, text: str):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "sinav_silme_onay_dialog.ui"), self)
        self.all = all
        self.text = text

        self.set_ui()
        self.set_signals()
        self.set_ws()

    def set_ui(self):
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setText(self.text)
            
    def set_signals(self):
        self.acceptBtn.clicked.connect(self.accept)
        self.denyBtn.clicked.connect(self.reject)
        
    def set_ws(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.exec_()
