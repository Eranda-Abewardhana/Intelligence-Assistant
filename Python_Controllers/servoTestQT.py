import pyfirmata
import time
from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen)
from PyQt5.QtWidgets import *
import inspect

def start():
    servo2.write(98)
    servo3.write(32)
    servo4.write(35)
    servo5.write(50)
    
def detach():
    servo2.pin = None
    servo3.pin = None
    servo4.pin = None
    servo5.pin = None
    
    

if not hasattr(inspect, 'getargspec'):
    inspect.getargspec = inspect.getfullargspec

############################################ 98 32 35 50

board = pyfirmata.Arduino('COM3')
servo2 = board.get_pin('d:4:s')
servo3 = board.get_pin('d:5:s')
servo4 = board.get_pin('d:6:s')
servo5 = board.get_pin('d:7:s')

############################################

start()
detach()

class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.horizontalSlider.setDisabled(1)
        self.ui.horizontalSlider_2.setValue(98)
        self.ui.horizontalSlider_3.setValue(32)
        self.ui.horizontalSlider_4.setValue(35)
        self.ui.horizontalSlider_5.setValue(50)

        self.show()
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_4.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_5.valueChanged.connect(self.sliderChanged)

    def sliderChanged(self):
        s2 = self.ui.horizontalSlider_2.value()
        s3 = self.ui.horizontalSlider_3.value()
        s4 = self.ui.horizontalSlider_4.value()
        s5 = self.ui.horizontalSlider_5.value()

        servo2.write(s2)
        servo3.write(s3)
        servo4.write(s4)
        servo5.write(s5)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    board.exit()
