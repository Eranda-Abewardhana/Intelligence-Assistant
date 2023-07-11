from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (QPoint, Qt,)
from PyQt5.QtGui import (QCursor, QFont, QPainter, QIcon, QPen)
from PyQt5.QtWidgets import *
import serial
import time
import math

k1 = 23.75
k2 = 21.5
k3 = 20

def calculate_x(a):
    part1 = math.asin( (k1**2 - k2**2 + k3**2 + a**2) / (2 * k1 * math.sqrt(k3**2 + a**2)) )
    part2 = math.asin( k3 / math.sqrt(k3**2 + a**2) )
    x = part1 - part2
    return x

def calculate_y(x):
    numerator = k1 * math.cos(x) - k3
    denominator = k2
    y = math.acos(numerator / denominator) - x
    return y

ser = serial.Serial('COM10', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(1)
s1,s2,s3,s4,s5=180,100,55,78,26


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # self.ui.horizontalSlider.setDisabled(1)
        self.ui.horizontalSlider.setValue(0)
        self.ui.horizontalSlider_2.setValue(100)
        self.ui.horizontalSlider_3.setValue(100)
        self.ui.horizontalSlider_4.setValue(78)
        self.ui.horizontalSlider_5.setValue(26)

        self.show()
        self.ui.horizontalSlider.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_4.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_5.valueChanged.connect(self.sliderChanged)

    def sliderChanged(self):
        global s1,s2,s3,s4,s5
        tmp_s1 = self.ui.horizontalSlider.value()
        tmp_s2 = self.ui.horizontalSlider_2.value()
        tmp_s3 = self.ui.horizontalSlider_3.value()
        tmp_s4 = self.ui.horizontalSlider_4.value()
        tmp_s5 = self.ui.horizontalSlider_5.value()

        # if 13 < tmp_s3 < 88:
        #     try:
        #         x_val = calculate_x(tmp_s3/2)
        #         y_val = calculate_y(x_val)
        #         command = f"servo_1:{int(math.degrees(y_val))-10},servo_2:{int(math.degrees(x_val))+50}, {tmp_s3}#:#\n"
        #         # print(tmp_s3)
        #         ser.write(command.encode())
        #         while True:
        #             if ser.in_waiting > 0:
        #                 data = ser.readline().decode().rstrip()
        #                 print(data)
        #                 break
        #     except: print("error")
        # else:
        command = ""
        if tmp_s1 != s1:
            command = f"servo_cam:{180-tmp_s1*2}, #:#\n"
            s1 = tmp_s1
        if tmp_s2 != s2:
            command = f"servo_base:{tmp_s2}, #:#\n"
            s2 = tmp_s2
        if tmp_s3 != s3:
            command = f"servo_grip:{tmp_s3}, #:#\n"
            s3 = tmp_s3
        if tmp_s4 != s4:
            command = f"servo_1:{tmp_s4+10}, #:#\n"
            s4 = tmp_s4
        if tmp_s5 != s5:
            command = f"servo_2:{(tmp_s5-12)}, #:#\n"
            s5 = tmp_s5
        # print(command)
        if command != "":
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
