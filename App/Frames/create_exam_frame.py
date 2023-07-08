from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from App.HtmlCreater import classrooms_html, grades_html
from App import database
from App.colors import COLOR_PALETTE
from App.logs import logger
from App.deploy import distribute

from dotenv import load_dotenv
from pathlib import Path
import os, sys, datetime, shutil


COLORS = list(COLOR_PALETTE.values())
BASE_DIR = os.getenv("BASE_DIR")
load_dotenv()



class CreateExamFrame(QFrame):
    MONTHS = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
        
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_frame.ui"), self)
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
        # Empty style sheets meant to make it normal
        self.masterExamNameIn.setStyleSheet("")
    
    def set_red(self):
        self.masterExamNameIn.setStyleSheet(f"background-color: rgb(255, 128, 128);")
        
        
class ExamStruct():
    # et_.. Exam Table
    # gl_.. Grade List
    def __init__(self,
            examTable: QTableWidget,        # Sınavlar
            gradeList: QListWidget,         # Sınıflar
            classroomList: QListWidget,     # Salonlar
            inputPlace: QLineEdit,          # Sınav adı
            addButton: QPushButton,         # Sınavı ekle
            removeButton: QPushButton,      # Seçili sınavı sil
            removeAllButton: QPushButton,   # Tüm sınavları sil
            createButton: QPushButton,      # Sınavı oluştur
            sidebyside_sitting: QCheckBox,
            backtoback_sitting: QCheckBox,
            crossbycross_sitting: QCheckBox,
            kizErkek: QCheckBox,            # Kız Erkek Yan Yana Oturmasın
            ogretmenMasasi: QCheckBox,      # Öğretmen Masasına Yerleştir
            sinavFrame):                    # YeniSinavFrame

        self.examTableWidget = examTable
        self.gradeListWidget = gradeList
        self.classroomListWidget = classroomList
        self.inputPlace = inputPlace
        self.addButton = addButton
        self.removeButton = removeButton
        self.removeAllButton = removeAllButton
        self.createButton = createButton
        self.sidebyside_sitting = sidebyside_sitting
        self.backtoback_sitting = backtoback_sitting
        self.crossbycross_sitting = crossbycross_sitting
        self.kizErkek = kizErkek
        self.ogretmenMasasi = ogretmenMasasi
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
        try:
            checkboxes = self.exams[self.selectedExamName]["checkBoxes"]
        except KeyError as e:
            print(e)
            return

        for checkbox in checkboxes:
            checkbox.setStyleSheet("")
            checkbox.setChecked(False)

        self.exams.pop(self.selectedExamName)
        for examName in self.exams:
            for checkbox in self.exams[examName]["checkBoxes"]:
                color = self.exams[examName]["paletteColor"]
                r, g, b = color
                checkbox.setChecked(True)
                checkbox.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 100)") 
        
        self.draw_exam_table()

    def remove_all_exams(self):
        try:
            checkboxes = self.exams[self.selectedExamName]["checkBoxes"]
        except KeyError as e:
            print(e)
            return
        
        for checkbox in checkboxes:
                checkbox.setStyleSheet("")
                checkbox.setChecked(False)
        
        for examName in list(self.exams.keys()):
            self.exams.pop(examName)
            for eName in self.exams:
                for checkbox in self.exams[eName]["checkBoxes"]:
                    color = self.exams[eName]["paletteColor"]
                    r, g, b = color
                    checkbox.setChecked(True)
                    checkbox.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 100)") 
        
        self.draw_exam_table()

    def on_cell_change(self):
        item = self.examTableWidget.currentItem()
        if item is None:
            return
        rowIndex = item.row()

        self.examTableWidget.selectRow(rowIndex)
        print("Row selected.", rowIndex)

        # Seçili sınavın rengini palet rengine ata
        keys = list(self.exams.keys())
        if not keys:
            return
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
        self.gradeListWidget.setStyleSheet("")
        if self.selectedExamName is None:
            return

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
            checkbox.setStyleSheet("")
            
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
        self.classroomListWidget.setStyleSheet("")
        
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
        self.examTableWidget.setItemDelegate(HighlightDelegate())
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
        self.inputPlace.setStyleSheet("")
    
    def set_red(self):
        self.inputPlace.setStyleSheet(f"background-color: rgb(255, 128, 128);")
    
    def create(self):
        rules = [self.sidebyside_sitting, self.backtoback_sitting, self.crossbycross_sitting, self.kizErkek.isChecked(), self.ogretmenMasasi.isChecked()]
        self.exam = Exam(exams = self.exams, classroomNames = self.classroomNames, rules = rules)

        self.deploy_step()
        
    def deploy_step(self):
        flag = False
        if not len(self.classroomNames):
            self.classroomListWidget.setStyleSheet(f"background-color: rgb(255, 128, 128);")
            flag = True
        all_grades = [value["gradeNames"] for value in self.exams.values()]
        if not all(all_grades):
            self.gradeListWidget.setStyleSheet(f"background-color: rgb(255, 128, 128);")
            flag = True
        if flag:
            return True
        
        sonuc = distribute(self.exam)
        if not sonuc:
            # Tekrar deneyiniz penceresi ekle
            message = """Seçili şubelerdeki öğrencileri dağıtmak için yeterli yer bulunamadı. 
Lütfen daha fazla salon seçmeyi veya öğretmen masasına öğrenci yerleştirme gibi seçenekleri deneyiniz.
Tekrar denemek ister misiniz?"""
            retrieve = QMessageBox.question(QWidget(), "Yetersiz yer", message, QMessageBox.Yes | QMessageBox.No)
            if retrieve == QMessageBox.Yes:
                self.deploy_step()
            else:
                return
            logger.info("Yetersiz yer.")
        else:
            # Create files
            classroomPaths = classrooms_html.create(self.examInfos, sonuc, self.exam.exams)
            gradePaths = grades_html.create(self.examInfos, sonuc, self.exam.exams)
            logger.error(classroomPaths)
            logger.error(gradePaths)
            
            self.show_result_frame(classroomPaths, gradePaths)
            # -> TODO CHECK THIS IS NOT WORKING
            self.sinavFrame.reset()
            
    def show_result_frame(self, classroomPaths: dict, gradePaths: dict):
        # Dialog sonucuna göre dosyayı ya kayıtlara taşı ya da sil
        examName = "_".join([self.examInfos[-1], self.examInfos[3], self.examInfos[4]])
        
        dialogSonuc = SonucDialog(classroomPaths, gradePaths).isAccepted
        try:
            if dialogSonuc:
                os.mkdir(os.path.join(BASE_DIR, 'Saved', examName))
                os.mkdir(os.path.join(BASE_DIR, 'Saved', examName, "Classrooms"))
                os.mkdir(os.path.join(BASE_DIR, 'Saved', examName, "Grades"))
                name_template = "{}.html"
                for cName in classroomPaths:
                    cNameToPath = "".join(cName.split("/"))
                    cPath = classroomPaths[cName]
                    Path(cPath).rename(os.path.join(BASE_DIR, 'Saved', examName, "Classrooms", name_template.format(cNameToPath)))
                
                for gName in gradePaths:
                    gNameToPath= "".join(gName.split("/"))
                    gPath = gradePaths[gName]
                    Path(gPath).rename(os.path.join(BASE_DIR, 'Saved', examName, "Grades", name_template.format(gNameToPath)))

            shutil.rmtree(os.path.join(BASE_DIR, "Temp", examName))
            
        except Exception as e:
            raise e
            logger.error(str(e))
    
