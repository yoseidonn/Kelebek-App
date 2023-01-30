from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from App import database
from App.colors import COLOR_PALETTE
import os, sys, random

COLORS = list(COLOR_PALETTE.keys())
random.shuffle(COLORS)

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

        self.etw = examTable
        self.glw = gradeList
        self.clw = classroomList
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
        self.et_set_signals()
        self.gl_set_signals()
        self.cl_set_signals()
        
        self.et_adjust_settings()
        self.gl_adjust_settings()
        self.cl_adjust_settings()

        self.et_draw()
        self.gl_draw()
        self.cl_draw()
        
    def set_ui(self):
        pass
    
    def set_signals(self):
        self.createButton.pressed.connect(self.create)
    ######################################################
    def et_set_signals(self):
        self.addButton.clicked.connect(self.et_add_exam)
        self.removeButton.clicked.connect(self.et_remove_exam)
        self.removeAllButton.clicked.connect(lambda: self.et_remove_exam(all = True))
        self.inputPlace.textChanged.connect(self.et_set_white)
        self.etw.itemSelectionChanged.connect(self.et_selection_changed)

    def cl_set_signals(self):
        self.clw.itemClicked.connect(self.cl_item_clicked)
    ######################################################
    def refresh_item_status(self):
        #Seçili sınav adı değiştiği için hem o sınava dahil sınıflar hem de itemler üzerinde gezip ismi uyuşanları aktif yap.
        for item in self.gradeItems:
            item.setFlags(Qt.NoItemFlags)

        usedItems = list()
        for examName in self.exams:
            items = self.exams[examName]["items"]
            usedItems.extend(items)
        
        for item in self.gradeItems:
            if not (item in usedItems):
                item.setFlags(Qt.ItemIsEnabled)
                
    def et_selection_changed(self):
        ### IMPLEMENT THIS ALGORITHM LATER ON
        items = self.etw.selectedItems()
        if len(items) == 0:
            return
        rowIndexes = set()
        for item in items:
            rowIndexes.add(item.row())

        rowIndex = max(rowIndexes)
        self.etw.selectRow(rowIndex)
        ###        
        self.selectedExamName = list(self.exams.keys())[rowIndex]
        self.refresh_item_status()
                
    def gl_item_clicked(self, item: QListWidgetItem):
        # checkState() returns 2 when box is checked, otherwise it returns 0
        flags = item.flags()
        if not (flags & Qt.ItemIsUserCheckable):
            gradeName = item.text()
            grade = self.grades[gradeName]

            index = list(self.exams.keys()).index(self.selectedExamName)
            current = int(self.etw.item(index, 1).text())
            toAdd = len(grade)
            all_used_grade_names = []
            for examName in self.exams:
                if examName != self.selectedExamName:
                    all_used_grade_names.extend(self.exams[examName]["gradeNames"])
            
            if gradeName in all_used_grade_names:
                print("bu sınıf seçili. lütfen önce iptal edin.")
                return
            
            if gradeName in self.exams[self.selectedExamName]["gradeNames"]:
                #Değeri azalt ve itemi çıkart
                self.exams[self.selectedExamName]["items"].remove(item)
                self.exams[self.selectedExamName]["gradeNames"].remove(gradeName)
                self.etw.item(index, 1).setText(f"{current - toAdd}")
                #TEKRAR AKTİF VE RENKSİZ YAP
                item.setFlags(Qt.ItemIsEnabled)
                item.setBackground(QColor("white"))
                return
            
            #Değeri arttır ve itemi ekle
            self.exams[self.selectedExamName]["items"].append(item)
            self.exams[self.selectedExamName]["gradeNames"].append(gradeName)
            self.etw.item(index, 1).setText(f"{current + toAdd}")
            #RENK EKLE
            index = list(self.exams).index(self.selectedExamName)
            color = self.etw.item(index, 0).background()
            item.setBackground(color)

    def cl_item_clicked(self, item: QListWidgetItem):
        flags = item.flags()
        if not (flags & Qt.ItemIsEnabled):
            self.classroomNames.append(item.text())
            item.setFlags(Qt.ItemIsEnabled)
        else:
            self.classroomNames.remove(item.text())
            item.setFlags(Qt.NoItemFlags)
            
    ################################################
    def et_draw(self):
        self.etw.setRowCount(len(self.exams))
        for rowInx, exam in enumerate(self.exams):
            examName = QTableWidgetItem(exam)
            count = 0
            for grade, students in self.exams[exam].items():
                count += len(students)

            count = QTableWidgetItem(str(count))
            self.etw.setItem(rowInx, 0, examName)
            self.etw.setItem(rowInx, 1, count)
            
            color = COLOR_PALETTE[COLORS[rowInx]]
            r, g, b = color
            self.etw.item(rowInx, 0).setBackground(QColor(r, g, b))
            self.etw.item(rowInx, 1).setBackground(QColor(r, g, b))
            
        self.etw.selectRow(len(self.exams) - 1)
        self.selectedExamName = list(self.exams.keys())[-1] if len(list(self.exams.keys())) != 0 else None
        print("ended")
        
    def gl_draw(self):
        # SINIF İSİMLERİ ITEM'E ÇEVİRİLİP LİSTEYE EKLENİR
        # HER ITEM DISABLED OLARAK AYARLANIR
        # DAHA SONRA SINAV DURUMUNA GÖRE "CHECKABLE VE ENABLED" YA DA "DISABLED" OLARAK DEĞİŞEBİLİR
        for item in self.gradeItems:
            item.setFlags(Qt.ItemIsSelectable)

        usedItems = list()
        for examName in self.exams:
            if examName != self.selectedExamName:
                usedItems.extend(self.exams[examName]["items"])

        for item in usedItems:
            item.setFlags(Qt.NoItemFlags)
            
    def cl_draw(self):
        pass
    
    ######################################################## Exam Table
    def et_add_exam(self):
        examName = self.inputPlace.text().strip().upper()
        if examName not in self.exams and examName != "":
            self.exams.update({examName: {}})
            self.exams[examName].update({"gradeNames": list(), "items": list()})
            self.selectedExamName = examName
            self.et_draw()
            self.inputPlace.clear()
            self.inputPlace.setStyleSheet(f"background-color: rgb(255, 255, 255);")
        else:
            self.inputPlace.setStyleSheet(f"background-color: rgb{COLOR_PALETTE['red']};")

    def et_remove_exam(self, all = False):
        if all:
            self.exams = {}
            self.gradeItems = []

            self.et_set_ts()
            self.et_draw()
            self.glw.clear()
            self.gl_set_ts()
            self.gl_draw()
        else:
            pass
    
    def et_set_white(self):
        color = ", ".join([str(i) for i in COLOR_PALETTE["red"]])
        if color in self.inputPlace.styleSheet():
            self.inputPlace.setStyleSheet("background-color: rgb(255, 255, 255);")

    ###########################
    def et_adjust_settings(self):
        self.etw.setColumnCount(2)
        columnHeaders = ["Sınav adı", "Öğrenci sayısı"]
        self.etw.setHorizontalHeaderLabels(columnHeaders)
        self.etw.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.etw.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.etw.setEditTriggers(QTableWidget.NoEditTriggers)
        self.etw.verticalHeader().hide()
     
    def gl_adjust_settings(self):
        for gradeName in self.gradeNames:
            item = QListWidgetItem(gradeName)
            self.gradeItems.append(item)
            self.glw.addItem(item) 
            
    def cl_adjust_settings(self):
        for classroomName in self.classroomsNames:
            item = QListWidgetItem(classroomName)
            item.setFlags(Qt.NoItemFlags)
            self.classroomItems.append(item)
            self.clw.addItem(item) 

    ########################
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
