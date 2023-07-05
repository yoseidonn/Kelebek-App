from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from dotenv import load_dotenv


from App import database
from App.database import num_sort
from App.logs import logger

import os, shutil, pathlib


load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")


class SavedExamsFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "sinavlar_frame.ui"), self)
        
        self.set_ui()

        buttons = [self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.archiveBtn, self.downloadsBtn]
        frames = [self.buttonsFrame, self.contentFrame]
        toolBoxes = [self.examsToolBox, self.filesToolBox]
        listWidgets = [self.activeList, self.archiveList, self.classroomList, self.gradeList]
        
        self.Display = Display(toolBoxes=toolBoxes, listWidgets=listWidgets, webEngineView = self.wev, displayGroupBox = self.displayGroupBox, buttons = buttons, frames = frames)
        
    def set_ui(self):
        self.wev = QWebEngineView()
        self.displayLayout.addWidget(self.wev)
        
        
class Display():
    def __init__(self, toolBoxes: list[QToolBox], listWidgets: list[QListWidget], webEngineView: QWebEngineView, displayGroupBox: QGroupBox, buttons: list, frames: list):
        self.examsToolBox, self.filesToolBox = toolBoxes
        self.activeList, self.archiveList, self.classroomList, self.gradeList = listWidgets
        
        self.wev = webEngineView
        self.displayGroupBox = displayGroupBox
        self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.archiveBtn, self.downloadsBtn = buttons
        self.buttonsFrame, self.contentFrame = frames

        self.init_settings()
        
    def init_settings(self):
        self.set_variables()
        self.set_downloads_menu()
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
        
        self.archive_exam = lambda: self.archive_exam_slot(archiveMode="Archive")
        self.de_archive_exam = lambda: self.archive_exam_slot(archiveMode="De-Archive")

    def set_signals(self):
        self.activeList.itemClicked.connect(self.active_clicked)
        self.archiveList.itemClicked.connect(self.archive_clicked)
        self.classroomList.itemClicked.connect(self.classroom_clicked)
        self.gradeList.itemClicked.connect(self.grade_clicked)
        
        self.examsToolBox.currentChanged.connect(self.exam_type_changed)
        self.filesToolBox.currentChanged.connect(self.file_mode_changed)

        self.removeBtn.clicked.connect(self.remove_exam)
        self.removeAllBtn.clicked.connect(lambda: self.remove_exam(all=True))
        self.refreshAllBtn.clicked.connect(self.refresh)
        self.archiveBtn.clicked.connect(self.archive_exam)
        
    def set_ui(self):
        self.removeBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.removeAllBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.refreshAllBtn.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.archiveBtn.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.downloadsBtn.setStyleSheet("background-color: rgb(143, 240, 164);")
        self.removeAllBtn.setStyleSheet("background-color: rgb(246, 97, 81);")
        
        self.examsToolBox.setCurrentIndex(0)
        self.removeBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.removeAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash.svg")))
        self.refreshAllBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images","icon", "refresh-ccw.svg")))
        self.archiveBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "custom_archive.svg")))
        self.downloadsBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")))

        self.removeBtn.setIconSize(QSize(24, 24))
        self.removeAllBtn.setIconSize(QSize(24, 24))
        self.refreshAllBtn.setIconSize(QSize(24, 24))
        self.archiveBtn.setIconSize(QSize(24, 24))
        self.downloadsBtn.setIconSize(QSize(24, 24))
        
    def set_downloads_menu(self):
        self.downloadsMenu = QMenu()
        self.download_selected_exam = QAction(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")), "Seçili sınavı indir", self.contentFrame)
        self.download_selected_exam_classrooms = QAction(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")), "Seçili sınavın salon görünümlerini indir", self.contentFrame)
        self.download_selected_exam_grades = QAction(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")), "Seçili sınavın sınıf listelerini indir", self.contentFrame)
        self.download_selected_file = QAction(QIcon(os.path.join(BASE_DIR, "Images", "icon", "download.svg")), "Seçili dosyayı indir", self.contentFrame)

        actions = [self.download_selected_exam, self.download_selected_exam_classrooms, self.download_selected_exam_grades, self.download_selected_file]
        self.downloadsMenu.addActions(actions)
        
        self.downloadsBtn.setMenu(self.downloadsMenu)
        
    # Button functions
    def de_archive_exam_slot(self):
        self.archive_exam_slot(archiveMode="De-Archive")

    def archive_exam_slot(self, archiveMode: str = "Archive"):
        if self.last_clicked_item is None:
            QMessageBox.information(None, "Uyarı", "Lütfen bir sınav seçiniz.")
            return

        current = "Saved" if archiveMode == "Archive" else "Archived"
        to = "Archived" if archiveMode == "Archive" else "Saved"

        # Start archive/dearchiving
        logger.info(f'{"Arşivleniyor" if self.current_exam_type == "Saved" else "Arşivden çıkartılıyor"}')
        
        classroomDirs = os.listdir(os.path.join(BASE_DIR, current, self.selected_exam_name, "Classrooms"))
        gradeDirs = os.listdir(os.path.join(BASE_DIR, current, self.selected_exam_name, "Grades"))
        classroomDirs = sorted(sorted(classroomDirs), key=num_sort)
        gradeDirs = sorted(sorted(gradeDirs), key=num_sort)
        
        try:
            os.mkdir(os.path.join(BASE_DIR, to, self.selected_exam_name))
        except FileExistsError:
            exam_type = ("arşivde" if self.current_exam_type == "Saved" else "aktif")
            reply = QMessageBox.question(None, "Uyarı", f'{self.selected_exam_name} adında {exam_type} bir sınav mevcut, eğer onaylarsanız {exam_type} olan \"{self.selected_exam_name}\" adlı sınav tekrar yazılacaktır.')
            if reply == QMessageBox.No:
                QMessageBox.information(None, "Uyarı", f'{self.selected_exam_name} adlı sınavı {("arşivleme" if self.current_exam_type == "Saved" else "arşivden çıkarma")} iptal edildi.')
                return
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

        logger.info("Arşivleme tamamlandı")
        self.last_clicked_item = None
        if archiveMode == "Archive":
            self.set_archive_list_widget()
            self.set_active_list_widget()
        else:
            self.set_active_list_widget()
            self.set_archive_list_widget()
    
    def remove_exam(self, all=False):
        if self.last_clicked_item is None:
            QMessageBox.information(None, "Uyarı", "Lütfen bir sınav seçiniz.")
            return
        
        # Kök dizinler
        delete_from = self.current_exam_type
        
        # Uygun uyarı mesajı
        if self.current_exam_type == "Saved" and not all:
            reply = QMessageBox.question(None, "Uyarı", f"Bu, geri alınamayan bir işlemdir. Kabul ediyor musunuz?\nNot: {self.selected_exam_name} adlı sınav siliniyor!")

        elif self.current_exam_type == "Saved" and all:
            reply = QMessageBox.question(None, "Uyarı", "Bu, geri alınamayan bir işlemdir. Kabul ediyor musunuz?\nNot: Tüm sınavlar siliniyor!")

        elif self.current_exam_type == "Archived" and not all:
            reply = QMessageBox.question(None, "Uyarı", "Bu, geri alınamayan bir işlemdir. Kabul ediyor musunuz?\nNot: Bu sınavı arşivden siliyorsunuz!")

        else:
            reply = QMessageBox.question(None, "Uyarı", "Bu, geri alınamayan bir işlemdir. Kabul ediyor musunuz?\nNot: Tüm arşivlenmiş sınavlar siliniyor!")
            
        # Kullanıcı yanıtı
        if reply == QMessageBox.No:
                QMessageBox.information(None, "Uyarı", "Sınav silme iptal edildi.")
                return
        
        # Silme işlemi
        if all:
            logger.info("Tüm sınavlar siliniyor")
            for item in (self.activeItems if self.current_exam_type == "Saved" else self.archiveItems):
                deleting_exam = item.text()
                self.last_clicked_item = item
                try:
                    shutil.rmtree(os.path.join(BASE_DIR, delete_from, deleting_exam))
                except Exception as e:
                    logger.error(f"{str(e)} | Sınav silinemedi: {self.selected_exam_name}")
        else:
            logger.info(f"{self.selected_exam_name} siliniyor")
            try:
                deleting_exam = self.last_clicked_item.text()
                shutil.rmtree(os.path.join(BASE_DIR, delete_from, deleting_exam))
            except Exception as e:
                logger.error(f"{str(e)} | Sınav silinemedi: {self.selected_exam_name}")

        logger.info("Silme tamamlandı")
        # Dosyaları yenileme
        self.refresh()
        
    def refresh(self):
        self.examsToolBox.setCurrentIndex(0)
        # Vars
        self.activeItems: list[QListWidgetItem] = []
        self.archiveItems: list[QListWidgetItem] = []
        self.classroomItems: list[QListWidgetItem] = []
        self.gradeItems: list[QListWidgetItem] = []

        self.is_selected_exam_archived = False
        self.current_exam_type = "Saved"
        self.selected_exam_name: str = None
        self.last_clicked_item: QListWidgetItem = None
        
        self.set_archive_list_widget() # Archive list widget
        self.set_active_list_widget() # Exam list widget
        
            
    def download(self):
        if self.last_clicked_item is None:
            QMessageBox.information(None, "Uyarı", "Lütfen bir sınav seçiniz.")
            return
        
    def download_dialog(self):
        if self.last_clicked_item is None:
            QMessageBox.information(None, "Uyarı", "Lütfen bir sınav seçiniz.")
            return

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
            self.removeBtn.setText("Sınavı sil")
            self.removeAllBtn.setText("Tüm sınavları sil")

            self.archiveBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "custom_archive.svg")))
            self.archiveBtn.clicked.disconnect(self.de_archive_exam)
            self.archiveBtn.clicked.connect(self.archive_exam)
            self.archiveBtn.setText("Arşivle")

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
            self.removeBtn.setText("Arşivden sil")
            self.removeAllBtn.setText("Tüm arşivlenmiş sınavları sil")
            
            self.archiveBtn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "custom_unarchive.svg")))
            self.archiveBtn.clicked.disconnect(self.archive_exam)
            self.archiveBtn.clicked.connect(self.de_archive_exam)
            self.archiveBtn.setText("Arşivden çıkar")

            if self.archiveItems:
                Item = self.archiveItems[0]
                Item.setSelected(True)
                self.archive_clicked(Item)
            else:
                self.clear_files_and_preview()
        
    def file_mode_changed(self):
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
            content = f"<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1><h3><strong>{os.getenv('LOG_PATH')}</strong></h3>"
            logger.error(e)

        self.wev.setHtml(content)
    
    def grade_clicked(self, item: QListWidgetItem):
        grade_name = item.text()
        file_path = os.path.join(BASE_DIR, self.current_exam_type, self.selected_exam_name, "Grades", self.get_un_slashed_name(grade_name, file_format=".html"))
        
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            content = f"<h1>Bir hata meydana geldi. Bu dosyayı bulamıyoruz. Kayıt defterine bakmak işinize yarayabilir.</h1><h3><strong>{os.getenv('LOG_PATH')}</strong></h3>"
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
