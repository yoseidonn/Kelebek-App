from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

from Client import client
from .HtmlCreater import classrooms_html, grades_html
from . import excel_reader, database, licence_dialogs, logs
from .logs import logger

from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import os, sys, datetime, logging

#os.environ['QT_DEBUG_PLUGINS']='1'
#os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-gpu-command-logging"
BASE_DIR = os.environ["BASE_DIR"]

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
        
        logger.info(f"[LICENCE] Active key: {key}\t Ending date: {end_date}\t Skip date: {skip_date}")
        result = self.validate_env_vars(key, end_date, skip_date)
        logger.info(result)

        h1, h2 = "Kelebek lisansı bulunamadı", "Eğer sahipseniz anahtarınızı girin ya da yeni bir anahtar alın."

        # Bozuk .env DOSYASI
        if result == -1:
            with open(".env", "w", encoding="utf-8") as file:
                file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://185.87.252.226")
                
        # Daha önce geçilmiş
        elif result == 0:
            year, month, day = [int(i) for i in skip_date.split("-")]
            skip_date = datetime.datetime(year, month, day)
            two_days_later = skip_date + datetime.timedelta(days=2)
            now = datetime.datetime.now()
            if two_days_later > now:
                # İki gün geçmemiş, doğrulamayı atla
                logger.info("It's not been too much after last validation skip.")
                return
            else:
                # İki gün geçmiş, tekrar doğrulama iste
                logger.info("It's been two days after last validation skip.")
                with open(".env", "w", encoding="utf-8") as file:
                    file.write(f"LICENCE_KEY=\nEND_DATE=\nSKIP_DATE=\nSERVER_IP=http://185.87.252.226")    
            
        # Hiç giriş yapılmamış
        elif result == 1:
            pass
        
        # Daha önce giriş yapılmış
        elif result == 2:
            year, month, day = [int(i) for i in self.found_date.split("-")]
            end_date = datetime.datetime(year, month, day)
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
        self.reset_all.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "trash-2.svg")))
        
    def set_signs(self):
        """
        Sets the signals, buttons or etc. which has relationship between them.
        """
        # OKUL BILGILERI
        actSchool = QAction(QIcon(os.path.join(BASE_DIR, "Images","img", "school.png")), "Okul bilgileri", self)
        actSchool.triggered.connect(self.okul_frame)
        self.toolBar.addAction(actSchool)
        # OGRENCILER
        actOgrenciler = QAction(QIcon(os.path.join(BASE_DIR, "Images","img", "student.png")), "Öğrenciler", self)
        actOgrenciler.triggered.connect(self.ogrenciler_frame)
        self.toolBar.addAction(actOgrenciler)
        # SALONLAR
        actSalonlar = QAction(QIcon(os.path.join(BASE_DIR, "Images","img", "classroom.png")), "Salonlar", self)
        actSalonlar.triggered.connect(self.salonlar_frame)
        self.toolBar.addAction(actSalonlar)
        # SINAV OLUŞTUR
        actNewExam = QAction(QIcon(os.path.join(BASE_DIR, "Images","img", "test.png")), "Yeni sınav oluştur", self)
        actNewExam.triggered.connect(self.yeni_sinav_frame)
        self.toolBar.addAction(actNewExam)
        # ÇIKTILAR
        actShowExams = QAction(QIcon(os.path.join(BASE_DIR, "Images", "icon", "list.svg")), "Sınavları göster", self)
        actShowExams.triggered.connect(self.sinavlar_frame)
        self.toolBar.addAction(actShowExams)
        # GOZETMEN
        #actGozetmen = QAction()
        #actGozetmen.triggered.connect(self.gozetmen_ata_frame)
        # VERILER
        #actVeriler = QAction()
        #actVeriler.triggered.connect(self.veriler)

    def set_ui(self):
        """
        This function, adds custom widgets and waits for signals comes from buttons.
        """
        self.welcomeText.setReadOnly(True)
        self.licenceText.setReadOnly(True)
        
        self.okulBilgileriFrame = OkulBilgileriFrame()
        self.ogrencilerFrame = OgrencilerFrame()
        self.salonlarFrame = SalonlarFrame()
        self.yeniSinavFrame = YeniSinavFrame()
        self.sinavlarFrame = SinavlarFrame()

        self.okulBilgileriFrame.setVisible(False)
        self.ogrencilerFrame.setVisible(False)
        self.salonlarFrame.setVisible(False)
        self.yeniSinavFrame.setVisible(False)
        self.sinavlarFrame.setVisible(False)

        self.frames = {
            "okulBilgileriFrame": self.okulBilgileriFrame,
            "ogrencilerFrame": self.ogrencilerFrame,
            "salonlarFrame": self.salonlarFrame,
            "yeniSinavFrame": self.yeniSinavFrame,
            "sinavlarFrame": self.sinavlarFrame,
            "textFrame": self.textFrame,
        }
        [self.MainLayout.addWidget(self.frames[key]) for key in self.frames]
    
    def okul_frame(self):
        if self.frames["okulBilgileriFrame"].isVisible():
            [self.frames[key].setVisible(False) for key in self.frames]
            self.textFrame.setVisible(True)
        else:
            [self.frames[key].setVisible(False) for key in self.frames]
            self.frames["okulBilgileriFrame"] = OkulBilgileriFrame()
            self.MainLayout.addWidget(self.frames["okulBilgileriFrame"])

    def ogrenciler_frame(self):
        if self.frames["ogrencilerFrame"].isVisible():
            [self.frames[key].setVisible(False) for key in self.frames]
            self.textFrame.setVisible(True)
        else:
            [self.frames[key].setVisible(False) for key in self.frames]
            self.frames["ogrencilerFrame"] = OgrencilerFrame()
            self.MainLayout.addWidget(self.frames["ogrencilerFrame"])

    def salonlar_frame(self):
        if self.frames["salonlarFrame"].isVisible():
            [self.frames[key].setVisible(False) for key in self.frames]
            self.textFrame.setVisible(True)
        else:
            [self.frames[key].setVisible(False) for key in self.frames]
            self.frames["salonlarFrame"] = SalonlarFrame()
            self.MainLayout.addWidget(self.frames["salonlarFrame"])

    def yeni_sinav_frame(self):
        self.yeniSinavFrame = YeniSinavFrame()

        if self.frames["yeniSinavFrame"].isVisible():
            [self.frames[key].setVisible(False) for key in self.frames]
            self.textFrame.setVisible(True)
        else:
            [self.frames[key].setVisible(False) for key in self.frames]
            self.frames["yeniSinavFrame"] = YeniSinavFrame()
            self.MainLayout.addWidget(self.frames["yeniSinavFrame"])

    def sinavlar_frame (self):
        if self.frames["sinavlarFrame"].isVisible():
            [self.frames[key].setVisible(False) for key in self.frames]
            self.textFrame.setVisible(True)
        else:
            [self.frames[key].setVisible(False) for key in self.frames]
            self.frames["sinavlarFrame"] = SinavlarFrame()
            self.MainLayout.addWidget(self.frames["sinavlarFrame"])

    def gozetmen_ata_frame(self):
        pass

    def veriler(self):
        pass

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

