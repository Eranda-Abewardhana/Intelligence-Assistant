
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(648, 220)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalSlider = QSlider(self.centralwidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(40, 30, 511, 22))
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider_2 = QSlider(self.centralwidget)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        self.horizontalSlider_2.setGeometry(QRect(40, 70, 511, 22))
        self.horizontalSlider_2.setOrientation(Qt.Horizontal)
        self.horizontalSlider_3 = QSlider(self.centralwidget)
        self.horizontalSlider_3.setGeometry(QRect(40, 110, 511, 22))
        self.horizontalSlider_3.setOrientation(Qt.Horizontal)
        
        self.horizontalSlider_4 = QSlider(self.centralwidget)
        self.horizontalSlider_4.setGeometry(QRect(40, 150, 511, 22))
        self.horizontalSlider_4.setOrientation(Qt.Horizontal)

        self.horizontalSlider_5 = QSlider(self.centralwidget)
        self.horizontalSlider_5.setGeometry(QRect(40, 190, 511, 22))
        self.horizontalSlider_5.setOrientation(Qt.Horizontal)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

