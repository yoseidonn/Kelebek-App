from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi

from App.HtmlCreater import classrooms_html, grades_html
from App import database
from App.colors import COLOR_PALETTE
from App.logs import logger
from App import deploy

from pathlib import Path
import os, sys, datetime, shutil, copy


COLORS = list(COLOR_PALETTE.values())
BASE_DIR = os.getenv("BASE_DIR")


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

        self.load_database_variables()
        
        # RENDER THE FRAME
        self.set_ui()
        self.set_signals()
        
        self.set_start_variables()
        self.adjust_widget_settings()

    def load_database_variables(self):
        self.grades = database.get_all_students(withGrades=True)
        self.classroom_names = database.get_all_classrooms(onlyNames=True)
        self.grade_names = list(self.grades.keys())

    def set_start_variables(self):
        self.classroomNamesBackup = set()
        self.classroomNames = set()         # To hold the selected classroom names
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
        self.select_all_classrooms_checkbox.stateChanged.connect(self.select_all_classrooms)
        
    def check_conditions(self):
        flag = False
        sinavAdi = self.informationFrame.sinavAdi.text()

        # Sınav adı girilmemiş ise uyarı mesajını göster
        if not sinavAdi:
            self.informationFrame.sinavAdiLabel.setVisible(True)
            self.informationFrame.sinavAdiLabel.setText("Lütfen bir sınav adı giriniz!")
            flag = True            

        # Sınav yoksa uyarı mesajını göster
        if not self.exams:
            self.examNameInLabel.setVisible(True)
            self.examNameInLabel.setText("Lütfen en az bir sınav ekleyin!")
            flag = True            

        # Sınav var ise:
        else:
            checked_grade_names = set([(checkbox if checkbox.isChecked() else None) for checkbox in self.grade_checkboxes])
            #print(checked_grade_names)

            # Henüz okula sınıf tanımlanmamış ise küme tamamen boş olurdu, o yüzden kontrol edip çıkartıyoruz
            if None in checked_grade_names:
                checked_grade_names.remove(None)
            # Hiç kayıtlı değilse de özel uyarı mesajı göster
            elif not checked_grade_names:
                self.gradeNamesLabel.setVisible(True)
                self.gradeNamesLabel.setText("Lütfen 'Öğrenciler' sekmesinden öğrenci kaydedin!")
                flag = True
            
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
            
            self.exams.update({examName: {"Grade-Names": [],
                                          "Checkboxes": [],
                                          "Palette-Color": color
                                          }})

            self.examNameIn.clear()
            self.draw_exam_table()

            self.removeButton.setEnabled(True)
            self.removeAllButton.setEnabled(True)

        else:
            self.set_red()       # Input place

    def remove_exam(self):
        checkboxes = self.exams[self.selectedExamName]["Checkboxes"]
        for checkbox in checkboxes:
            checkbox.blockSignals(True)
            checkbox.setStyleSheet("")
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
            #item = self.grade_checkboxes[checkbox]
            #index = self.gradeListWidget.row(item)
            
        self.exams.pop(self.selectedExamName)
        self.selectedExamName = None
        self.draw_exam_table()
        self.draw_grade_table()

    def remove_all_exams(self):
        self.adjust_widget_settings(reset=True)

    def on_cell_change(self):
        item = self.examTableWidget.currentItem()
        if item is None:
            self.selectedExamName = None
            return
        
        rowIndex = item.row()

        self.examTableWidget.selectRow(rowIndex)

        # Seçili sınavın rengini palet rengine ata
        keys = list(self.exams.keys())
        if not keys:
            return
        
        examName = keys[rowIndex]
        self.selectedExamName = examName                        # draw_exam_table da kullanılıyor
        examColor = self.exams[examName]["Palette-Color"]
        highLightColor = QColor(*examColor, 100)

        self.colorPalette.setColor(QPalette.Highlight, highLightColor)    
        self.examTableWidget.setPalette(self.colorPalette)
            
        self.draw_grade_table()
        
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
        if gradeName in self.exams[self.selectedExamName]["Grade-Names"]:
            self.exams[self.selectedExamName]["Checkboxes"].remove(checkbox)
            self.exams[self.selectedExamName]["Grade-Names"].remove(gradeName)
            self.examTableWidget.item(examIndex, 1).setText(f"{current - toAdd}")
            # RENGI SIFIRLA
            checkbox.setStyleSheet("")
            
        #Değeri arttır ve itemi ekle
        else:
            self.exams[self.selectedExamName]["Checkboxes"].append(checkbox)
            self.exams[self.selectedExamName]["Grade-Names"].append(gradeName)
            self.examTableWidget.item(examIndex, 1).setText(f"{current + toAdd}")
            #RENK EKLE
            color = self.exams[self.selectedExamName]["Palette-Color"]
            r, g, b = color
            checkbox.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 100)")

    def classroom_checkbox_clicked(self, checkbox: QCheckBox):
        self.classroomNamesLabel.setVisible(False)
        self.classroomNames.add(checkbox.text())
        self.classroomListWidget.setStyleSheet("")
        
    def select_all_classrooms(self):
        self.classroomNamesLabel.setVisible(False)
        self.classroomListWidget.blockSignals(True)
        
        state = self.select_all_classrooms_checkbox.isChecked()
        if state:
            # Eski secili olanlari yedekle ve tum salon adlarini listeye ekle
            self.classroomNamesBackup = self.classroomNames.copy()
            self.classroomNames = self.classroom_names.copy()
            for checkbox in self.classroom_checkboxes:
                checkbox.blockSignals(True)
                
                checkbox.setEnabled(False)
                checkbox.setChecked(True)
                
                checkbox.blockSignals(False)
        else:
            # Yedegi geri getir
            self.classroomNames = self.classroomNamesBackup.copy()
            for checkbox in self.classroom_checkboxes:
                checkbox.blockSignals(True)
                
                checkbox.setEnabled(True)
                if checkbox.text() not in self.classroomNames:
                    checkbox.setChecked(False)

                checkbox.blockSignals(False)
            self.classroomNamesBackup = set()
            
        self.classroomListWidget.blockSignals(False)

    def draw_exam_table(self):
        self.examTableWidget.setRowCount(len(self.exams))
        for rowIndex, examName in enumerate(self.exams.keys()):
            # Get the count of all the students which are in the gradeNames list in the spesific exam
            studentCount = 0
            for gradeName in self.exams[examName]["Grade-Names"]:
                studentCount += len(self.grades[gradeName])

            item1 = QTableWidgetItem(examName)
            item2 = QTableWidgetItem(str(studentCount))
            self.examTableWidget.setItem(rowIndex, 0, item1)
            self.examTableWidget.setItem(rowIndex, 1, item2)
            
            color = self.exams[examName]["Palette-Color"]
            r, g, b = color
            self.examTableWidget.item(rowIndex, 0).setBackground(QColor(r, g, b))
            self.examTableWidget.item(rowIndex, 1).setBackground(QColor(r, g, b))
            
        # Eğer silme ile çağrılmış ise ve geride sınav kalmamışsa None seç
        if len(self.exams.keys()):
            lastRowIndex = len(self.exams) - 1
            self.examTableWidget.selectRow(lastRowIndex)
            #print("Lastrow index", lastRowIndex)
            self.selectedExamName = list(self.exams.keys())[lastRowIndex]

        else:
            self.selectedExamName = None
    
    def draw_grade_table(self):
        print("drawed grades")
        for checkbox in self.grade_checkboxes:
            checkbox.setEnabled(True if len(self.exams) else False)
            checkbox.setStyleSheet("")

        for exam_name, exam in self.exams.items():
            #RENK EKLE
            color = exam["Palette-Color"]
            r, g, b = color

            checkboxes = exam["Checkboxes"]
            for checkbox in checkboxes:
                if exam_name != self.selectedExamName:
                    checkbox.setEnabled(False)
                checkbox.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, 100)")

    def set_grade_table(self):
        print("grades set")
        for grade_name in self.grade_names:
            item = QListWidgetItem()
            checkbox = QCheckBox(grade_name, self)
            checkbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.grade_checkbox_clicked(c))
            self.gradeListWidget.addItem(item)
            self.gradeListWidget.setItemWidget(item, checkbox)

            self.grade_checkboxes.update({checkbox: item})

    def set_classroom_table(self):
        print("classrooms set")
        for classroom_name in self.classroom_names:
            item = QListWidgetItem()
            checkbox = QCheckBox(classroom_name, self)
            checkbox.stateChanged.connect(lambda state, c=checkbox: self.classroom_checkbox_clicked(c))
            
            self.classroomListWidget.addItem(item)
            self.classroomListWidget.setItemWidget(item, checkbox)
            self.classroom_checkboxes.update({checkbox: item})
    
    def adjust_widget_settings(self, reset = False):
        if reset:
            print("reset")
            self.exams = {}
            self.examTableWidget.clear()
            self.gradeListWidget.clear()
            self.classroomListWidget.clear()
            for checkbox, item in self.grade_checkboxes.items():
                checkbox.deleteLater()
                del item
            for checkbox, item in self.classroom_checkboxes.items():
                checkbox.deleteLater()
                del item

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

        self.grade_checkboxes = dict()
        self.classroom_checkboxes = dict()

        self.draw_exam_table()
        self.set_grade_table()
        self.draw_grade_table()
        self.set_classroom_table()
    
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
        self.exam = Exam(exams = self.exams, classroomNames = list(self.classroomNames), rules = rules)

        sonuc = deploy.distribute(self.exam)
        print(f"Status: {sonuc.get('Status')}")
        print(f"Class-Counts: {sonuc.get('Class-Counts')}")
        print(f"Placed-Count: {sonuc.get('Placed-Count')}")
        print(f"Unplaced-Count: {sonuc.get('Un-Placed-Count')}")
        if sonuc.get("Status"):
            # Create files
            exam_infos = {
                # egitimOgretimYili, donem, kacinciYazili, tarih, kacinciDers, salonAdi
                "Sinav-Adi": self.informationFrame.sinavAdi.text(),
                "Egitim-Ogretim-Yili": self.informationFrame.egitimOgretimYili.currentText(),
                "Kacinci-Donem": self.informationFrame.kacinciDonem.currentText(),
                "Donemin-Kacinci-Sinavi": self.informationFrame.doneminKacinciSinavi.currentText(),
                "Tarih": "-".join([str(i) for i in self.informationFrame.sinavTarihi.date().getDate()]),
                "Kacinci-Ders": self.informationFrame.kacinciDers.currentText(),
            }
            print(exam_infos)
            classroomPaths = classrooms_html.create(exam_infos, sonuc.get("Classrooms"), self.exam.exams)
            gradePaths = grades_html.create(exam_infos, sonuc.get("Classrooms"), self.exam.exams)
            
            self.show_result_frame(classroomPaths, gradePaths, exam_infos)

        else:
            # Tekrar deneyiniz penceresi
            retrieve = QMessageBox.question(QWidget(), "Yetersiz yer", "Tekrar denemek için Evet'e basın.", QMessageBox.Yes | QMessageBox.No)
            if retrieve == QMessageBox.Yes:
                self.deploying_step()
            else:
                logger.info(f"Status: {sonuc.get('Status')} | Placed: {sonuc.get('Place-Count')} | Unplaced: {sonuc.get('Unplaced-Count')}")    

    def show_result_frame(self, classroomPaths: dict, gradePaths: dict, exam_infos: dict):
        # Dialog sonucuna göre dosyayı ya kayıtlara taşı ya da sil
        dialogSonuc = SonucDialog(classroomPaths, gradePaths).isAccepted

        try:
            examName = "_".join([exam_infos.get('Sinav-Adi'), exam_infos.get('Tarih'), exam_infos.get('Kacinci-Ders').strip()])
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
            logger.error(f"{str(e)} | Sınav kaydedilirken bir sorun meydana geldi")
            
    
    
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
            grades = self.exams[examName]["Grade-Names"]
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
        
        #logger.info(list(self.classroomPaths.items()))
        #logger.info(self.classroomItems)
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