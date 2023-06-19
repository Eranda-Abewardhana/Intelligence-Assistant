import requests
from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.horizontalSlider_5.setDisabled(True)
        self.ui.horizontalSlider.setValue(110)
        self.ui.horizontalSlider_2.setValue(0)
        self.ui.horizontalSlider_3.setValue(80)
        self.ui.horizontalSlider_4.setValue(50)
        self.ui.horizontalSlider_5.setValue(0)

        self.show()
        self.ui.horizontalSlider.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_3.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_4.valueChanged.connect(self.sliderChanged)
        self.ui.horizontalSlider_5.valueChanged.connect(self.sliderChanged)

    def sendRequest(self, servo_base, servo_grip, servo_1, servo_2):
        url = "http://192.168.114.127"
        payload = {
            'stop': 1,
            'x_err': 0,
            'y_err': 0,
            'm_init': 0,
            'servo_base': servo_base,
            'servo_grip': servo_grip, # MAX 65
            'servo_1': servo_1,
            'servo_2': servo_2,
        }
        try:
            response = requests.get(url, params=payload, verify=False, timeout=1)
            if response.status_code == 200:
                print("Response content : ")
                print(response.text)
            else:
                print("Request failed with status code:", response.status_code)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def sliderChanged(self):
        print(self.ui.horizontalSlider.value(), self.ui.horizontalSlider_2.value(), self.ui.horizontalSlider_3.value(), self.ui.horizontalSlider_4.value(), self.ui.horizontalSlider_5.value())
        s1 = self.ui.horizontalSlider.value()
        s2 = self.ui.horizontalSlider_2.value()
        s3 = self.ui.horizontalSlider_3.value()
        s4 = self.ui.horizontalSlider_4.value()
        s5 = self.ui.horizontalSlider_5.value()
        self.sendRequest(s1, s2, s3, s4)


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