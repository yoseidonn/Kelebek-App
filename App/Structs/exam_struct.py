from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from App import database
from App.colors import COLOR_PALETTE
from App.HtmlCreater import classrooms_html, students_html
from App.deploy import deploy_and_get_classrooms

from pathlib import Path
import os, sys, random, time

COLORS = list(COLOR_PALETTE.values())
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
        self.set_start_variables()
        
        # RENDER THE FRAME
        self.set_ui()
        self.set_signals()
        
        self.adjust_widget_settings()

    def set_start_variables(self):
        self.examInfos = list()             # self.egitimOgretimYili, self.donem, self.kacinciYazili, self.tarih, self.kacinciDers, self.masterExamName
        self.gradeCheckBoxes = list()       # To hold the checkboxes for enabling all when i need
        self.classroomNames = list()        # To hold the selected classroom names
        self.exams = dict()                 # To hold the exam names with gradenames
        self.selectedExamName = str()

    def set_ui(self):
        self.removeButton.setEnabled(False)
        self.removeAllButton.setEnabled(False)
    
    def set_signals(self):
        self.addButton.clicked.connect(self.add_exam)
        self.removeButton.clicked.connect(self.remove_exam)
        self.removeAllButton.clicked.connect(self.remove_all_exams)
        self.inputPlace.textChanged.connect(self.set_white)

        self.examTableWidget.itemSelectionChanged.connect(self.on_cell_change)

        self.createButton.clicked.connect(self.create)
        
    def add_exam(self):
        examName = self.inputPlace.text().strip().upper()
        if len(examName) and (examName not in self.exams.keys()):
            examIndex = len(self.exams)
            color = COLORS[examIndex]
            
            self.exams.update({examName: {"gradeNames": [],
                                          "checkBoxes": [],
                                          "paletteColor": color
                                          }})

            self.inputPlace.clear()
            self.draw_exam_table()

            self.removeButton.setEnabled(True)
            self.removeAllButton.setEnabled(True)

        else:
            self.set_red()       # Input place

    def remove_exam(self):
        del self.exams[self.selectedExamName]
        self.draw_exam_table()
        pass

    def remove_all_exams(self):
        self.set_start_variables()
        self.adjust_widget_settings()
        self.removeButton.setEnabled(False)
        self.removeAllButton.setEnabled(False)

    def on_cell_change(self):
        item = self.examTableWidget.currentItem()
        if item is None:
            return
        rowIndex = item.row()
        self.examTableWidget.selectRow(rowIndex)
        print("Row selected.", rowIndex)

        # Seçili sınavın rengini palet rengine ata
        keys = list(self.exams.keys())
        examName = keys[rowIndex]
        self.selectedExamName = examName                        # draw_exam_table da kullanılıyor
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

    def grade_checkbox_clicked(self, checkbox: QCheckBox):
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

    def classroom_checkbox_clicked(self, checkbox: QCheckBox):
        self.classroomNames.append(checkbox.text())
        
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
            print("Lastrow index", lastRowIndex)
            self.selectedExamName = list(self.exams.keys())[lastRowIndex]

        else:
            self.selectedExamName = None
    
    def draw_grade_table(self):
        for gradeName in self.gradeNames:
            item = QListWidgetItem()
            checkbox = QCheckBox(gradeName, self.sinavFrame)
            checkbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.grade_checkbox_clicked(c))
            
            self.gradeListWidget.addItem(item)
            self.gradeListWidget.setItemWidget(item, checkbox)

            self.gradeCheckBoxes.append(checkbox)

    def draw_classroom_table(self):
        for classroomName in self.classroomsNames:
            item = QListWidgetItem()
            checkbox = QCheckBox(classroomName, self.sinavFrame)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.classroom_checkbox_clicked(c))
            
            self.classroomListWidget.addItem(item)
            self.classroomListWidget.setItemWidget(item, checkbox)
    
    def adjust_widget_settings(self, reset = False):
        if reset:
            self.examTableWidget.clear()

            self.gradeListWidget.clear()
            self.gradeCheckBoxes = []

            self.classroomListWidget.clear()

            # Exams table
        # Tablo ayarlarını yap
        self.examTableWidget.setColumnCount(2)
        columnHeaders = ["Sınav adı", "Öğrenci sayısı"]
        self.examTableWidget.setHorizontalHeaderLabels(columnHeaders)
        self.examTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.examTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.examTableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.examTableWidget.verticalHeader().hide()
        # Bir renk paleti ekle
        self.colorPalette = QPalette()
        self.examTableWidget.setPalette(self.colorPalette)
        # Tek satır seçme
        self.examTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.examTableWidget.setSelectionBehavior(QTableWidget.SelectRows)

        self.draw_exam_table()
        self.draw_grade_table()
        self.draw_classroom_table()
    
    def set_white(self):
        self.inputPlace.setStyleSheet("background-color: white;")
    
    def set_red(self):
        self.inputPlace.setStyleSheet(f"background-color: rgb(255, 128, 128);")
    
    def create(self):
        algorithm = self.algorithmCombo.currentText()
        options = [self.kizErkCheck.isChecked(), self.omyCheck.isChecked()]
        self.exam = Exam(exams = self.exams, classroomNames = self.classroomNames, algorithmName = algorithm, optionList = options)

        self.deploy_step()
        
    def deploy_step(self):
        sonuc = deploy_and_get_classrooms(self.exam)
        if not sonuc:
            # Tekrar deneyiniz penceresi ekle
            print("[LOG] Yetersiz yer.")
            pass
        else:
            # Create files
            con1 = classrooms_html.create(self.examInfos, sonuc, self.exam.exams)
            con2 = students_html.create(self.examInfos, sonuc, self.exam.exams)

            self.show_result_frame(classroomsContainer = con1, studentsContainer = con2)
            self.sinavFrame.reset()
            
    def show_result_frame(self, classroomsContainer: list, studentsContainer: list):
        # Dialog sonucuna göre dosyayı ya kayıtlara taşı ya da sil
        cFilePath, cContent = classroomsContainer
        sFilePath, sContent = studentsContainer

        examPath = "_".join([self.examInfos[-1], self.examInfos[3], self.examInfos[4]])

        dialogSonuc = SonucDialog(classroomsHTML = cContent, studentsHTML = sContent).isAccepted
        if dialogSonuc:
            try:
                os.mkdir(os.path.join('Saved', examPath))
            except FileExistsError:
                pass
            Path(cFilePath).rename(os.path.join('Saved', examPath, 'salon_oturma_duzenleri.html'))
            Path(sFilePath).rename(os.path.join('Saved', examPath, 'sinif_listeleri.html'))

            #print(os.path.join('Saved', examPath, 'salon_oturma_duzenleri.html'))
            #print(os.path.join('Saved', examPath, 'sinif_listeleri.html'))
            
        else:
            os.remove(cFilePath)
            os.remove(sFilePath)

        os.rmdir(os.path.join('Temp', examPath))
    