class OkulBilgileriFrame(QFrame):
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

    def update_buttons_visibility(self, schoolName = False, managerName = False, typee = False):
        if schoolName:
            [btn.setVisible(True) for btn in self.schoolNameButtons]
        
        elif managerName:
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
    
class OgrencilerFrame(QFrame):
    def __init__(self):
        super().__init__()    
        loadUi(os.path.join(BASE_DIR, "Forms", "ogrenciler_frame.ui"), self)
        
        self.ogrencilerList = database.get_all_students()

        self.set_signs() #SIGNALS
        self.set_ts() #TABLE SETTINGS

    def set_signs(self):
        """
        Sets the signals, buttons or etc. which has relationship between them.
        """
        self.searchByCombo.currentIndexChanged.connect(self.change_search_by)
        self.searchButton.pressed.connect(lambda: self.draw_table(searchBy = self.searchByCombo.currentText()))
        self.importButton.clicked.connect(self.import_dialog)
        self.addButton.clicked.connect(self.add_dialog)
        self.editButton.clicked.connect(self.edit_dialog)
        self.deleteButton.clicked.connect(lambda: self.remove_student(removeBy = True))
        self.deleteAllButton.clicked.connect(lambda: self.remove_student(all = True))

        self.table.itemSelectionChanged.connect(self.select_row)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed) #KUTUCUK SECILINCE UYARI OLUSTURMA

        self.table.horizontalHeader().sectionClicked.connect(self.sort)
        self.resetOrderButton.clicked.connect(self.draw_table)
        
    def sort(self, sectionIndex):
        if sectionIndex == 0:
            self.draw_table(order=True, sectionIndex=sectionIndex)

        elif sectionIndex == 1:
            self.draw_table(order=True, sectionIndex=sectionIndex)

        elif sectionIndex == 2:
            self.draw_table(order=True, sectionIndex=sectionIndex)

        elif sectionIndex == 3:
            self.draw_table(order=True, sectionIndex=sectionIndex)

        elif sectionIndex == 4:
            self.draw_table(order=True, sectionIndex=sectionIndex)
            
    def draw_table(self, searchBy = False, order = False, sectionIndex = 0):
        BY_NO = "Numaraya göre"
        BY_FULLNAME = "Tam ada göre"
        BY_CLASS = "Sınıfa göre"

        if order:
            self.ogrencilerList = sorted(self.ogrencilerList, key=lambda ogrenci: ogrenci[sectionIndex])
            self.set_table_items()
            return
        
        searchContent = self.searchIn.text().strip().upper()
        if searchContent == "":
            self.ogrencilerList = database.get_all_students()

        elif searchBy == BY_NO:
            self.ogrencilerList = database.get_all_students(number = searchContent)

        elif searchBy == BY_FULLNAME:
            self.ogrencilerList = database.get_all_students(fullname = searchContent)

        elif searchBy == BY_CLASS:
            self.ogrencilerList = database.get_all_students(grade = searchContent)

        self.set_table_items()

    def set_table_items(self):
        self.table.setRowCount(len(self.ogrencilerList))
        for rowInd, student in enumerate(self.ogrencilerList):
            for columnInd, data_raw in enumerate(student):
                self.table.setItem(rowInd, columnInd, QTableWidgetItem(str(data_raw)))

        self.table.show()

    def change_search_by(self):
        self.searchBy = self.searchByCombo.currentText()

    def select_row(self):
        items = self.table.selectedItems()
        rowIndexes = set()
        for item in items:
            rowIndexes.add(item.row())

        rowIndex = min(rowIndexes)
        self.table.selectRow(rowIndex)        

    def import_dialog(self):
        dialog = QFileDialog(caption="Dosya seçiniz", filter="(*.xls)")
        if dialog.exec_() == dialog.Accepted:
            filePath = str(dialog.selectedFiles()[0])
        else:
            return
    
        ogrencilerList = excel_reader.get_workbook_content(filePath)
        database.add_multiple_students(students = ogrencilerList)
    
        self.ogrencilerList = database.get_all_students()
        self.draw_table()

    def add_dialog(self):
        dialog = EkleDuzenleDialog()
        if dialog.toAdd:
            database.add_one_student(dialog.student)

        self.ogrencilerList = database.get_all_students()
        self.draw_table()

    def edit_dialog(self):
        #ogrenci = get_ogrenci_by_satir_no()  -> Bu fonksiyon ogrenciler tarafindan tasarlanacaktir.
        dialog = EkleDuzenleDialog(ogrenci = [2949, "Yusuf", "Kiris", "9/A"])
        if dialog.toUpdate:
            database.update_student(dialog.student)
        
        self.ogrencilerList = database.get_all_students()
        self.draw_table()

    def remove_student(self, removeBy = False, all = False):
        if all:
            onaydialog = OgrencilerSilmeOnayDialog()
            if onaydialog.result:
                database.remove_all_students()

        elif removeBy:
            rowIndexes = [item.row() for item in self.table.selectedItems()]
            for rowIndex in rowIndexes:
                lastIndex = rowIndex
                if rowIndex != lastIndex:
                    pass
            # TÜM SEÇİLİ SATIRLARIN UZUNLUĞUNU KONTROL ET. EĞER 1 TANE SATIR SEÇİLİ İSE ONUN NUMARASINA BAK VE SİL
            print(self.table.itemAt(QPoint(0, self.table.selectedItems()[0].row())).text())
            database.remove_one_student(number = self.table.itemAt(QPoint(0, self.table.selectedItems()[0].row())).text())

        self.ogrencilerList = database.get_all_students()
        self.draw_table()

    def add_student(self):
        no = int(self.noIn.text().strip())              #
        name = self.nameIn.text().strip().upper()       #
        surname = self.surnameIn.text().strip().upper() #
        grade = self.gradeCombo.currentText()           #   INPUTS
        classs = self.classCombo.currentText()          #
        gc = grade + "/" + classs                       #
        if "Sınıf" == grade or "Şube" == classs :
            return
            
        student = [no, name, surname, gc]               #

        database.add_one_student(student = student)     #   ADD TO DATABASE

        self.draw_table()                               #   REDRAW THE TABLE
        
        [input.clear() for input in [self.noIn, self.nameIn, self.surnameIn]] #CLEAR THE LINE_EDITS
        [combo.setCurrentIndex(0) for combo in [self.gradeCombo, self.classCombo]] #RESET THE COMBO_BOXES

    def on_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        #Bu fonksiyon öğrenciler tarafından tasarlanacak.
        pass
    
    def set_ts(self):
        """
        Set the 'table settings'.
        """
        self.table.setColumnCount(5)
        columnHeaders = ["Numara", "Ad", "Soyad", "Cinsiyet", "Sınıf"]
        self.table.setHorizontalHeaderLabels(columnHeaders)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.draw_table()    
   
