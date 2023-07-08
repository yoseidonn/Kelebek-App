from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from dotenv import load_dotenv

from App import database
from App.logs import logger

import os, functools


load_dotenv()
BASE_DIR = os.getenv("BASE_DIR")
SOL = "Solda"
SAG = "Sağda"
TEK = "1'li"
CIFT = "2'li"


class ClassroomsFrame(QFrame):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(BASE_DIR, "Forms", "salonlar_frame.ui"), self)
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
        
        
class ClassroomStruct:
    def __init__(self, grid: QGridLayout, leftFrame: QFrame, rightFrame: QFrame, dualCombo: QComboBox, directionCombo: QComboBox, buttons = []):
        self.grid = grid
        self.teacherLeftFrame = leftFrame
        self.teacherRightFrame = rightFrame
        self.dualCombo = dualCombo
        self.directionCombo = directionCombo
        self.addColumnButton, self.removeColumnButton, self.addRowButton, self.removeRowButton = buttons

        self.columns = []
        self.lastColumnIndex = 0

        self.change_yon()
        self.set_signals_and_ui()
        self.set_3x5()

        self.grid.setSpacing(15)
        
    def set_signals_and_ui(self):
        #SIGNALS
        self.directionCombo.currentIndexChanged.connect(lambda: self.change_yon(direction=self.directionCombo.currentText()))
        self.dualCombo.currentIndexChanged.connect(lambda: self.change_kacli(mode=self.dualCombo.currentText()))
        
        self.addColumnButton.clicked.connect(self.add_column)
        self.removeColumnButton.clicked.connect(self.remove_column)
        self.addRowButton.clicked.connect(self.add_row)
        self.removeRowButton.clicked.connect(self.remove_row)

        #UI
        self.directionCombo.setCurrentIndex(0)
        self.dualCombo.setCurrentIndex(1)
        
    def add_column(self):
        maxRowCount = max([column.deskCount for column in self.columns])
        for column in self.columns:
            if column.deskCount < maxRowCount:
                for i in range(maxRowCount - column.deskCount):
                    column.add_desk()

        newColumn = Column(self, self.grid, self.dualCombo, self.lastColumnIndex)
        newColumn.add_desk(multiple=maxRowCount)
        self.columns.append(newColumn)
        self.lastColumnIndex += 1

        #print(self.columns)

    def remove_column(self):
        if len(self.columns) > 1:
            self.columns[-1].clear()
            self.columns.pop(-1)
            self.lastColumnIndex -=1

        #print(self.columns)

    def add_row(self):
        for column in self.columns:
            column.add_desk()

    def remove_row(self):
        if all([ (column.deskCount > 1) for column in self.columns] ):
            #print([ (column.deskCount > 1) for column in self.columns])
            for column in self.columns:
                column.remove_desk()

    def _reset(self):
        for column in self.columns:
            column.clear()
        self.columns.clear()
        self.lastColumnIndex = 0

        self.directionCombo.setCurrentIndex(0)
        self.dualCombo.setCurrentIndex(1)

    def change_yon(self, direction="Solda", reset = False):
        #print("'Yon' değiştirildi.")
        if reset:
            self.teacherLeftFrame.setVisible(True)
            self.teacherRightFrame.setVisible(False)
            return

        if direction == SOL:
            #print("Sol")
            self.teacherLeftFrame.setVisible(True)
            self.teacherRightFrame.setVisible(False)
        elif direction == SAG:
            #print("Sağ")
            self.teacherLeftFrame.setVisible(False)
            self.teacherRightFrame.setVisible(True)

    def change_kacli(self, mode):
        #print("'Kaçlı' değiştirildi.")
        for column in self.columns:
            for desk in column.desks:
                if mode == TEK:
                    #print(TEK)
                    desk.set_single()
                elif mode == CIFT:
                    #print(CIFT)
                    desk.set_double()

    def set_3x5(self):
        for i in range(3):
            self.columns.append(newColumn:=Column(self, self.grid, self.dualCombo, self.lastColumnIndex))
            self.lastColumnIndex += 1
            newColumn.add_desk(multiple=5)

    def set_layout(self, layout):
        self._reset()
        rowCounts = layout.split(",")
        for _ in range(len(rowCounts)):
            newColumn = Column(self, self.grid, self.dualCombo, self.lastColumnIndex, mode = 2)
            self.lastColumnIndex += 1
            self.columns.append(newColumn)
            
        for columnInx, count in enumerate(rowCounts):
            [self.columns[columnInx].add_desk() for _ in range(int(count))]


