
# CONSTANTS
SOL = "Solda"
SAG = "Sağda"
TEK = "1'li"
CIFT = "2'li"

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os, sys, functools

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
        self.setStyleSheet(f'border-image: url({os.path.join("Images", "img", "double_student_desk.png")})')

    def set_single(self):
        self.setStyleSheet(f'border-image: url({os.path.join("Images", "img", "single_student_desk.png")})')
