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
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(400, 300)

        # QDialogButtonBox 생성
        self.buttonBox = QDialogButtonBox(MainWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)

        self.retranslateUi(MainWindow)

        # 버튼 신호를 사용자 정의 슬롯에 연결
        self.buttonBox.accepted.connect(self.on_accepted)
        self.buttonBox.rejected.connect(self.on_rejected)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))

    # 사용자 정의 슬롯 메서드
    def on_accepted(self):
        print("Accepted button clicked")
        # 여기에 OK 버튼 클릭 시 수행할 동작을 추가하세요

    def on_rejected(self):
        print("Rejected button clicked")

