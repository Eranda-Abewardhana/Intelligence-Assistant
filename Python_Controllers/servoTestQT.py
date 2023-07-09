from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen)
from PyQt5.QtWidgets import *
import serial
import time

ser = serial.Serial('COM10', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(1)
s2,s3,s4,s5=50,0,50,50


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.horizontalSlider.setDisabled(1)
        self.ui.horizontalSlider_2.setValue(50)
        self.ui.horizontalSlider_3.setValue(0)
        self.ui.horizontalSlider_4.setValue(50)
        self.ui.horizontalSlider_5.setValue(50)

        self.show()
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_4.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_5.valueChanged.connect(self.sliderChanged)

    def sliderChanged(self):
        global s2,s3,s4,s5
        tmp_s2 = self.ui.horizontalSlider_2.value()
        tmp_s3 = self.ui.horizontalSlider_3.value()
        tmp_s4 = self.ui.horizontalSlider_4.value()
        tmp_s5 = self.ui.horizontalSlider_5.value()

        command = ""
        if tmp_s2 != s2:
            command = f"servo_base:{(s2-tmp_s2)}, #:#\n"
            s2 = tmp_s2
        if tmp_s3 != s3:
            command = f"servo_grip:{s3}, #:#\n"
            s3 = tmp_s3
        if tmp_s4 != s4:
            command = f"servo_1:{(s4-tmp_s4)}, #:#\n"
            s4 = tmp_s4
        if tmp_s5 != s5:
            command = f"servo_2:{(s5-tmp_s5)}, #:#\n"
            s5 = tmp_s5
        # print(command)
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
