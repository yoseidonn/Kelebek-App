from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtTest import QTest

from .HtmlCreater import classrooms_html, students_html
from . import database, excel_reader
from pathlib import Path
import os, sys, datetime, pytz
import urllib.request as req
import urllib.error as err 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "mainwindow.ui"), self)

        """x = self.is_date_over()
        if x in ["NO_INTERNET", "ENDED"]:
            print(x)
            exit()"""
            
        self.set_signs()
        self.set_ui()
        self.sws()

    def set_signs(self):
        """
        Sets the signals, buttons or etc. which has relationship between them.
        """
        # OKUL BILGILERI
        actSchool = QAction(QIcon(os.path.join("Images","img", "school.png")), "Okul bilgileri", self)
        actSchool.triggered.connect(self.okul_frame)
        self.toolBar.addAction(actSchool)
        # OGRENCILER
        actOgrenciler = QAction(QIcon(os.path.join("Images","img", "student.png")), "Öğrenciler", self)
        actOgrenciler.triggered.connect(self.ogrenciler_frame)
        self.toolBar.addAction(actOgrenciler)
        # SALONLAR
        actSalonlar = QAction(QIcon(os.path.join("Images","img", "classroom.png")), "Salonlar", self)
        actSalonlar.triggered.connect(self.salonlar_frame)
        self.toolBar.addAction(actSalonlar)
        # SINAV OLUŞTUR
        actNewExam = QAction(QIcon(os.path.join("Images","img", "test.png")), "Yeni sınav oluştur", self)
        actNewExam.triggered.connect(self.yeni_sinav_frame)
        self.toolBar.addAction(actNewExam)
        # ÇIKTILAR
        actShowExams = QAction(QIcon(os.path.join("Images", "icon", "list.svg")), "Sınavları göster", self)
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
        self.textBrowser.setReadOnly(True)
        self.textBrowser2.setReadOnly(True)
        
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
    
    def is_date_over(self):
        try:
            res = req.urlopen('http://just-the-time.appspot.com/')
            print("internet var")
        except:
            print("internet yok")
            dialog = NoInternetDialog()
            return "NO_INTERNET"
        
        time_str = res.read().strip().decode()
        date, hour = time_str.split(" ")        
        year, month, day = date.split("-")
        hour, minute, second = hour.split(":")

        now = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

        endDay = datetime.datetime(2023, 2, 28, 12, 30, 0)
        if endDay >= now:
            return "NOT_ENDED"
        
        dialog = DateIsOverDialog()
        return "ENDED"

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
        self.setWindowTitle("Kelebek sistemi")
        self.setWindowIcon(QIcon(os.path.join("Images", "img", "butterfly.png")))
        self.show()

class DateIsOverDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "date_is_over_dialog.ui"), self)

        self.exitBtn.clicked.connect(self.close)
        self.textBrowser.setReadOnly(True)

        self.exec_()


class NoInternetDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "no_internet_dialog.ui"), self)

        self.exitBtn.clicked.connect(self.close)
        self.textBrowser.setReadOnly(True)
        
        self.exec_()


class OkulBilgileriFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "okul_bilgileri_frame.ui"), self)

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
        #gradeCounts, studentCounts, classroomCounts = infos
                
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

    
class OgrencilerFrame(QFrame):
    def __init__(self):
        super().__init__()    
        loadUi(os.path.join("Forms", "ogrenciler_frame.ui"), self)
        
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
            
        print("sort")

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
            onaydialog = OnayDialog()
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
        loadUi(os.path.join("Forms", "ekle_duzenle_dialog.ui"), self)
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


class OnayDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "onay_dialog.ui"), self)
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
    DICT_YON={"Solda": 0, "Sağda": 1}
    DICT_HSPD={"1'li": 0, "2'li": 1}

    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "salonlar_frame.ui"), self)
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
        self.solGraphic.setStyleSheet(f"border-image: url(./{os.path.join('Images','img', 'teacher_desk.png')})")
        self.sagGraphic.setStyleSheet(f"border-image: url(./{os.path.join('Images','img', 'teacher_desk.png')})")
        self.cancelButton.setIcon(QIcon(os.path.join('Images','icon', 'x.svg')))

        self.addColumn.setIcon(QIcon(os.path.join("Images", "icon", "plus.svg")))
        self.addRow.setIcon(QIcon(os.path.join("Images", "icon", "plus.svg")))
        self.removeColumn.setIcon(QIcon(os.path.join("Images", "icon", "minus.svg")))
        self.removeRow.setIcon(QIcon(os.path.join("Images", "icon", "minus.svg")))
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
        """# Salonu ekle
        salonAdi = self.salonNameIn.text().strip().upper()
        ogretmenY = self.yonCombo.currentText()
        kacli = self.kacliCombo.currentText()
        duzen = ",".join([str(column.deskCount) for column in self.Classroom.columns])
        database.remove_classroom(classroomName = self.removeName)

        database.add_new_classroom(salonAdi, ogretmenY, kacli, duzen)

        # Ana haline döndür
        self.cancel_button_clicked()

        # Listeyi bir daha çiz
        self.classrooms = database.get_all_classrooms()
        self.classroomNames = database.get_all_classrooms(onlyNames = True)
        self.draw_list()"""
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
        self.yonCombo.setCurrentIndex(self.DICT_YON[teacherd])
        self.Classroom.set_layout(layout)
        self.kacliCombo.setCurrentIndex(self.DICT_HSPD[hspd])

    def draw_list(self):
        self.classroomList.clear()
        self.classroomList.addItems(self.classroomNames)


class YeniSinavFrame(QFrame):
    MONTHS = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
        
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "yeni_sinav_frame.ui"), self)
        from .Structs.exam_struct import ExamStruct
        self.ExamStruct = ExamStruct(examTable = self.examTable,
                                    gradeList = self.gradeList,
                                    classroomList = self.classroomList,
                                    inputPlace = self.examNameIn,
                                    addButton = self.addButton,
                                    removeButton = self.removeButton,
                                    removeAllButton = self.removeAllButton,
                                    algorithmCombo = self.algCombo,
                                    kizErkCheck = self.kizErkCheck,
                                    omyCheck = self.omyCheck,
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
        self.examInfos = [self.egitimOgretimYili, self.donem, self.kacinciYazili, self.tarih, self.kacinciDers, self.masterExamName]
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
        loadUi(os.path.join("Forms", "sinavlar_frame.ui"), self)
        from .Structs.display_struct import Display
        
        buttons = [self.downloadBtn]
        
        self.set_ui()
        self.Display = Display(examsList = self.examsList, filesList = self.filesList, webEngineView = self.wev, buttons = buttons)
        
    def set_ui(self):
        self.wev = QWebEngineView()
        self.displayLayout.addWidget(self.wev)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
