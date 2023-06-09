import pyfirmata
import time
from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen )
from PyQt5.QtWidgets import *


import inspect

if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

############################################

board = pyfirmata.Arduino('COM3')
# servo1 = board.get_pin('d:4:s')
servo2 = board.get_pin('d:5:s')
servo3 = board.get_pin('d:6:s')
servo4 = board.get_pin('d:7:s')
servo5 = board.get_pin('d:10:s')


############################################

servo2.write(50)
servo5.write(80)
servo3.write(110)
servo4.write(0)
time.sleep(0.7)
servo2.write(40)
time.sleep(0.3)
servo2.write(30)

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.horizontalSlider.setDisabled(1)
        self.ui.horizontalSlider_2.setValue(30)
        self.ui.horizontalSlider_3.setValue(50)
        self.ui.horizontalSlider_4.setValue(0)
        self.ui.horizontalSlider_5.setValue(0)

        self.show()
        # self.ui.horizontalSlider.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_4.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_5.valueChanged.connect(self.sliderChanged)

    def sliderChanged(self):
        print(self.ui.horizontalSlider.value(), self.ui.horizontalSlider_2.value(), self.ui.horizontalSlider_3.value(), self.ui.horizontalSlider_4.value(), self.ui.horizontalSlider_5.value())
        # s1 = self.ui.horizontalSlider.value()
        s2 = self.ui.horizontalSlider_2.value()
        s3 = self.ui.horizontalSlider_3.value()
        s4 = self.ui.horizontalSlider_4.value()
        s5 = self.ui.horizontalSlider_5.value()

        # servo1.write(s1)
        servo2.write(82 if s2>82 else s2)
        servo3.write(s3*2.2)
        servo4.write(54 if s4>54 else s4)
        servo5.write(0 if s5>82 else 82-s5)

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