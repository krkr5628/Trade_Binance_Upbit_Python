# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main_designer.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform, QTextBlockFormat)
from PySide6.QtWidgets import (QApplication, QGroupBox, QHeaderView, QLCDNumber,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTableView,
    QTextBrowser, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1729, 846)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 120, 1271, 281))
        self.groupBox_7 = QGroupBox(self.groupBox)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setGeometry(QRect(850, 10, 411, 261))
        font = QFont()
        font.setPointSize(8)
        self.groupBox_7.setFont(font)
        self.groupBox_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textBrowser = QTextBrowser(self.groupBox_7)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(10, 20, 391, 231))
        self.groupBox_8 = QGroupBox(self.groupBox)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.groupBox_8.setGeometry(QRect(10, 140, 831, 131))
        self.groupBox_8.setFont(font)
        self.groupBox_8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_2 = QTableView(self.groupBox_8)
        self.tableView_2.setObjectName(u"tableView_2")
        self.tableView_2.setGeometry(QRect(10, 20, 811, 101))
        self.groupBox_9 = QGroupBox(self.groupBox)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.groupBox_9.setGeometry(QRect(10, 10, 831, 131))
        self.groupBox_9.setFont(font)
        self.groupBox_9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView = QTableView(self.groupBox_9)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(10, 20, 811, 101))
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 510, 1271, 281))
        self.groupBox_4 = QGroupBox(self.groupBox_2)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(10, 10, 831, 131))
        self.groupBox_4.setFont(font)
        self.groupBox_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_3 = QTableView(self.groupBox_4)
        self.tableView_3.setObjectName(u"tableView_3")
        self.tableView_3.setGeometry(QRect(10, 20, 811, 101))
        self.groupBox_5 = QGroupBox(self.groupBox_2)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(10, 140, 831, 131))
        self.groupBox_5.setFont(font)
        self.groupBox_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_4 = QTableView(self.groupBox_5)
        self.tableView_4.setObjectName(u"tableView_4")
        self.tableView_4.setGeometry(QRect(10, 20, 811, 101))
        self.groupBox_6 = QGroupBox(self.groupBox_2)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(850, 10, 411, 261))
        self.groupBox_6.setFont(font)
        self.groupBox_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textBrowser_2 = QTextBrowser(self.groupBox_6)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        self.textBrowser_2.setGeometry(QRect(10, 20, 391, 231))
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(1290, 120, 421, 671))
        self.tableView_5 = QTableView(self.groupBox_3)
        self.tableView_5.setObjectName(u"tableView_5")
        self.tableView_5.setGeometry(QRect(10, 60, 401, 601))
        font1 = QFont()
        font1.setPointSize(7)
        self.tableView_5.setFont(font1)
        self.textBrowser_3 = QTextBrowser(self.groupBox_3)
        self.textBrowser_3.setObjectName(u"textBrowser_3")
        self.textBrowser_3.setGeometry(QRect(10, 20, 201, 41))
        font2 = QFont()
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setUnderline(True)
        self.textBrowser_3.setFont(font2)
        self.textBrowser_4 = QTextBrowser(self.groupBox_3)
        self.textBrowser_4.setObjectName(u"textBrowser_4")
        self.textBrowser_4.setGeometry(QRect(210, 20, 201, 41))
        font3 = QFont()
        font3.setPointSize(12)
        font3.setBold(False)
        font3.setUnderline(True)
        self.textBrowser_4.setFont(font3)
        self.textBrowser_4.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.groupBox_10 = QGroupBox(self.centralwidget)
        self.groupBox_10.setObjectName(u"groupBox_10")
        self.groupBox_10.setGeometry(QRect(1290, 40, 421, 81))
        self.label = QLabel(self.groupBox_10)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 20, 101, 21))
        font4 = QFont()
        font4.setBold(True)
        self.label.setFont(font4)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_2 = QLabel(self.groupBox_10)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 50, 101, 21))
        self.label_2.setFont(font4)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_3 = QLabel(self.groupBox_10)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(130, 20, 101, 21))
        self.label_3.setFont(font4)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_4 = QLabel(self.groupBox_10)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(130, 50, 101, 21))
        self.label_4.setFont(font4)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.groupBox_11 = QGroupBox(self.centralwidget)
        self.groupBox_11.setObjectName(u"groupBox_11")
        self.groupBox_11.setGeometry(QRect(10, 400, 1271, 111))
        self.tableView_7 = QTableView(self.groupBox_11)
        self.tableView_7.setObjectName(u"tableView_7")
        self.tableView_7.setGeometry(QRect(340, 20, 921, 81))
        self.tableView_7.setFont(font)
        self.tableView_7.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.pushButton_6 = QPushButton(self.groupBox_11)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(90, 70, 81, 31))
        self.pushButton_7 = QPushButton(self.groupBox_11)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(170, 70, 81, 31))
        self.pushButton_8 = QPushButton(self.groupBox_11)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(10, 70, 81, 31))
        self.pushButton_10 = QPushButton(self.groupBox_11)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setGeometry(QRect(250, 70, 81, 31))
        self.groupBox_12 = QGroupBox(self.centralwidget)
        self.groupBox_12.setObjectName(u"groupBox_12")
        self.groupBox_12.setGeometry(QRect(10, 10, 1271, 111))
        self.tableView_6 = QTableView(self.groupBox_12)
        self.tableView_6.setObjectName(u"tableView_6")
        self.tableView_6.setGeometry(QRect(340, 20, 921, 81))
        self.tableView_6.setFont(font)
        self.pushButton = QPushButton(self.groupBox_12)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(10, 70, 81, 31))
        self.pushButton_3 = QPushButton(self.groupBox_12)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(250, 70, 81, 31))
        self.pushButton_4 = QPushButton(self.groupBox_12)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(90, 70, 81, 31))
        self.pushButton_5 = QPushButton(self.groupBox_12)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(170, 70, 81, 31))
        self.lcdNumber = QLCDNumber(self.centralwidget)
        self.lcdNumber.setObjectName(u"lcdNumber")
        self.lcdNumber.setGeometry(QRect(1290, 0, 421, 41))
        self.lcdNumber.setDigitCount(19)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1729, 33))
        self.menuMENU = QMenu(self.menubar)
        self.menuMENU.setObjectName(u"menuMENU")
        self.menuSETTING = QMenu(self.menubar)
        self.menuSETTING.setObjectName(u"menuSETTING")
        self.menuTICKER = QMenu(self.menubar)
        self.menuTICKER.setObjectName(u"menuTICKER")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMENU.menuAction())
        self.menubar.addAction(self.menuSETTING.menuAction())
        self.menubar.addAction(self.menuTICKER.menuAction())

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Binance", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("MainWindow", u"LOG", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("MainWindow", u"TRANSACTION", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"ORDER", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"UPBIT", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"ORDER", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"TRANSACTION", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"LOG", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"PRICE(BINANCE,UPBIT)", None))
        self.groupBox_10.setTitle(QCoreApplication.translate("MainWindow", u"INFO_ORDER", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"TextLabel1", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TextLabel2", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"TextLabel3", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"TextLabel4", None))
        self.groupBox_11.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"CLEAR_ALL", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"CLEAR_PLUS", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"REFRESH", None))
        self.pushButton_10.setText(QCoreApplication.translate("MainWindow", u"CANCEL", None))
        self.groupBox_12.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"REFRESH", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"CANCEL", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"CLEAR_ALL", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"CLEAR_PLUS", None))
        self.menuMENU.setTitle(QCoreApplication.translate("MainWindow", u"MENU", None))
        self.menuSETTING.setTitle(QCoreApplication.translate("MainWindow", u"SETTING", None))
        self.menuTICKER.setTitle(QCoreApplication.translate("MainWindow", u"TICKER", None))
    # retranslateUi

