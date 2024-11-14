from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from pathlib import Path

from Client import client
from .Frames import school_infos_frame, students_frame, classrooms_frame, create_exam_frame, saved_exams_frame
from . import database, licence_dialogs, logs
from .logs import logger

import os, sys, datetime, logging, subprocess

BASE_DIR = os.getenv("BASE_DIR")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "mainwindow.ui"), self)
        self.licenced = False

        self.check_licence()
        self.set_signs()
        self.set_menu_bar()
        self.set_ui()
        self.sws()

    def check_licence(self):
        key = os.getenv("LICENCE_KEY")
        end_date = os.getenv("END_DATE")
        skip_date = os.getenv("SKIP_DATE")

        key = 'BLANK' if not key else key
        end_date = 'BLANK' if not end_date else end_date
        skip_date = 'BLANK' if not skip_date else skip_date
        
        logger.info(f"Kayıtlı anahtar: {key}\t Sonra eriş tarihi: {end_date}\t En son geçme tarihi: {skip_date}")
        result = self.validate_env_vars(key, end_date, skip_date)
        
        if result == -1:
            logger.info("Bozuk .env dosyası")
        elif result == 0:
            logger.info("Daha önce geçilmiş")
        elif result == 1:
            logger.info("Hiç giriş yapılmamış")
        elif result == 2:
            logger.info("Daha önce giriş yapılmış")

        h1, h2 = "Kelebek lisansı bulunamadı", "Eğer sahipseniz anahtarınızı girin ya da yeni bir anahtar alın."

        # Bozuk .env DOSYASI
        if result == -1:
            with open(".env", "w", encoding="utf-8") as file:
                file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://kelebeksistemi.com.tr/")
                
        # Daha önce geçilmiş
        elif result == 0:
            try:
                year, month, day = [int(i) for i in skip_date.split("-")]
                skip_date = datetime.datetime(year, month, day)
                two_days_later = skip_date + datetime.timedelta(days=2)
            except Exception as e:
                logger.error(f"{e} | Tarih ayırmada hata oluştu, tarih: {skip_date}")
                with open(".env", "w", encoding="utf-8") as file:
                    file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://kelebeksistemi.com.tr/")
                return
            
            now = datetime.datetime.now()
            if two_days_later > now:
                # İki gün geçmemiş, doğrulamayı atla
                logger.info("It's not been too much after last validation skip.")
                return
            else:
                # İki gün geçmiş, tekrar doğrulama iste
                logger.info("It's been two days after last validation skip.")
                with open(".env", "w", encoding="utf-8") as file:
                    file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://kelebeksistemi.com.tr/")    
            
        # Hiç giriş yapılmamış
        elif result == 1:
            pass
        
        # Daha önce giriş yapılmış
        elif result == 2:
            try:
                year, month, day = [int(i) for i in end_date.split("-")]
                end_date = datetime.datetime(year, month, day)
            except Exception as e:
                logger.error(f"{e} | Tarih ayırmada hata oluştu, tarih: {end_date}")
                with open(".env", "w", encoding="utf-8") as file:
                    file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://kelebeksistemi.com.tr/")
                return

            now = datetime.datetime.now()
            if end_date < now:
                h1 = "Kelebek lisans geçersiz"
                h2 = "Girdiğiniz lisansın süresi dolmuş."
            else:
                logger.info("Date is not over. Verified.")
                self.enable_licence_features()
                return
            
        dialog = licence_dialogs.LisansDialog(header_text=h1, subheader_text=h2, found_key=key, found_date=end_date)

        if not dialog.code:
            logger.info("Validation refused. Exiting the application.")
            exit()
            
        elif dialog.code == 1:
            self.enable_licence_features()
            logger.info("Validation succeed. Starting the application.")
            
        elif dialog.code == -1:
            logger.info("Skipping licence validation. Starting the application.")
    
    def validate_env_vars(self, key, end_date, skip_date):
        is_key = key != "BLANK"
        is_end_date = end_date != "BLANK"
        is_skip_date = skip_date != "BLANK"
        isses = [is_key, is_end_date, is_skip_date]

        # BOZULMUŞ .env DOSYASI
        if all(isses):
            return -1
        elif not is_key and is_end_date:
            return -1
        elif is_key and not is_end_date:
            return -1

        # NORMAL DURUMLAR        
        elif not is_key and not is_end_date and is_skip_date:
            # Daha önce geçilmiş
            return 0
        elif not is_key and not is_end_date:
            # Daha önce hiç giriş yapılmamış
            return 1
        elif is_key and is_end_date:
            # Daha önce giriş yapılmış
            return 2
        
        
    def enable_licence_features(self):
        # TODO MAKE A LOGIC TO ENABLE SOME CONSTANT VALUES WHICH ARE ENABLING SPESIFIC FEATURES
        self.licenced = True
    
    def set_menu_bar(self):
        self.actionResetAllData.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash-2.svg")))
        self.actionSettings.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "settings.svg")))
        self.actionLicense.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "key.svg")))
        
    def set_signs(self):
        """
        Sets the signals, buttons or etc. which has relationship between them.
        """
        self.actionResetAllData.triggered.connect(lambda: print("Reset all data action has just triggered"))
        self.actionSettings.triggered.connect(self.settings_dialog)
        self.actionLicense.triggered.connect(lambda: print("License key action has just triggered"))
        self.tabWidget.currentChanged.connect(lambda index: self.tab_changed(index))

    def tab_changed(self, index: int):
        if index == 1:
            if self.schoolInfosVLayout.count():
                child = self.schoolInfosVLayout.takeAt(0)
                del child
            self.schoolInformationsFrame = school_infos_frame.SchoolInformationsFrame()
            self.schoolInfosVLayout.addWidget(self.schoolInformationsFrame)    

        elif index == 2:
            if self.studentsVLayout.count():
                child = self.studentsVLayout.takeAt(0)
                del child
            self.studentsFrame = students_frame.StudentsFrame()
            self.studentsVLayout.addWidget(self.studentsFrame)
        
        elif index == 3:
            if self.classroomsVLayout.count():
                child = self.classroomsVLayout.takeAt(0)
                del child
            self.classroomsFrame = classrooms_frame.ClassroomsFrame()
            self.classroomsVLayout.addWidget(self.classroomsFrame)
            
        elif index == 4:
            if self.createExamVLayout.count():
                child = self.createExamVLayout.takeAt(0)
                del child
            self.createExamFrame = create_exam_frame.CreateExamBaseFrame()
            self.createExamVLayout.addWidget(self.createExamFrame)
            
        elif index == 5:
            if self.savedExamsVLayout.count():
                child = self.savedExamsVLayout.takeAt(0)
                del child
            self.savedExamsFrame = saved_exams_frame.SavedExamsFrame()
            self.savedExamsVLayout.addWidget(self.savedExamsFrame)
            
    def set_ui(self):
        """
        This function, adds custom widgets and waits for signals comes from buttons.
        """
        self.mainPageTextBrowser.setReadOnly(True)
        self.licenceTextBrowser.setReadOnly(True)
        
        self.schoolInformationsFrame = school_infos_frame.SchoolInformationsFrame()
        self.studentsFrame = students_frame.StudentsFrame()
        self.classroomsFrame = classrooms_frame.ClassroomsFrame()
        self.createExamFrame = create_exam_frame.CreateExamBaseFrame()
        self.savedExamsFrame = saved_exams_frame.SavedExamsFrame()
        
        self.schoolInfosVLayout.addWidget(self.schoolInformationsFrame)
        self.studentsVLayout.addWidget(self.studentsFrame)
        self.classroomsVLayout.addWidget(self.classroomsFrame)
        self.createExamVLayout.addWidget(self.createExamFrame)
        self.savedExamsVLayout.addWidget(self.savedExamsFrame)
        
    def settings_dialog(self):
        dialog = SettingsDialog()

    
    def sws(self):
        """
        Adjust the window settings
        """
        if self.licenced:
            self.setWindowTitle("Kelebek sistemi")
        else:
            self.setWindowTitle("Kelebek Sistemi - Lisanslanmamış") 
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "Images", "img", "butterfly.png")))
        self.show()
    

class SettingsDialog(QDialog):
    themes = {
        0: "auto",
        1: "light",
        2: "dark"
    }
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "ayarlar_dialog.ui"), self)
        
        self.set_signals()
        self.set_ui()
        self.set_ws()

    def set_signals(self):
        self.saveApplyBtn.clicked.connect(self.restart_application)
        self.discardBtn.clicked.connect(self.close)
    def set_ui(self):
        current_theme = database.get_theme()
        for index, theme in enumerate(list(self.themes.values())):
            if current_theme == theme:
                self.themeComboBox.setCurrentIndex(index)
                return
    
    def restart_application(self):
        theme_index = self.themeComboBox.currentIndex()
        theme = self.themes[theme_index]
        database.set_theme(theme)
        
        QApplication.quit()  # Mevcut uygulamayı kapatır
        subprocess.Popen([sys.executable] + sys.argv)

    def set_ws(self):
        self.setWindowTitle("Ayarlar")
        self.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())