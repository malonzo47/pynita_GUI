# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layouts/ui_code_popuptable.ui',
# licensing of 'layouts/ui_code_popuptable.ui' applies.
#
# Created: Mon Jan  7 15:09:15 2019
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

"""
Created on Fri Nov 16 16:31:28 2018

@author: Praveen Noojipady
@email: noojipad@american.edu
@Project: pyNITA-GUI
License:  
Copyright (c)
"""
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(324, 386)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 325))
        self.tabWidget.setMaximumSize(QtCore.QSize(300, 320))
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab2)
        self.gridLayout.setObjectName("gridLayout")
        self.popup_table = QtWidgets.QTableWidget(self.tab2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.popup_table.sizePolicy().hasHeightForWidth())
        self.popup_table.setSizePolicy(sizePolicy)
        self.popup_table.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.popup_table.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.popup_table.setLineWidth(17)
        self.popup_table.setObjectName("popup_table")
        self.popup_table.setColumnCount(1)
        self.popup_table.setRowCount(8)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setVerticalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.popup_table.setHorizontalHeaderItem(0, item)
        self.popup_table.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.popup_table, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab2, "")
        self.gridLayout_8.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 324, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.popup_table.verticalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "bail_thresh", None, -1))
        self.popup_table.verticalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "noise_thresh", None, -1))
        self.popup_table.verticalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "penalty", None, -1))
        self.popup_table.verticalHeaderItem(3).setText(QtWidgets.QApplication.translate("MainWindow", "filter_dist", None, -1))
        self.popup_table.verticalHeaderItem(4).setText(QtWidgets.QApplication.translate("MainWindow", "pct", None, -1))
        self.popup_table.verticalHeaderItem(5).setText(QtWidgets.QApplication.translate("MainWindow", "max_complex", None, -1))
        self.popup_table.verticalHeaderItem(6).setText(QtWidgets.QApplication.translate("MainWindow", "min_complex", None, -1))
        self.popup_table.verticalHeaderItem(7).setText(QtWidgets.QApplication.translate("MainWindow", "filter_opt", None, -1))
        self.popup_table.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "Optimized Parameters", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab2), QtWidgets.QApplication.translate("MainWindow", "Optimized Parameters", None, -1))

