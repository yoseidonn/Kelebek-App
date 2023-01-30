from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
import _database as database
from _colors import COLOR_PALETTE
import os, sys, random

COLORS = list(COLOR_PALETTE.values())
random.shuffle(COLORS)


class ExamFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join("Forms", "yeni_sinav_frame_demo.ui"), self)
        self.examStruct = ExamStruct(self.examTable, self.gradeList, self.classroomList, self.examNameIn, self.addButton, self.removeButton, self.removeAllButton, self.createButton, self.algCombo, self.kizErkCheck, self.omyCheck, self)
        self.show()
        
class ExamStruct():
    # et_.. Exam Table
    # gl_.. Grade List
    def __init__(self,
                examTable: QTableWidget,        # Sınavlar
                gradeList: QListWidget,   # Sınıflar
                classroomList: QListWidget,     # Salonlar
                inputPlace: QLineEdit,          # Sınav adı
                addButton: QPushButton,         # Sınavı ekle
                removeButton: QPushButton,      # Seçili sınavı sil
                removeAllButton: QPushButton,   # Tüm sınavları sil
                createButton: QPushButton,      # Sınavı oluştur
                algorithmCombo: QComboBox,      # Kalan özellikleri ekle ve ardından butona tıklanınca exami oluşturup dene
                kizErkCheck: QCheckBox,         # Kız Erkek Yan Yana Oturmasın
                omyCheck: QCheckBox,            # Öğretmen Masasına Yerleştir
                sinavFrame):                    # YeniSinavFrame

        self.examTableWidget = examTable
        self.gradeListWidget = gradeList
        self.classroomListWidget = classroomList
        self.inputPlace = inputPlace
        self.addButton = addButton
        self.removeButton = removeButton
        self.removeAllButton = removeAllButton
        self.createButton = createButton
        self.algorithmCombo = algorithmCombo
        self.kizErkCheck = kizErkCheck
        self.omyCheck = omyCheck
        self.sinavFrame = sinavFrame

        # DATAS FROM DATABASE
        self.grades = database.get_all_students(withGrades=True)
        self.gradeNames = database.get_all_grade_names()
        self.classroomsNames = database.get_all_classrooms(onlyNames=True)

        # VARIABLES
        self.classroomItems = list()
        self.gradeCheckBoxes = list()
        self.classroomNames = list()
        self.exams = dict()
        self.selectedExamName = str()
        
        # RENDER THE FRAME
        self.set_ui()
        self.set_signals()
        
        self.adjust_widget_settings()

    def set_ui(self):
        pass
    
    def set_signals(self):
        self.addButton.clicked.connect(self.add_exam)
        self.examTableWidget.itemSelectionChanged.connect(self.examtable_selection_changed)

    def add_exam(self):
        examName = self.inputPlace.text().strip().upper()
        if len(examName) and (examName not in self.exams.keys()):
            examIndex = len(self.exams)
            color = COLORS[examIndex]
            
            self.exams.update({examName: {"gradeNames": [],
                                          "checkBoxes": [],
                                          "paletteColor": color
                                          }})
            self.draw_exam_table()

        else:
            self.inputPlace.setStyleSheet("background-color: ")

    def examtable_selection_changed(self):
        selection: list = self.examTableWidget.selectedItems()
        if len(selection):
            # Son satırı seç
            rowIndexes = []
            for item in selection:
                rowIndexes.append(item.row())

            rowIndex = max(rowIndexes)
            self.examTableWidget.selectRow(rowIndex)

            # Seçili sınavın rengini palet rengine ata
            keys = list(self.exams.keys())
            examName = keys[rowIndex]
            self.selectedExamName = examName                        # 3. Yorumda kullanılıyor.
            examColor = self.exams[examName]["paletteColor"]
            highLightColor = QColor(*examColor, 100)

            self.colorPalette.setColor(QPalette.Highlight, highLightColor)    
            self.examTableWidget.setPalette(self.colorPalette)
            
            # Herhangi bir sınavın checkBoxes listesinde bulunmayan tüm checkbox nesnelerini aktif et
            selectedBoxes = []
            for examName in self.exams:
                if examName != self.selectedExamName:
                    checkboxes = self.exams[examName]["checkBoxes"]
                    selectedBoxes.extend(checkboxes)

            for checkbox in self.gradeCheckBoxes:
                checkbox.setEnabled(True)
            
            for checkbox in selectedBoxes:
                print(checkbox.text())
                checkbox.setEnabled(False)

    def checkbox_clicked(self, checkbox: QCheckBox):
        print(f"{checkbox.text()} clicked")
        examIndex = list(self.exams.keys()).index(self.selectedExamName)
        gradeName = checkbox.text()
        grade = self.grades[gradeName]
        toAdd = len(grade)
        current = int(self.examTableWidget.item(examIndex, 1).text())
        
        #Değeri azalt ve itemi çıkart
        if gradeName in self.exams[self.selectedExamName]["gradeNames"]:
            self.exams[self.selectedExamName]["checkBoxes"].remove(checkbox)
            self.exams[self.selectedExamName]["gradeNames"].remove(gradeName)
            self.examTableWidget.item(examIndex, 1).setText(f"{current - toAdd}")
            # RENGI SIFIRLA
            checkbox.setStyleSheet("background-color: rgba(0,0,0,0)")
            
        #Değeri arttır ve itemi ekle
        else:
            self.exams[self.selectedExamName]["checkBoxes"].append(checkbox)
            self.exams[self.selectedExamName]["gradeNames"].append(gradeName)
            self.examTableWidget.item(examIndex, 1).setText(f"{current + toAdd}")
            #RENK EKLE
            color = self.exams[self.selectedExamName]["paletteColor"]
            r, g, b = color
            checkbox.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 100)")

        
    def draw_exam_table(self):
        self.examTableWidget.setRowCount(len(self.exams))
        for rowIndex, examName in enumerate(self.exams.keys()):
            # Get the count of all the students which are in the gradeNames list in the spesific exam
            studentCount = 0
            for gradeName in self.exams[examName]["gradeNames"]:
                studentCount += len(self.grades[gradeName])

            item1 = QTableWidgetItem(examName)  
            item2 = QTableWidgetItem(str(studentCount))
            self.examTableWidget.setItem(rowIndex, 0, item1)
            self.examTableWidget.setItem(rowIndex, 1, item2)
            
            color = self.exams[examName]["paletteColor"]
            r, g, b = color
            self.examTableWidget.item(rowIndex, 0).setBackground(QColor(r, g, b))
            self.examTableWidget.item(rowIndex, 1).setBackground(QColor(r, g, b))
            
        # Eğer silme ile çağrılmış ise ve geride sınav kalmamışsa None seç
        if len(self.exams.keys()):
            lastRowIndex = len(self.exams) - 1
            self.examTableWidget.selectRow(lastRowIndex)
            self.selectedExamName = list(self.exams.keys())[lastRowIndex]

        else:
            self.selectedExamName = None
    
    def draw_grade_table(self):
        for gradeName in self.gradeNames:
            item = QListWidgetItem()
            checkbox = QCheckBox(gradeName, self.sinavFrame)
            checkbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.checkbox_clicked(c))
            
            self.gradeListWidget.addItem(item)
            self.gradeListWidget.setItemWidget(item, checkbox)

            self.gradeCheckBoxes.append(checkbox)

    def draw_classroom_table(self):
        for classroomName in self.classroomsNames:
            item = QListWidgetItem()
            checkbox = QCheckBox(classroomName)
            self.classroomListWidget.addItem(item)
            self.classroomListWidget.setItemWidget(item, checkbox)
    
    def adjust_widget_settings(self):
        # Exams table
        self.examTableWidget.setColumnCount(2)
        columnHeaders = ["Sınav adı", "Öğrenci sayısı"]
        self.examTableWidget.setHorizontalHeaderLabels(columnHeaders)
        self.examTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.examTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.examTableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.examTableWidget.verticalHeader().hide()
        self.colorPalette = QPalette()
        self.examTableWidget.setPalette(self.colorPalette)
        
        # Grades table
        palette = QPalette()
        palette.setColor(QPalette.Highlight, QColor(214, 214, 214))
        self.draw_exam_table()
        self.draw_grade_table()
        self.draw_classroom_table()
    
    def create(self):
        algorithm = self.algorithmCombo.currentText()
        options = [self.kizErkCheck.isChecked(), self.omyCheck.isChecked()]
        self.exam = Exam(exams = self.exams, classroomNames = self.classroomNames, algorithmName = algorithm, optionList = options)
        # Sonraki pencereye geç
        self.sinavFrame.next_step(karma = True)
        
    
class Exam():
    def __init__(self, exams: dict, classroomNames: list, algorithmName: str, optionList: list):
        self.exams = exams
        self.classroomNames = classroomNames
        self.algorithmName = algorithmName
        self.optionList = optionList

        self.restore_exams()
        
    def restore_exams(self):
        exams = dict()
        for examName in self.exams:
            grades = self.exams[examName]["gradeNames"]
            exams.update({examName: grades})
        self.exams = exams
                   
    def __str__(self):
        string = f"Sınavlar: {self.exams}\n\n{self.classrooms}\n\nÖğrenciler {self.algorithmName} ile karılacaktır.\n\nSeçenekler: {self.optionList}"
        return string


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = ExamFrame()
    app.exec_()