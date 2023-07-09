from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen)
from PyQt5.QtWidgets import *
import serial
import time

ser = serial.Serial('COM10', 9600)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(1)


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.horizontalSlider.setDisabled(1)
        self.ui.horizontalSlider_2.setValue(100)
        self.ui.horizontalSlider_3.setValue(0)
        self.ui.horizontalSlider_4.setValue(78)
        self.ui.horizontalSlider_5.setValue(26)

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

        command = f"servo_base:{s2},servo_grip:{s3},servo_1:{s4},servo_2:{s5}, #:#"
        ser.write(command.encode())
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode().rstrip()
                print(data)
                break

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    def exit():
        app.exec_()
        ser.close()
    sys.exit(exit())