class EkleDuzenleDialog(QDialog):
    def __init__(self, ogrenci = False):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "ekle_duzenle_dialog.ui"), self)
        self.lineEditItems = [self.noIn, self.nameIn, self.surnameIn]
        self.comboBoxItems = [self.gradeCombo, self.classCombo]
        self.student = ogrenci
        self.toUpdate = False
        self.toAdd = False
        
        self.set_signals()
        
    def set_signals(self):
        self.noIn.textChanged.connect(lambda: self.noIn.setStyleSheet("background-color: white;"))
        self.nameIn.textChanged.connect(lambda: self.nameIn.setStyleSheet("background-color: white;"))
        self.surnameIn.textChanged.connect(lambda: self.surnameIn.setStyleSheet("background-color: white;"))
        self.saveButton.clicked.connect(self.check)
        self.exitButton.clicked.connect(self.close)

        if not self.student:
            self.setWindowTitle("Öğrenci ekle")
        else:
            self.set_values()
            self.setWindowTitle("Öğrenci bilgilerini düzenle")

        self.set_ws()
    
    def set_values(self):
        [lineEdit.setText(str(data)) for lineEdit, data in zip(self.lineEditItems, self.student)]
        grade, classs = self.student[-1].split("/")
        self.gradeCombo.setCurrentText(grade)
        self.classCombo.setCurrentText(classs)

    def check(self):
        no = self.noIn.text().strip()
        name = self.nameIn.text().strip().upper()
        surname = self.surnameIn.text().strip().upper()
        grade = self.gradeCombo.currentText() + "/" + self.classCombo.currentText()
        sex = self.sexCombo.currentText()
        student = [no, name, surname, sex, grade]
        
        if not no.isnumeric():
            self.noIn.setStyleSheet("background-color: red;")
            return
        elif not name.isalpha():
            self.nameIn.setStyleSheet("background-color: red;")
            return
        elif not surname.isalpha():
            self.surnameIn.setStyleSheet("background-color: red;")
            return

        if all(map(len, student)):
            if not self.student:
                database.add_one_student(student=student)
            else:
                database.update_student(student=student)
            self.close()

    def set_ws(self):
        """
        Adjust the window settings
        """
        self.exec_()


class OgrencilerSilmeOnayDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "ogrenciler_silme_onay_dialog.ui"), self)
        self.checkk()

        self.okayButton.clicked.connect(self.closee)
        self.checkBox.stateChanged.connect(self.checkk)
        
        self.result = False
        self.set_ws()

    def checkk(self):
        if self.checkBox.isChecked():
            self.okayButton.setEnabled(True)
        else:
            self.okayButton.setEnabled(False)

    def closee(self):
        self.result = True
        self.close()

    def set_ws(self):
        """
        Adjust the window settings
        """
        self.exec_()


class SalonlarFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "salonlar_frame.ui"), self)
        from .Structs.classroom_struct import ClassroomStruct
        buttons = [self.addColumn, self.removeColumn, self.addRow, self.removeRow]
        self.Classroom = ClassroomStruct(self.grid, self.ogretmenSolFrame, self.ogretmenSagFrame, self.kacliCombo, self.yonCombo, buttons = buttons)
        
        self.buttons = [self.addButton, self.saveButton, self.removeButton, self.cancelButton]
        self.classroomNames = database.get_all_classrooms(onlyNames=True)
        self.classrooms = database.get_all_classrooms()

        self.set_ui()
        self.set_signals()
        self.draw_list()

    def set_ui(self):
        self.solGraphic.setStyleSheet(f"border-image: url({os.path.join(BASE_DIR, 'Images','img', 'teacher_desk.png')})")
        self.sagGraphic.setStyleSheet(f"border-image: url({os.path.join(BASE_DIR, 'Images','img', 'teacher_desk.png')})")
        self.cancelButton.setIcon(QIcon(os.path.join(BASE_DIR, 'Images','icon', 'x.svg')))

        self.addColumn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "plus.svg")))
        self.addRow.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "plus.svg")))
        self.removeColumn.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "minus.svg")))
        self.removeRow.setIcon(QIcon(os.path.join(BASE_DIR, "Images", "icon", "minus.svg")))
        [button.setVisible(False) for button in self.buttons if button is not self.addButton]
        self.salonNameIn.setPlaceholderText("Salon adı")

    def set_signals(self):
        self.classroomList.itemClicked.connect(self.classroom_item_clicked)
        self.addButton.clicked.connect(self.add_button_clicked)
        self.saveButton.clicked.connect(self.save_button_clicked)
        self.cancelButton.clicked.connect(self.cancel_button_clicked)
        self.removeButton.clicked.connect(self.remove_button_clicked)

    def classroom_item_clicked(self, item: QListWidgetItem):
        classroomName = item.text()
        classroom = self.classrooms[classroomName]
        self.draw_selected_classroom(values = classroom)
        self.removeName = classroomName

    def add_button_clicked(self):
        self.save_button_clicked(add = True)
        
    def save_button_clicked(self, add = False):
        # Salonu ekle
        salonAdi = self.salonNameIn.text().strip().upper()
        ogretmenY = self.yonCombo.currentText()
        kacli = self.kacliCombo.currentText()
        duzen = ",".join([str(column.deskCount) for column in self.Classroom.columns])

        # Ekleme değilse sil ve tekrar kaydet, ekleme ise sadece ekle
        if not add:
            database.remove_classroom(classroomName = self.removeName)
        database.add_new_classroom(salonAdi, ogretmenY, kacli, duzen)

        # Ana haline döndür
        self.cancel_button_clicked()
        
        # Tabloyu çiz
        self.classrooms = database.get_all_classrooms()
        self.classroomNames = database.get_all_classrooms(onlyNames = True)
        self.draw_list()

    def cancel_button_clicked(self):
        self.Classroom._reset()
        self.Classroom.set_3x5()
        self.salonNameIn.clear()
    
        [button.setVisible(False) for button in self.buttons]
        self.addButton.setVisible(True)

    def remove_button_clicked(self):
        database.remove_classroom(classroomName = self.removeName)
        self.classrooms = database.get_all_classrooms()
        self.classroomNames = database.get_all_classrooms(onlyNames = True)
        self.draw_list()
        self.cancel_button_clicked()

    def draw_selected_classroom(self, values):
        [button.setVisible(True) for button in self.buttons]
        self.addButton.setVisible(False)

        name, teacherd, hspd, layout = values
        self.salonNameIn.setText(name)
        self.Classroom.set_layout(layout)
        self.yonCombo.setCurrentText(teacherd)
        self.kacliCombo.setCurrentText(hspd)
        
    def draw_list(self):
        self.classroomList.clear()
        self.classroomList.addItems(self.classroomNames)