class Column:
    def __init__(self, Structer: ClassroomStruct, grid: QGridLayout, dualCombo: QComboBox, columnIndex: int, mode = 2):
        self.grid = grid
        self.dualCombo = dualCombo
        self.columnIndex = columnIndex
        self.Structer = Structer

        self.desks = []
        self.deskCount = 0
        self.lastRowIndex = 0

    def press_event(self, event: QMouseEvent, sourceObject):
        if event.button() == 1 and sourceObject.rowIndex == (self.lastRowIndex - 1) and self.deskCount > 1:
            self.desks.remove(sourceObject)
            self.deskCount -= 1
            self.lastRowIndex -= 1
            self.grid.removeWidget(sourceObject)
            sourceObject.deleteLater()
            del sourceObject

        else:
            #print(event.button() == 1, sourceObject.rowIndex != (self.lastRowIndex - 1))
            #print(sourceObject.rowIndex, (self.lastRowIndex - 1))
            pass

    def add_desk(self, multiple = False):
        a = {"1'li": 1, "2'li": 2}
        mode = a[self.dualCombo.currentText()]#Tekli ikili
        if multiple:
            for i in range(multiple):
                newDesk = Desk(self, self.columnIndex, self.lastRowIndex, mode=mode)
                self.grid.addWidget(newDesk, self.deskCount, self.columnIndex)    
                
                self.desks.append(newDesk)
                self.deskCount += 1
                self.lastRowIndex += 1
        else:
            newDesk = Desk(self, self.columnIndex, self.lastRowIndex, mode=mode)
            self.grid.addWidget(newDesk, self.deskCount, self.columnIndex)    
            
            self.desks.append(newDesk)
            self.deskCount += 1
            self.lastRowIndex += 1
    
    def remove_desk(self):
        self.grid.removeWidget(self.desks[-1])
        self.desks[-1].deleteLater()
        del self.desks[-1]
        self.deskCount -= 1
        self.lastRowIndex -= 1

    def clear(self):
        for desk in self.desks:
            self.grid.removeWidget(desk)
            desk.setVisible(False)
            del desk
        self.desks = list()
        self.deskCount = 0
        self.lastRowIndex = 0


class Desk(QLabel):
    def __init__(self, column, columnIndex, rowIndex, mode = 2):
        super().__init__()
        self.column = column
        self.columnIndex = columnIndex
        self.rowIndex = rowIndex
        self.mode = mode

        self.mousePressEvent = functools.partial(self.column.press_event, sourceObject = self)

        self.setFixedSize(QSize(64,64))
        self.set_double() if self.mode == 2 else self.set_single()

    def press_event(self, event):
        if event.button() == 1:
            if self.column.desks.index(self) == len(self.column.desks) -1:
                print()

                self.column.grid.removeWidget(self)
                self.column.desks.remove(self)
                self.column.deskCount -= 1
                self.deleteLater()
                print()

    def set_double(self):
        self.setStyleSheet(f'border-image: url({os.path.join(BASE_DIR, "Images", "img", "double_student_desk.png")})')

    def set_single(self):
        self.setStyleSheet(f'border-image: url({os.path.join(BASE_DIR, "Images", "img", "single_student_desk.png")})')
