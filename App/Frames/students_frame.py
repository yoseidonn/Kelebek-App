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
        self.selectedStudents = list()

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

        # TODO - Her secim degistigi zaman sadece yeni eklenen yerdeki ogrencileri secililere ekliyor, 
        # TODO - tum secili itemlerdeki ogrencileri selected listesine almanin bi yolunu bul.
        
        # Selection signals
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemClicked.connect(self.on_item_clicked)

        # Sorting signals
        self.table.horizontalHeader().sectionClicked.connect(self.sort)
        self.resetOrderButton.clicked.connect(self.draw_table)
        
    def change_button_statuses(self):
        selected_student_count = len(self.selectedStudents)
        student_count = len(self.ogrencilerList)
        if not student_count:
            self.deleteAllButton.setEnabled(False)
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)

        elif student_count:
            self.deleteAllButton.setEnabled(True)
            if self.selectedStudents:
                if selected_student_count > 1:
                    self.editButton.setEnabled(False)
                else:
                    self.editButton.setEnabled(True)

                self.deleteButton.setEnabled(True)
            else:
                self.editButton.setEnabled(False)
                self.deleteButton.setEnabled(False)
            
    def on_selection_changed(self):
        selecteds = self.table.selectedItems()
        # Bu fonksiyon öğrenciler tarafından tasarlanacak.
        # Tasarlanacak idi fakat yine kendim yaptim :')
        self.table.blockSignals(True)
        
        # Indexleri bul
        row_indexes = list()
        for item in selecteds:
            row_indexes.append(item.row())
        row_indexes = list(set(row_indexes))
        
        # Her indexin gosterdigi satiri sec
        for row_ind in row_indexes:
            for col_ind in range(5):
                item: QTableWidgetItem = self.table.item(row_ind, col_ind)
                item.setSelected(True)
        
        # Secili indexlerde olan ogrencilerden olusan bir listeyi comphrension kullanarak secili ogrenciler listesine ata
        self.selectedStudents = [self.ogrencilerList[row_ind] for row_ind in row_indexes]
        self.table.blockSignals(False)
        self.change_button_statuses()
        
    def on_item_clicked(self, item: QTableWidgetItem):
        row = item.row()
        self.table.selectRow(row)
        self.selectedStudents = [self.ogrencilerList[row]]
        return
        
    def de_select_all_items(self):
        self.table.blockSignals(True)
        selecteds = self.table.selectedItems()

        for item in selecteds:
            row, col = item.row(), item.column()
            item = self.table.item(row, col)
            item.setSelected(False)

        self.selectedStudents = []
        self.table.blockSignals(False)
        self.change_button_statuses()

    def sort(self, sectionIndex):
        self.table.blockSignals(True)
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
            
        self.table.blockSignals(False)
        
    def draw_table(self, searchBy = False, order = False, sectionIndex = 0):
        self.change_button_statuses()
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
        self.change_button_statuses()

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
            student_numbers = [student[0] for student in self.selectedStudents]
            database.remove_students(numbers = student_numbers)
            
        self.ogrencilerList = database.get_all_students()
        self.de_select_all_items()
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
        self.table.setSelectionMode(QAbstractItemView.ContiguousSelection)
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
