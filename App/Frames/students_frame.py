from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from App import excel_reader, database
from App.logs import logger
import os

BASE_DIR = os.getenv("BASE_DIR")


class StudentsFrame(QFrame):
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
            #print(self.table.itemAt(QPoint(0, self.table.selectedItems()[0].row())).text())
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
        # Empty style sheets meant to make it normal
        self.noIn.textChanged.connect(lambda: self.noIn.setStyleSheet(""))
        self.nameIn.textChanged.connect(lambda: self.nameIn.setStyleSheet(""))
        self.surnameIn.textChanged.connect(lambda: self.surnameIn.setStyleSheet(""))
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