class YeniSinavFrame(QFrame):
    MONTHS = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
        
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_frame.ui"), self)
        from .Structs.exam_struct import ExamStruct
        self.ExamStruct = ExamStruct(
            examTable = self.examTable,
            gradeList = self.gradeList,
            classroomList = self.classroomList,
            inputPlace = self.examNameIn,
            addButton = self.addButton,
            removeButton = self.removeButton,
            removeAllButton = self.removeAllButton,
            sidebyside_sitting = self.sidebyside_sitting,
            backtoback_sitting = self.backtoback_sitting,
            crossbycross_sitting = self.crossbycross_sitting,
            kizErkek = self.kizErkek,
            ogretmenMasasi = self.ogretmenMasasi,
            createButton = self.createButton,
            sinavFrame = self)

        self.isStarted = False

        self.set_ui()
        self.set_signals()
    
    def set_ui(self):
        self.mainFrame.setVisible(False)

    def set_signals(self):
        self.continueButton.clicked.connect(self.next_step) #PRE-EVENT SIGNAL
        self.masterExamNameIn.textChanged.connect(self.set_white)
        
    def next_step(self):
        if len(self.masterExamNameIn.text().strip()) == 0:
            self.set_red()
            return
            
        day = int(self.day.currentText())
        month = self.MONTHS[self.month.currentText()]
        year = int(self.year.currentText())
        date = datetime.datetime(year, month, day)
        tarih  = str(date.date())
            
        self.masterExamName = self.masterExamNameIn.text().strip()
        self.egitimOgretimYili = self.egitimOgretimCombo.currentText()
        self.donem = self.donemCombo.currentText().upper()
        self.kacinciYazili = self.doneminKacinciCombo.currentText().upper()
        self.tarih = tarih
        self.kacinciDers = self.dersSaatiCombo.currentText().upper()
        self.examInfos = [self.egitimOgretimYili.strip(), self.donem.strip(), self.kacinciYazili.strip(), self.tarih.strip(), self.kacinciDers.strip(), self.masterExamName.strip()]
        self.ExamStruct.examInfos = self.examInfos
        self.upperOfExamInfos.setVisible(False)
        self.mainFrame.setVisible(True)
        self.isStarted = True
        
    def reset(self):
        self.upperOfExamInfos.setVisible(True)
        self.mainFrame.setVisible(False)
        self.isStarted = False
            
    def set_white(self):
        self.masterExamNameIn.setStyleSheet("background-color: white;")
    
    def set_red(self):
        self.masterExamNameIn.setStyleSheet(f"background-color: rgb(255, 128, 128);")
    

class SinavlarFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "sinavlar_frame.ui"), self)
        from .Structs.display_struct_beta import Display
        
        buttons = [self.removeBtn, self.removeAllBtn, self.refreshAllBtn, self.archiveBtn, self.downloadsBtn]
        
        self.set_ui()
        toolBoxes = [self.examsToolBox, self.filesToolBox]
        listWidgets = [self.activeList, self.archiveList, self.classroomList, self.gradeList]
        self.Display = Display(toolBoxes=toolBoxes, listWidgets=listWidgets, webEngineView = self.wev, displayTitle = self.displayTitle, buttons = buttons, buttonsLayout = self.buttonsLayout)
        
    def set_ui(self):
        self.wev = QWebEngineView()
        self.displayLayout.addWidget(self.wev)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())