class Exam():
    def __init__(self, exams: dict, classroomNames: list, algorithmName: str, optionList: list):
        self.exams = exams
        self.classroomNames = classroomNames
        self.algorithmName = algorithmName
        self.optionList = optionList

        self.restore_exams()
        
    def restore_exams(self):
        """
        Bu fonksiyon sonrasında bir önceki yapıda checkbox'ların davranışlarını yönetirken kullandığım,
        "checkBoxes" anahtarı karşılığındaki listeyi siler ve her sınav adının karşılığı sadece sınıf adları olan bir liste olur.
        """
        exams = dict()
        for examName in self.exams:
            grades = self.exams[examName]["gradeNames"]
            exams.update({examName: grades})
        self.exams = exams
                   
    def __str__(self):
        string = f"Sınavlar: {self.exams}\n\n{self.classrooms}\n\nÖğrenciler {self.algorithmName} ile karılacaktır.\n\nSeçenekler: {self.optionList}"
        return string

        
class SonucDialog(QDialog):
    def __init__(self, classroomsHTML, studentsHTML):
        super().__init__()
        loadUi(os.path.join("Forms", "sonuc_dialog.ui"), self)
        
        self.classroomsHTML = classroomsHTML
        self.studentsHTML = studentsHTML
        self.isAccepted = False

        self.wev = QWebEngineView()
        self.previewLayout.addWidget(self.wev)

        self.set_flw()
        self.set_signals()
        self.exec_()
    
    def set_signals(self):
        self.filesList.itemClicked.connect(self.fl_item_clicked)
        self.saveBtn.clicked.connect(lambda: self.close(key = True))
        self.discardBtn.clicked.connect(self.close)
        
    def fl_item_clicked(self, item: QListWidgetItem):
        print(item.text())
        if item.text() == 'Salon oturma düzenleri':
            self.wev.setHtml(self.classroomsHTML)

        else:
            self.wev.setHtml(self.studentsHTML)
        
    def close(self, key = False):
        # self.accept is just for close the window
        if key:
            self.isAccepted = True
            self.accept()
            return
        self.isAccepted = False
        self.accept()
        
    def set_flw(self):
        item1 = QListWidgetItem('Salon oturma düzenleri')
        item2 = QListWidgetItem('Sınıf listeleri')
        item1.setSelected(True)

        self.filesList.addItem(item1)
        self.filesList.addItem(item2)
        self.wev.setHtml(self.classroomsHTML)
        

if __name__ == '__main__':
    class ExamFrame(QFrame):
        def __init__(self):
            super().__init__()
            loadUi(os.path.join("Forms", "yeni_sinav_frame_demo.ui"), self)
            self.examStruct = ExamStruct(self.examTable, self.gradeList, self.classroomList, self.examNameIn, self.addButton, self.removeButton, self.removeAllButton, self.createButton, self.algCombo, self.kizErkCheck, self.omyCheck, self)
            self.show()
        
    app = QApplication(sys.argv)
    frame = ExamFrame()
    app.exec_()