class Exam():
    def __init__(self, exams: dict, classroomNames: list, rules: list):
        self.exams = exams
        self.classroomNames = classroomNames
        self.rules = rules

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
        string = f"Sınavlar: {self.exams}\n\n{self.classrooms}\n\n\Kurallar: {self.rules}"
        return string

        
class SonucDialog(QDialog):
    def __init__(self, classroomPaths, gradePaths):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "sonuc_dialog.ui"), self)
        
        self.classroomPaths = classroomPaths
        self.gradePaths = gradePaths
        self.isAccepted = False

        self.wev = QWebEngineView()
        self.previewLayout.addWidget(self.wev)

        self.classroomItems = list()
        self.gradeItems = list()
        
        self.set_cl()
        self.set_gl()
        self.set_signals()
        self.exec_()
    
    def set_signals(self):
        self.classroomList.itemClicked.connect(self.cl_item_clicked)
        self.gradeList.itemClicked.connect(self.gl_item_clicked)
        self.saveBtn.clicked.connect(lambda: self.close(key = True))
        self.discardBtn.clicked.connect(self.close)
        
    def cl_item_clicked(self, item: QListWidgetItem):
        print(item.text())
        file_path = self.classroomPaths[item.text()]
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        self.wev.setHtml(html_content)
        
    def gl_item_clicked(self, item: QListWidgetItem):
        print(item.text())
        file_path = self.gradePaths[item.text()]
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        self.wev.setHtml(html_content)
        
    def close(self, key = False):
        if key:
            self.isAccepted = True
            self.accept()
            return
        self.isAccepted = False
        self.accept()
        
    def set_cl(self):
        for classroomName in self.classroomPaths:
            item = QListWidgetItem(classroomName)
            self.classroomItems.append(item)
            self.classroomList.addItem(item)
        
        logger.info(list(self.classroomPaths.items()))
        logger.info(self.classroomItems)
        try:
            first_classroom_item = self.classroomItems[0]
            first_classroom_item.setSelected(True)

            file_path = self.classroomPaths[first_classroom_item.text()]
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            self.wev.setHtml(html_content)
        except Exception as e:
            logger.error(e)
    
    def set_gl(self):
        for gradeName in self.gradePaths:
            item = QListWidgetItem(gradeName)
            self.gradeItems.append(item)
            self.gradeList.addItem(item)
            
  
class HighlightDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        # Call the base class paint method to draw the item
        super().paint(painter, option, index)

        # Check if the item is selected
        if option.state & QStyle.State_Selected:
            # Get the selected border color
            borderColor = QColor(255, 255, 255)  # Black color
            # Set the selected border color and style
            pen = QPen(borderColor, 2)  # 2-pixel border width
            pen.setJoinStyle(Qt.MiterJoin)  # Set the border join style
            painter.setPen(pen)
            # Draw the border inside the item rectangle
            painter.drawRect(option.rect.adjusted(1, 1, -1, -1))
        
  
if __name__ == '__main__':
    class ExamFrame(QFrame):
        def __init__(self):
            super().__init__()
            loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_frame_demo.ui"), self)
            self.examStruct = ExamStruct(self.examTable, self.gradeList, self.classroomList, self.examNameIn, self.addButton, self.removeButton, self.removeAllButton, self.createButton, self.sidebyside_sitting, self.backtoback_sitting, self.crossbycross_sitting, self.kizErkek, self.ogretmenMasasi, self)
            self.show()
        
    app = QApplication(sys.argv)
    frame = ExamFrame()
    app.exec_()