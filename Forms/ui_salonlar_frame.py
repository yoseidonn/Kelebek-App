# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/yusuf/Belgeler/Projects/Software/Kelebek/Kelebek BETA/Forms/salonlar_frame.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(889, 717)
        Frame.setStyleSheet("QFrame {\n"
"border: none\n"
"}\n"
"")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Frame)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(Frame)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.classroomList = QtWidgets.QListWidget(self.groupBox_2)
        self.classroomList.setObjectName("classroomList")
        self.horizontalLayout_4.addWidget(self.classroomList)
        self.horizontalLayout.addWidget(self.groupBox_2, 0, QtCore.Qt.AlignLeft)
        self.rightBody = QtWidgets.QFrame(Frame)
        self.rightBody.setStyleSheet("")
        self.rightBody.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightBody.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rightBody.setObjectName("rightBody")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.rightBody)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.rightBody)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.buttonsFrame = QtWidgets.QFrame(self.frame)
        self.buttonsFrame.setStyleSheet("")
        self.buttonsFrame.setObjectName("buttonsFrame")
        self.buttonLayout_2 = QtWidgets.QVBoxLayout(self.buttonsFrame)
        self.buttonLayout_2.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout_2.setSpacing(10)
        self.buttonLayout_2.setObjectName("buttonLayout_2")
        self.columnFrame = QtWidgets.QFrame(self.buttonsFrame)
        self.columnFrame.setStyleSheet("")
        self.columnFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.columnFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.columnFrame.setObjectName("columnFrame")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.columnFrame)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.sutunText = QtWidgets.QLabel(self.columnFrame)
        self.sutunText.setObjectName("sutunText")
        self.verticalLayout_12.addWidget(self.sutunText)
        self.frame_5 = QtWidgets.QFrame(self.columnFrame)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.addColumn = QtWidgets.QPushButton(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addColumn.sizePolicy().hasHeightForWidth())
        self.addColumn.setSizePolicy(sizePolicy)
        self.addColumn.setText("")
        self.addColumn.setObjectName("addColumn")
        self.horizontalLayout_12.addWidget(self.addColumn)
        self.removeColumn = QtWidgets.QPushButton(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeColumn.sizePolicy().hasHeightForWidth())
        self.removeColumn.setSizePolicy(sizePolicy)
        self.removeColumn.setText("")
        self.removeColumn.setObjectName("removeColumn")
        self.horizontalLayout_12.addWidget(self.removeColumn)
        self.verticalLayout_12.addWidget(self.frame_5, 0, QtCore.Qt.AlignLeft)
        self.buttonLayout_2.addWidget(self.columnFrame)
        self.rowFrame = QtWidgets.QFrame(self.buttonsFrame)
        self.rowFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rowFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.rowFrame.setObjectName("rowFrame")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.rowFrame)
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label = QtWidgets.QLabel(self.rowFrame)
        self.label.setObjectName("label")
        self.verticalLayout_13.addWidget(self.label)
        self.frame_7 = QtWidgets.QFrame(self.rowFrame)
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.frame_7)
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.addRow = QtWidgets.QPushButton(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addRow.sizePolicy().hasHeightForWidth())
        self.addRow.setSizePolicy(sizePolicy)
        self.addRow.setText("")
        self.addRow.setObjectName("addRow")
        self.horizontalLayout_13.addWidget(self.addRow)
        self.removeRow = QtWidgets.QPushButton(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeRow.sizePolicy().hasHeightForWidth())
        self.removeRow.setSizePolicy(sizePolicy)
        self.removeRow.setText("")
        self.removeRow.setObjectName("removeRow")
        self.horizontalLayout_13.addWidget(self.removeRow)
        self.verticalLayout_13.addWidget(self.frame_7, 0, QtCore.Qt.AlignLeft)
        self.buttonLayout_2.addWidget(self.rowFrame)
        self.frame_9 = QtWidgets.QFrame(self.buttonsFrame)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_14.setSpacing(5)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_3 = QtWidgets.QLabel(self.frame_9)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_14.addWidget(self.label_3, 0, QtCore.Qt.AlignLeft)
        self.label_5 = QtWidgets.QLabel(self.frame_9)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_14.addWidget(self.label_5)
        self.yonCombo = QtWidgets.QComboBox(self.frame_9)
        self.yonCombo.setObjectName("yonCombo")
        self.yonCombo.addItem("")
        self.yonCombo.addItem("")
        self.verticalLayout_14.addWidget(self.yonCombo, 0, QtCore.Qt.AlignLeft)
        self.buttonLayout_2.addWidget(self.frame_9)
        self.frame_10 = QtWidgets.QFrame(self.buttonsFrame)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.frame_10)
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_15.setSpacing(5)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_4 = QtWidgets.QLabel(self.frame_10)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_15.addWidget(self.label_4, 0, QtCore.Qt.AlignLeft)
        self.kacliCombo = QtWidgets.QComboBox(self.frame_10)
        self.kacliCombo.setObjectName("kacliCombo")
        self.kacliCombo.addItem("")
        self.kacliCombo.addItem("")
        self.verticalLayout_15.addWidget(self.kacliCombo, 0, QtCore.Qt.AlignLeft)
        self.buttonLayout_2.addWidget(self.frame_10)
        self.horizontalLayout_5.addWidget(self.buttonsFrame, 0, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.salonShape = QtWidgets.QGroupBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.salonShape.sizePolicy().hasHeightForWidth())
        self.salonShape.setSizePolicy(sizePolicy)
        self.salonShape.setTitle("")
        self.salonShape.setObjectName("salonShape")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.salonShape)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.salonNameIn = QtWidgets.QLineEdit(self.salonShape)
        self.salonNameIn.setText("")
        self.salonNameIn.setObjectName("salonNameIn")
        self.verticalLayout_10.addWidget(self.salonNameIn)
        self.ogretmenSagFrame = QtWidgets.QFrame(self.salonShape)
        self.ogretmenSagFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ogretmenSagFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ogretmenSagFrame.setObjectName("ogretmenSagFrame")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.ogretmenSagFrame)
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.sagGrid = QtWidgets.QGridLayout()
        self.sagGrid.setObjectName("sagGrid")
        self.sagGraphic = QtWidgets.QGraphicsView(self.ogretmenSagFrame)
        self.sagGraphic.setMinimumSize(QtCore.QSize(80, 80))
        self.sagGraphic.setMaximumSize(QtCore.QSize(80, 80))
        self.sagGraphic.setStyleSheet("")
        self.sagGraphic.setObjectName("sagGraphic")
        self.sagGrid.addWidget(self.sagGraphic, 0, 4, 1, 1, QtCore.Qt.AlignRight)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.sagGrid.addItem(spacerItem, 0, 3, 1, 1)
        self.verticalLayout_11.addLayout(self.sagGrid)
        self.verticalLayout_10.addWidget(self.ogretmenSagFrame, 0, QtCore.Qt.AlignTop)
        self.ogretmenSolFrame = QtWidgets.QFrame(self.salonShape)
        self.ogretmenSolFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ogretmenSolFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ogretmenSolFrame.setObjectName("ogretmenSolFrame")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.ogretmenSolFrame)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.solGrid = QtWidgets.QGridLayout()
        self.solGrid.setObjectName("solGrid")
        self.solGraphic = QtWidgets.QGraphicsView(self.ogretmenSolFrame)
        self.solGraphic.setMinimumSize(QtCore.QSize(80, 80))
        self.solGraphic.setMaximumSize(QtCore.QSize(80, 80))
        self.solGraphic.setStyleSheet("")
        self.solGraphic.setObjectName("solGraphic")
        self.solGrid.addWidget(self.solGraphic, 0, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.solGrid.addItem(spacerItem1, 0, 1, 1, 1)
        self.horizontalLayout_9.addLayout(self.solGrid)
        self.verticalLayout_10.addWidget(self.ogretmenSolFrame, 0, QtCore.Qt.AlignTop)
        self.masalar = QtWidgets.QFrame(self.salonShape)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.masalar.sizePolicy().hasHeightForWidth())
        self.masalar.setSizePolicy(sizePolicy)
        self.masalar.setMaximumSize(QtCore.QSize(16777215, 16000))
        self.masalar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.masalar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.masalar.setObjectName("masalar")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.masalar)
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.frame_11 = QtWidgets.QFrame(self.masalar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy)
        self.frame_11.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.frame_11)
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.grid = QtWidgets.QGridLayout()
        self.grid.setContentsMargins(-1, -1, -1, 0)
        self.grid.setObjectName("grid")
        self.horizontalLayout_14.addLayout(self.grid)
        self.horizontalLayout_11.addWidget(self.frame_11)
        self.verticalLayout_10.addWidget(self.masalar)
        self.horizontalLayout_5.addWidget(self.salonShape)
        self.verticalLayout.addWidget(self.frame, 0, QtCore.Qt.AlignLeft)
        self.frame_2 = QtWidgets.QFrame(self.rightBody)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.addButton = QtWidgets.QPushButton(self.frame_2)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout_2.addWidget(self.addButton)
        self.saveButton = QtWidgets.QPushButton(self.frame_2)
        self.saveButton.setStyleSheet("background-color: rgb(87, 227, 137);")
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_2.addWidget(self.saveButton)
        self.removeButton = QtWidgets.QPushButton(self.frame_2)
        self.removeButton.setStyleSheet("background-color: rgb(246, 97, 81);")
        self.removeButton.setObjectName("removeButton")
        self.horizontalLayout_2.addWidget(self.removeButton)
        self.cancelButton = QtWidgets.QPushButton(self.frame_2)
        self.cancelButton.setStyleSheet("background-color: rgb(119, 118, 123);")
        self.cancelButton.setText("")
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_2.addWidget(self.cancelButton, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.frame_2)
        self.istatistiklerFrame = QtWidgets.QFrame(self.rightBody)
        self.istatistiklerFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.istatistiklerFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.istatistiklerFrame.setObjectName("istatistiklerFrame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.istatistiklerFrame)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.groupBox_3 = QtWidgets.QGroupBox(self.istatistiklerFrame)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.istatistiklerWIdget = QtWidgets.QListWidget(self.groupBox_3)
        self.istatistiklerWIdget.setObjectName("istatistiklerWIdget")
        self.verticalLayout_9.addWidget(self.istatistiklerWIdget)
        self.horizontalLayout_3.addWidget(self.groupBox_3)
        self.verticalLayout.addWidget(self.istatistiklerFrame)
        self.horizontalLayout.addWidget(self.rightBody)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.groupBox_2.setTitle(_translate("Frame", "Salonlar"))
        self.sutunText.setText(_translate("Frame", "Sütun"))
        self.label.setText(_translate("Frame", "Satır"))
        self.label_3.setText(_translate("Frame", "Öğretmen"))
        self.label_5.setText(_translate("Frame", "Solda"))
        self.yonCombo.setItemText(0, _translate("Frame", "Solda"))
        self.yonCombo.setItemText(1, _translate("Frame", "Sağda"))
        self.label_4.setText(_translate("Frame", "Sıralar"))
        self.kacliCombo.setItemText(0, _translate("Frame", "1\'li"))
        self.kacliCombo.setItemText(1, _translate("Frame", "2\'li"))
        self.salonNameIn.setPlaceholderText(_translate("Frame", "Salon adı"))
        self.addButton.setText(_translate("Frame", "Yeni ekle"))
        self.saveButton.setText(_translate("Frame", "Kaydet"))
        self.removeButton.setText(_translate("Frame", "Sil"))
        self.groupBox_3.setTitle(_translate("Frame", "İstatistikler"))
import resources_rc
