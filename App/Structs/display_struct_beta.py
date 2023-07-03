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
from App.database import num_sort

BASE_DIR = os.environ["BASE_DIR"]

class Display():
    def __init__(self, toolBoxes: list[QToolBox], listWidgets: list[QListWidget], webEngineView: QWebEngineView, displayTitle: QLabel, buttons: list, buttonsFrame: QFrame):
        self.examsToolBox, self.filesToolBox = toolBoxes
        self.activeList, self.archiveList, self.classroomList, self.gradeList = listWidgets
        
        self.wev = webEngineView
        self.displayTitle = displayTitle
        self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.menuBtn, self.downloadsBtn = buttons
        self.buttonsFrame = buttonsFrame

        self.init_settings()
        
    def init_settings(self):
        self.set_variables()
        self.set_signals()
        self.set_ui()
        
        self.set_archive_list_widget() # Archive list widget
        self.set_active_list_widget() # Exam list widget
        
    def set_variables(self):
        self.activeItems: list[QListWidgetItem] = []
        self.archiveItems: list[QListWidgetItem] = []
        self.classroomItems: list[QListWidgetItem] = []
        self.gradeItems: list[QListWidgetItem] = []

        self.is_selected_exam_archived = False
        self.current_exam_type = "Saved"
        self.selected_exam_name: str = None
        self.last_clicked_item: QListWidgetItem = None

    def set_signals(self):
        self.activeList.itemClicked.connect(self.active_clicked)
        self.archiveList.itemClicked.connect(self.archive_clicked)
        self.classroomList.itemClicked.connect(self.classroom_clicked)
        self.gradeList.itemClicked.connect(self.grade_clicked)
        
        self.examsToolBox.currentChanged.connect(self.exam_type_changed)
        self.filesToolBox.currentChanged.connect(self.file_mode_changed)

        self.refreshAllBtn.clicked.connect(self.refresh)

    def set_ui(self):
        self.removeBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.removeAllBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.refreshAllBtn.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.menuBtn.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.downloadsBtn.setStyleSheet("background-color: rgb(143, 240, 164);")
        self.removeAllBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        
        self.examsToolBox.setCurrentIndex(0)
        self.removeBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images","icon", "refresh-ccw.svg")))
        self.menuBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "menu.svg")))
        self.downloadsBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")))

        self.menu = QMenu()
        self.actArchive = QAction("Arşivle", self.buttonsFrame)
        self.actDeArchive = QAction("Arşivden çıkar", self.buttonsFrame)
        self.actRemoveArchive = QAction("Arşivi temizle", self.buttonsFrame)
        self.menu.addAction(self.actArchive)
        self.menu.addAction(self.actDeArchive)
        self.menu.addAction(self.actRemoveArchive)
        self.menuBtn.setMenu(self.menu)

        self.actArchive.triggered.connect(lambda: self.archive_exam("Archive"))
        self.actDeArchive.triggered.connect(lambda: self.archive_exam("De-archive"))
        self.actRemoveArchive.triggered.connect(lambda: self.remove_exam(all=True))
        
    # Button functions
    def archive_exam(self, mod: str = "Archived"):
        current = "Saved" if mod == "Archive" else "Archived"
        to = "Archived" if mod == "Archive" else "Saved"

        print(f"Current: {current}, To: {to}, mod: {mod}")
        print(f"Current exam type: {self.current_exam_type}")
        if self.current_exam_type != current:
            logger.error("You can't archive an exam which is already archived.")
            # TODO ADD WARNING MESSAGE
            return
        
        if self.last_clicked_item is None:
            return
        
        # Make the process
        classroomDirs = os.listdir(os.path.join(BASE_DIR, current, self.selected_exam_name, "Classrooms"))
        gradeDirs = os.listdir(os.path.join(BASE_DIR, current, self.selected_exam_name, "Grades"))
        classroomDirs = sorted(sorted(classroomDirs), key=num_sort)
        gradeDirs = sorted(sorted(gradeDirs), key=num_sort)
        
        print(f"Classroom dirs: {', '.join([dir for dir in classroomDirs])}")
        print(f"Grade dirs: {', '.join([dir for dir in gradeDirs])}")
        
        try:
            os.mkdir(os.path.join(BASE_DIR, to, self.selected_exam_name))
        except Exception as e:
            logger.error(f"Yeni dizinleri oluşturma | root dir -> {e}")
        try:
            os.mkdir(os.path.join(BASE_DIR, to, self.selected_exam_name, "Classrooms"))
        except Exception as e:
            logger.error(f"Yeni dizinleri oluşturma | classrooms dir -> {e}")
        try:
            os.mkdir(os.path.join(BASE_DIR, to, self.selected_exam_name, "Grades"))
        except Exception as e:
            logger.error(f"Yeni dizinleri oluşturma | grades dir -> {e}")
        
        try:
            for classroomDir in classroomDirs:
                old_file_dir = os.path.join(BASE_DIR, current, self.selected_exam_name, "Classrooms", classroomDir)
                new_file_dir = os.path.join(BASE_DIR, to, self.selected_exam_name, "Classrooms", classroomDir)
                pathlib.Path(old_file_dir).rename(new_file_dir)
        except Exception as e:
            logger.error(f"Dosyaları taşıma | classrooms -> {e}")

        try:
            for gradeDir in gradeDirs:
                old_file_dir = os.path.join(BASE_DIR, current, self.selected_exam_name, "Grades", gradeDir)
                new_file_dir = os.path.join(BASE_DIR, to, self.selected_exam_name, "Grades", gradeDir)
                pathlib.Path(old_file_dir).rename(new_file_dir)
        except Exception as e:
            logger.error(f"Dosyaları taşıma | grades -> {e}")

        try:
            shutil.rmtree(os.path.join(BASE_DIR, current, self.selected_exam_name))
        except Exception as e:
            logger.error(f"Eski dizini silme -> {e}")

        print("Archived\n")
        self.last_clicked_item = None
        if mod == "Archive":
            self.set_archive_list_widget()
            self.set_active_list_widget()
        else:
            self.set_active_list_widget()
            self.set_archive_list_widget()
    
    def remove_exam(self):
        if True:
            self.remove_active()
        else:
            self.remove_archive()    

    def remove_active(self, all = False):
        pass
        
    def remove_archive(self, all = False):
        pass
    
    def refresh(self):
        self.init_settings()
            
    def download(self):
        pass
        
    def download_dialog(self):
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setWindowTitle("Kaydetme dizini seçiniz")
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_() == QFileDialog.Accepted:
            return dialog.selectedFiles()[0]
           
    # Signal functions----------------------
    def exam_type_changed(self):
        if self.examsToolBox.currentIndex() == 0:
            self.current_exam_type = "Saved"
            
            self.removeBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
            self.removeAllBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
            
            if self.activeItems:
                Item = self.activeItems[0]
                Item.setSelected(True)
                self.active_clicked(Item)
            else:
                self.clear_files_and_preview()

        else:
            self.current_exam_type = "Archived"

            self.removeBtn.setStyleSheet("background-color: rgb(224, 27, 36);")
            self.removeAllBtn.setStyleSheet("background-color: rgb(224, 27, 36);")

            if self.archiveItems:
                Item = self.archiveItems[0]
                Item.setSelected(True)
                self.archive_clicked(Item)
            else:
                self.clear_files_and_preview()
        
    def file_mode_changed(self):
        print(f"Classroom item texts: {', '.join([item.text() for item in self.classroomItems])}")
        print(f"Grade item texts: {', '.join([item.text() for item in self.gradeItems])}")
        print("----")
        if self.filesToolBox.currentIndex() == 0:
            if self.classroomItems:
                Item = self.classroomItems[0]
                Item.setSelected(True)
                self.classroom_clicked(Item)
            else:
                self.wev.setHtml("")

        else:
            if self.gradeItems:
                Item = self.gradeItems[0]
                Item.setSelected(True)
                self.grade_clicked(Item)
            else:
                self.wev.setHtml("")
                
    # Exam panel
    def active_clicked(self, item: QListWidgetItem):
        # Set needed vars for next time
        self.is_selected_exam_archived = False
        self.current_exam_type = "Saved"
         
        if self.last_clicked_item is not None:
            self.last_clicked_item.setSelected(False)
        self.last_clicked_item = item
        self.filesToolBox.setCurrentIndex(0)
        
        # Item seç ve dosyaları güncelle
        item.setSelected(True)
        self.selected_exam_name = item.text()
        examPath = os.path.join(BASE_DIR, "Saved", self.selected_exam_name)

        self.set_classroom_list_widget(examPath=examPath)
        if self.classroomItems:
            Item = self.classroomItems[0]
            Item.setSelected(True)
            self.filesToolBox.setCurrentIndex(0)
            self.classroom_clicked(Item)
            
        self.set_grade_list_widget(examPath=examPath)
        self.file_mode_changed()
        
    def archive_clicked(self, item: QListWidgetItem):
        # Set needed vars for next time
        self.is_selected_exam_archived = True
        self.current_exam_type = "Archived"
        
        if self.last_clicked_item is not None:
            self.last_clicked_item.setSelected(False)
        self.last_clicked_item = item
        self.examsToolBox.setCurrentIndex(1)

        # Item seç ve dosyaları güncelle
        item.setSelected(True)
        self.selected_exam_name = item.text()
        examPath = os.path.join(BASE_DIR, "Archived", self.selected_exam_name)
        
        self.set_classroom_list_widget(examPath=examPath)
        if self.classroomItems:
            Item = self.classroomItems[0]
            Item.setSelected(True)
            self.filesToolBox.setCurrentIndex(0)
            self.classroom_clicked(Item)
            
        self.set_grade_list_widget(examPath=examPath)
        self.file_mode_changed()
        
    # File panel
    def classroom_clicked(self, item: QListWidgetItem):
        classroom_name = item.text()
        file_path = os.path.join(BASE_DIR, self.current_exam_type, self.selected_exam_name, "Classrooms", self.get_un_slashed_name(classroom_name, file_format=".html"))

        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            content = f"<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1><h3><strong>{os.path.join(BASE_DIR, 'kayit_defteri.log')}</strong></h3>"
            logger.error(e)

        self.wev.setHtml(content)
    
    def grade_clicked(self, item: QListWidgetItem):
        grade_name = item.text()
        file_path = os.path.join(BASE_DIR, self.current_exam_type, self.selected_exam_name, "Grades", self.get_un_slashed_name(grade_name, file_format=".html"))
        
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            content = f"<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1><h3><strong>{os.path.join(BASE_DIR, 'kayit_defteri.log')}</strong></h3>"
            logger.error(e)

        self.wev.setHtml(content)
 
    # Adjust functions---------------
    def clear_files_and_preview(self):
        self.last_clicked_item = None
        self.classroomList.clear()
        self.gradeList.clear()
        self.classroomItems: list = list()
        self.gradeItems: list = list()
        self.wev.setHtml("")
        
    # Exam panel
    def set_active_list_widget(self):
        self.activeList.clear()
        self.activeItems: list = list()
        
        examDirs = os.listdir(os.path.join(BASE_DIR, "Saved"))
        examDirs = sorted(sorted(examDirs), key=num_sort)
        
        for directory in examDirs:
            item = QListWidgetItem(directory)
            item.setSelected(False)
            self.activeItems.append(item)
            self.activeList.addItem(item)

        if self.current_exam_type == "Saved" and len(self.activeItems) != 0:
            self.last_clicked_item = self.activeItems[0]
            self.last_clicked_item.setSelected(True)
            self.active_clicked(self.last_clicked_item)
            
        elif self.current_exam_type == "Saved" and len(self.activeItems) == 0:
            self.clear_files_and_preview()

    def set_archive_list_widget(self):
        self.archiveList.clear()
        self.archiveItems: list = list()
        
        examDirs = os.listdir(os.path.join(BASE_DIR, "Archived"))
        examDirs = sorted(sorted(examDirs), key=num_sort)

        for directory in examDirs:
            item = QListWidgetItem(directory)
            item.setSelected(False)
            self.archiveItems.append(item)
            self.archiveList.addItem(item)
        
        if self.current_exam_type == "Archived" and len(self.archiveItems) != 0:
            self.last_clicked_item = self.archiveItems[0]
            self.last_clicked_item.setSelected(True)
            self.archive_clicked(self.last_clicked_item)
            
        elif self.current_exam_type == "Archived" and len(self.archiveItems) == 0:
            self.clear_files_and_preview()
    
    # File panel
    def set_classroom_list_widget(self, examPath: str):
        # Classroom list widget
        self.classroomList.clear()
        self.classroomItems.clear()
        
        classroomDirs = os.listdir(os.path.join(BASE_DIR, self.current_exam_type, self.selected_exam_name, "Classrooms"))
        classroomDirs = sorted(sorted(classroomDirs), key=num_sort)

        for directory in classroomDirs:
            directory = self.get_slashed_name(directory)
            if len(directory) != 0:
                item = QListWidgetItem(directory)
                self.classroomItems.append(item)
                self.classroomList.addItem(item)

    def set_grade_list_widget(self, examPath: str):
        # Grade list widget
        self.gradeList.clear()
        self.gradeItems.clear()

        gradeDirs = os.listdir(os.path.join(BASE_DIR, self.current_exam_type , self.selected_exam_name, "Grades"))
        gradeDirs = sorted(sorted(gradeDirs), key=num_sort)
        
        for directory in gradeDirs:
            directory = self.get_slashed_name(directory)
            if len(directory) != 0:
                item = QListWidgetItem(directory)
                self.gradeItems.append(item)
                self.gradeList.addItem(item)
    
    # Extra functions---------------------
    def get_slashed_name(self, name: str, file_format: str = ""):
        prefix = []
        suffix = []
        
        for letter in name:
            if letter.isnumeric():
                prefix.append(letter)  
            else:
                suffix.append(letter)  

        prefix = "".join(prefix)
        
        if file_format:
            suffix = "".join(suffix)
        else:
            suffix2 = []
            for letter in suffix:
                if letter == ".":
                    break
                suffix2.append(letter)
            suffix = "".join(suffix2)
             
        return f"{prefix}/{suffix}{file_format}"
    
    def get_un_slashed_name(self, name: str, file_format: str = ""):
        prefix = []
        suffix = []
        
        for letter in name:
            if letter.isnumeric():
                prefix.append(letter)  
            elif letter != "/":
                suffix.append(letter)  

        prefix = "".join(prefix)
        
        if file_format:
            suffix = "".join(suffix)
        else:
            suffix2 = []
            for letter in suffix:
                if letter == ".":
                    break
                suffix2.append(letter)
            suffix = "".join(suffix2)
             
        return f"{prefix}{suffix}{file_format}"

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
