import pyfirmata
import time
from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen )
from PyQt5.QtWidgets import *

board = pyfirmata.Arduino('COM4')
servo1 = board.get_pin('d:9:s')
servo2 = board.get_pin('d:10:s')
servo3 = board.get_pin('d:11:s')

servo1.write(0)
servo2.write(0)
servo3.write(0)

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()
        self.ui.horizontalSlider.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)

    def sliderChanged(self):
        print(self.ui.horizontalSlider.value(), self.ui.horizontalSlider_2.value(), self.ui.horizontalSlider_3.value())
        servo1.write(self.ui.horizontalSlider.value())
        servo2.write(self.ui.horizontalSlider_2.value())
        servo3.write(self.ui.horizontalSlider_3.value())

    # def mouseMoveEvent(self, QMouseEvent):
    #     x = QMouseEvent.pos().x()/4
    #     y = QMouseEvent.pos().y()/4
    #     print(x, y)
    #     if(0<x<256 and 0<y<256):
    #         servo1.write(x)
    #         servo2.write(y)
    #         # time.sleep(.3)
    #         # painter = QPainter(self)
    #         # painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
    #         # painter.drawEllipse(QPoint(x,y), 1, 1)
    #         # painter.end()

    # def mouseReleaseEvent(self, QMouseEvent):
    #     cursor = QtGui.QCursor()
    #     print(cursor.pos())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    board.exit()