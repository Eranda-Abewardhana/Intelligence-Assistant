import requests
from new import *
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


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

    def sendRequest(self, stop=0, x_err=0, y_err=0, m_init=0, servo_base=0, servo_grip=0, servo_1=0, servo_2=0):
        url = "http://192.168.137.45"
        payload = {
            'stop': stop,
            'x_err': x_err,
            'y_err': y_err,
            'm_init': m_init,
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
        self.sendRequest(servo_base=s1, servo_grip=s2, servo_1=s3, servo_2=s4)


    def mouseMoveEvent(self, QMouseEvent):
        x = int(QMouseEvent.pos().x()*4-1200)
        y = int(QMouseEvent.pos().y()*1.2-250)
        print(x, -y)
        # self.sendRequest(stop=0, x_err=x, m_init=-y)
        painter = QPainter(self)
        painter.setPen(QPen((0,255,0), 2, Qt.SolidLine))
        painter.drawEllipse(QPoint(x,y), 1, 1)
        painter.end()

    def mouseReleaseEvent(self, QMouseEvent):
        cursor = QtGui.QCursor()
        print(cursor.pos())
        self.sendRequest(stop=1)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
    board.exit()