from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from App.HtmlCreater import classrooms_html, grades_html
from App import database
from App.colors import COLOR_PALETTE
from App.logs import logger
from App import deploy

from dotenv import load_dotenv
from pathlib import Path
import os, sys, datetime, shutil


COLORS = list(COLOR_PALETTE.values())
BASE_DIR = os.getenv("BASE_DIR")
load_dotenv()



class CreateExamBaseFrame(QFrame):
    MONTHS = {"Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12}
        
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_base_frame.ui"), self)
        
        self.informationFrame = InformationFrame()
        self.examFrame = ExamFrame(informationFrame = self.informationFrame)

        self.set_ui()
    
    def set_ui(self):
        self.informationLayout.addWidget(self.informationFrame)
        self.examLayout.addWidget(self.examFrame)
    
    def set_signals(self):
        pass

class InformationFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_bilgileri_frame.ui"), self)

        self.set_ui()   
        self.set_signals()

    def set_ui(self):
        pass
    
    def set_signals(self):
        self.sinavAdi.textChanged.connect(self.validate_text)
    
    def validate_text(self, new_text):
        warning_message = "İstenmeyen karakter(ler): {}"
        un_wanted_chars = [*"!'^+%&/=?_\"()[]<>{}., "]
        un_wanted_chars2 = []
        if any([char in new_text for char in un_wanted_chars]):
            modified_text = new_text
            for char in un_wanted_chars:
                if char in new_text:
                    modified_text = modified_text.replace(char, "")
                    if char == " ":
                        char = "BOSLUK"
                    un_wanted_chars2.append(char)

            self.sinavAdi.setText(modified_text)
            self.sinavAdiLabel.setText(warning_message.format(", ".join(un_wanted_chars2)))
            self.sinavAdiLabel.setVisible(True)

        else:
            self.sinavAdiLabel.setVisible(False)
            

        
class ExamFrame(QFrame):
    def __init__(self, informationFrame: InformationFrame):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "yeni_sinav_sinavlar_frame.ui"), self)

        self.informationFrame = informationFrame

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

        self.examNameInLabel.setVisible(False)
        self.gradeNamesLabel.setVisible(False)
        self.classroomNamesLabel.setVisible(False)

    def set_signals(self):
        self.addButton.clicked.connect(self.add_exam)
        self.removeButton.clicked.connect(self.remove_exam)
        self.removeAllButton.clicked.connect(self.remove_all_exams)
        self.examNameIn.textChanged.connect(self.set_white)

        self.examTableWidget.itemSelectionChanged.connect(self.on_cell_change)

        self.createButton.clicked.connect(self.check_conditions)
        
    def check_conditions(self):
        flag = False
        sinavAdi = self.informationFrame.sinavAdi.text()
        if not sinavAdi:
            self.informationFrame.sinavAdiLabel.setVisible(True)
            self.informationFrame.sinavAdiLabel.setText("Lütfen bir sınav adı giriniz!")
            flag = True            

        if not self.exams:
            self.examNameInLabel.setVisible(True)
            self.examNameInLabel.setText("Lütfen en az bir sınav ekleyin!")
            flag = True            

        else:
            checked_grade_names = set([(checkbox if checkbox.isChecked() else None) for checkbox in self.gradeCheckBoxes])
            if checked_grade_names:
                checked_grade_names.remove(None)

            if len(checked_grade_names) < len(self.exams.keys()):
                self.gradeNamesLabel.setVisible(True)
                self.gradeNamesLabel.setText("Lütfen her sınava en az bir sınıf ekleyiniz!")
                flag = True            

        if not len(self.classroomNames):
            self.classroomNamesLabel.setVisible(True)
            self.classroomNamesLabel.setText("Lütfen en az bir salon seçiniz!")
            flag = True            

        if flag:
            return
        
        self.deploying_step()

        
    def add_exam(self):
        examName = self.examNameIn.text().strip().upper()
        if len(examName) and (examName not in self.exams.keys()):
            examIndex = len(self.exams)
            color = COLORS[examIndex]
            
            self.exams.update({examName: {"gradeNames": [],
                                          "checkBoxes": [],
                                          "paletteColor": color
                                          }})

            self.examNameIn.clear()
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
        self.gradeNamesLabel.setVisible(False)
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
        self.classroomNamesLabel.setVisible(False)
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
            checkbox = QCheckBox(gradeName, self)
            checkbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.grade_checkbox_clicked(c))
            
            self.gradeListWidget.addItem(item)
            self.gradeListWidget.setItemWidget(item, checkbox)

            self.gradeCheckBoxes.append(checkbox)

    def draw_classroom_table(self):
        for classroomName in self.classroomsNames:
            item = QListWidgetItem()
            checkbox = QCheckBox(classroomName, self)
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
        self.examNameInLabel.setVisible(False)
    
    def set_red(self):
        self.examNameInLabel.setText("Sınav adı boş olamaz!")
        self.examNameInLabel.setVisible(True)
    
    def deploying_step(self):
        rules = {"SideBySideSitting": self.sidebyside_sitting,
                 "BackToBackSitting": self.backtoback_sitting,
                 "CrossByCrossSitting": self.crossbycross_sitting,
                 "KizErkekYanYanaOturabilir": self.kizErkek.isChecked(),
                 "OgretmenMasasinaOgrenciOturabilir": self.ogretmenMasasi.isChecked()
                }
        self.exam = Exam(exams = self.exams, classroomNames = self.classroomNames, rules = rules)

        sonuc = deploy.distribute(self.exam)
        if not sonuc:
            # Tekrar deneyiniz penceresi ekle
            message = sonuc
            retrieve = QMessageBox.question(QWidget(), "Yetersiz yer", message, QMessageBox.Yes | QMessageBox.No)
            if retrieve == QMessageBox.Yes:
                self.deploy_step()
            else:
                return
            logger.info(message)

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
        dialogSonuc = SonucDialog(classroomPaths, gradePaths).isAccepted

        try:
            examName = "_".join([self.examInfos[-1], self.examInfos[3], self.examInfos[4]])
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
    def __init__(self, exams: dict, classroomNames: list, rules: dict):
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
    pass