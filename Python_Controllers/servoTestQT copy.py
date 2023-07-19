import math
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
import numpy as np
import cv2
from torch import cuda
from ultralytics import YOLO
import random
from time import time,sleep
from deep_sort_realtime.deepsort_tracker import DeepSort
import threading

arm1_length = 23.75
arm2_length = 21.5
distance_arm_cam = 29
object_distance = 20

stop_threads = False

def calculate_arm_angles(x, y):
    r = math.sqrt(x**2 + y**2)
    ang = math.atan2(y, x)
    y1 = math.acos((arm1_length**2+arm2_length**2-r**2)/(2*arm1_length*arm2_length))
    x1 = ang+math.asin(arm2_length*math.sin(y1)/r)
    return int(math.degrees(x1)),int(math.degrees(y1))

def calculate_baseAngle(angle_cam, object_distance):
    grip_distance = math.sqrt( object_distance**2 + distance_arm_cam**2 - 2*distance_arm_cam*object_distance*math.cos(math.radians(angle_cam+50)) )
    grip_angle = math.degrees( math.asin( object_distance*math.sin(math.radians(angle_cam+50)) / grip_distance ) )
    return int(grip_distance), int(grip_angle)


try: ser = serial.Serial('COM10', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port
except: print("No Serial")

# time.sleep(1)

servo_cam, servo_base, servo_grip, servo_1, servo_2 = 30,90,0,120,0

gripperLoc_x, gripperLoc_y = 25,10




class MainWindow(QMainWindow):
    kp = [0.02, 0.02]  # Proportional gain
    ki = [0.0, 0.0]  # Integral gain
    kd = [0.0, 0.0]  # Derivative gain

    last_time = 0  # Last time update occurred
    error_sum_x = 0.0  # Cumulative error
    last_error_x = 0.0  # Last error
    error_sum_y = 0.0  # Cumulative error
    last_error_y = 0.0  # Last error

    def __init__(self):
        super().__init__()
        global gripperLoc_x, gripperLoc_y, servo_cam, servo_base, servo_grip, servo_1, servo_2

        self.device = 'cuda' if cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = YOLO("yolov8n.pt")
        self.model.fuse()
        self.tracker = DeepSort(max_age=5)
        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]
        self.CLASS_NAMES_DICT = self.model.names
        self.SendData(f"servo_cam:{servo_cam}, #:#\n")

        self.resize(1200, 600)

        self.image_label = QLabel(self)
        self.video_stream = cv2.VideoCapture(1)
        assert self.video_stream.isOpened()

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_frame) # type: ignore
        # self.timer.start(30)  # Update the frame every 30ms (30 FPS)
        
        threading.Thread(target = self.flow).start()

        self.centralwidget = QWidget()

        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        
        self.verticalLayout_2 = QVBoxLayout()
        
        self.horizontalLayout = QHBoxLayout()

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout_3 = QVBoxLayout()

        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.addWidget(self.image_label)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.slider1 = QSlider()
        self.slider1.setOrientation(Qt.Horizontal) # type: ignore

        self.slider2 = QSlider()
        self.slider2.setOrientation(Qt.Horizontal) # type: ignore

        self.slider3 = QSlider()
        self.slider3.setOrientation(Qt.Horizontal) # type: ignore

        self.slider4 = QSlider()
        self.slider4.setOrientation(Qt.Horizontal) # type: ignore

        self.slider5 = QSlider()
        self.slider5.setOrientation(Qt.Horizontal) # type: ignore

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # self.figure2 = Figure()
        # self.canvas2 = FigureCanvas(self.figure2)
        # self.ax2 = self.figure2.add_subplot(222)

        self.horizontalLayout.addWidget(self.canvas)
        # self.horizontalLayout.addWidget(self.canvas2)

        self.verticalLayout_3.addWidget(QLabel("servo_cam"))
        self.verticalLayout_3.addWidget(self.slider1)

        self.verticalLayout_3.addWidget(QLabel("servo_base"))
        self.verticalLayout_3.addWidget(self.slider2)

        self.verticalLayout_3.addWidget(QLabel("servo_grip"))
        self.verticalLayout_3.addWidget(self.slider3)

        self.verticalLayout_3.addWidget(QLabel("gripperLoc_x"))
        self.verticalLayout_3.addWidget(self.slider4)

        self.verticalLayout_3.addWidget(QLabel("gripperLoc_y"))
        self.verticalLayout_3.addWidget(self.slider5)

        self.setCentralWidget(self.centralwidget)

        self.slider1.setRange(0, 180)
        self.slider2.setRange(10, 170)
        self.slider3.setRange(0, 70)
        self.slider4.setRange(0, 50)
        self.slider5.setRange(0, 30)

        self.slider1.setValue(servo_cam)
        self.slider2.setValue(servo_base)
        self.slider3.setValue(servo_grip)
        self.slider4.setValue(gripperLoc_x)
        self.slider5.setValue(gripperLoc_y)

        self.show()
        self.update_plot()

        self.slider1.valueChanged.connect(self.sliderChanged)
        self.slider2.valueChanged.connect(self.sliderChanged)
        self.slider3.valueChanged.connect(self.sliderChanged)
        self.slider4.valueChanged.connect(self.sliderChanged)
        self.slider5.valueChanged.connect(self.sliderChanged)


    def flow(self):
        global servo_cam, object_distance, servo_1, servo_2, servo_base

        thread = threading.Thread(target = self.getGripPos)
        thread.start()
        thread.join()
        
        try:
            grip_distance, servo_base = calculate_baseAngle(servo_cam, object_distance)
            for angle in range(90, servo_base, -1):
                self.SendData(f"servo_base:{angle}, #:#\n")
                sleep(0.05)

            for distance in range(5, grip_distance):
                servo_1, servo_2 = calculate_arm_angles(distance, 5)
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
                sleep(0.05)

            self.SendData(f"servo_grip:20, #:#\n")
            sleep(0.5)

            for distance in range(grip_distance, 5, -1):
                servo_1, servo_2 = calculate_arm_angles(distance, 5)
                servo_2 = 180 - servo_1
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
                sleep(0.05)

            for angle in range(servo_base, 90):
                self.SendData(f"servo_base:{angle}, #:#\n")
                sleep(0.05)

        except:
            print("Math err")


    def SendData(self, dataStr):
        try:
            ser.write(dataStr.encode())

            string = ""
            while True:
                if ser.in_waiting > 0:
                    string = ser.readline().decode().rstrip()
                    break
            
            # print(string)
            segments = string.split(",")

            key_value_pairs = {}
            for segment in segments:
                colon_index = segment.find(":")
                if colon_index != -1:
                    key = segment[:colon_index].strip()
                    value = segment[colon_index+1:].strip()
                    key_value_pairs[key] = value

            return key_value_pairs
        except:
            print("Err<< :", dataStr)


    def update_plot(self):
        lx1 = arm1_length * math.cos(math.radians(servo_1)) * math.cos(math.radians(servo_base-100))
        lz1 = arm1_length * math.sin(math.radians(servo_1))
        ly1 = arm1_length * math.cos(math.radians(servo_1)) * math.sin(math.radians(servo_base-100))

        realY = math.radians(servo_1) + math.radians(servo_2) - math.pi
        lx2 = arm2_length * math.cos(realY) * math.cos(math.radians(servo_base-100))
        lz2 = arm2_length * math.sin(realY)
        ly2 = arm2_length * math.cos(realY) * math.sin(math.radians(servo_base-100))

        self.ax.clear()

        # Arm1
        x = np.array([0, lx1])
        y = np.array([0, ly1])
        z = np.array([0, lz1])

        self.ax.plot(x, y, z, linewidth=1.5, color='blue')

        # Arm2
        x = np.array([lx1, lx1+lx2])
        y = np.array([ly1, ly1+ly2])
        z = np.array([lz1, lz1+lz2])

        self.ax.plot(x, y, z, linewidth=1.5, color='green')

        # Gripper
        self.ax.scatter(x, y, z, color='blue', s=10)

        # Mid Line
        x = np.array([0, distance_arm_cam])
        y = np.array([0, 0])
        z = np.array([0, 0])

        self.ax.plot(x, y, z, linewidth=0.5, color='black')

        x = np.array([-6, 17.5*math.cos(math.radians(70))-6, 35.5-6, 35.5-6, 17.5*math.cos(math.radians(70))-6, -6])
        y = np.array([0, 17.5*math.sin(math.radians(70)), 6.25, -6.25, -17.5*math.sin(math.radians(70)), 0])
        z = np.array([0, 0, 0, 0, 0, 0])

        self.ax.plot(x, y, z, linewidth=0.5, color='black')

        # Object Line
        grip_distance, grip_angle = calculate_baseAngle(servo_cam, object_distance)

        lx1 = grip_distance*math.cos(math.radians(grip_angle))
        ly1 = grip_distance*math.sin(math.radians(grip_angle))

        lx2 = distance_arm_cam - object_distance*math.cos(math.radians(servo_cam+50))
        ly2 = object_distance*math.sin(math.radians(servo_cam+50))

        x = np.array([distance_arm_cam, lx2, 0])
        y = np.array([0, -ly2, 0])
        z = np.array([0, 0, 0])

        self.ax.plot(x, y, z, linewidth=1, color='red')

        # Object
        self.ax.scatter(lx2, -ly2, 0, color='red', s=10)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        # self.ax.set_title('3D Beam Visualization')

        self.ax.set_xlim3d(-15, 35)
        self.ax.set_ylim3d(-25, 15)
        self.ax.set_zlim3d(0, 20)

        self.canvas.draw()

    def sliderChanged(self):
        global servo_cam,servo_base,servo_grip,servo_1,servo_2
        global gripperLoc_x, gripperLoc_y
        
        slider1_value = self.slider1.value()
        slider2_value = self.slider2.value()
        slider3_value = self.slider3.value()
        slider4_value = self.slider4.value()
        slider5_value = self.slider5.value()

        command = ""

        if slider1_value != servo_cam:
            command = f"servo_cam:{slider1_value}, #:#\n"
            servo_cam = slider1_value
        if slider2_value != servo_base:
            print(slider2_value)
            command = f"servo_base:{slider2_value}, #:#\n"
            servo_base = slider2_value
        if slider3_value != servo_grip:
            command = f"servo_grip:{slider3_value}, #:#\n"
            servo_grip = slider3_value
        # if slider3_value != servo_grip:
        #     if servo_grip<slider3_value:
        #         x_val, y_val = calculate_arm_angles(slider3_value/2)
        #     else:
        #         x_val, y_val = calculate_arm_angles(slider3_value/2)
        #         y_val = 180 - x_val
        #     # servo_grip = slider3_value
        #     command = f"servo_1:{x_val},servo_2:{y_val}, {slider3_value}#:#\n"
        #     servo_grip = slider3_value
        #     # print(command)
        if slider4_value != gripperLoc_x or slider5_value != gripperLoc_y:
            gripperLoc_x = slider4_value
            gripperLoc_y = slider5_value
            print(gripperLoc_x, gripperLoc_y)

            try:
                servo_1, servo_2 = calculate_arm_angles(gripperLoc_x, gripperLoc_y)
                command = f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n"
            except:
                print("Math err")

        # print(command)
        if command != "" and 'ser' in globals():
            ser.write(command.encode())
            while True:
                if ser.in_waiting > 0:
                    data = ser.readline().decode().rstrip()
                    print(data)
                    break
        self.update_plot()

    def getGripPos(self):
        global object_distance, servo_cam, stop_threads
        targetDone = 0
        while not stop_threads:
            ret, frame = self.video_stream.read()
            if ret:
                start_time = time()
                # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                results = self.model.predict(frame, verbose=False)[0]

                detections = []
                for r in results.boxes.data.tolist():
                    x1, y1, x2, y2, score, class_id = r
                    if(class_id == 0):
                        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                        detections.append([[x1, y1, x2, y2], score, class_id])

                tracked = self.tracker.update_tracks(detections, frame=frame)
                
                for track in tracked:   
                    if not track.is_confirmed():
                        continue
                    track_id = int(track.track_id)
                    color = self.colors[track_id % len(self.colors)]
                    
                    x1, y1, x2, y2 = map(int, track.to_ltwh(orig=True))
                    obj_mid = [int((x1+x2)/2),int((y1+y2)/2)]

                    frame_width_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
                    frame_height_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

                    errorX = (obj_mid[0] - frame_width_mid)
                    errorY = (frame_height_mid - obj_mid[1])
                                    
                    # print("Change X : ", errorX, " | Change Y : ", errorY)
                    cv2.line(frame, (frame_width_mid, frame_height_mid), (obj_mid[0], frame_height_mid), color, 2)
                    cv2.line(frame, (frame_width_mid, frame_height_mid), (frame_width_mid, obj_mid[1]), color, 2)
                    cv2.putText(frame,f'X:{errorX} | Y:{errorY}',(obj_mid[0],obj_mid[1]),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,255),1)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (color), 3)
                    # cv2.circle(frame,(obj_mid[0],obj_mid[1]),4,(255,0,0),-1)
                    cv2.putText(frame,f'ID : {track_id}',(x1,y1),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)

                    current_time = time()
                    self.elapsed_time = current_time - self.last_time

                    self.error_sum_x += errorX * self.elapsed_time
                    d_error_x = (errorX - self.last_error_x) / self.elapsed_time

                    self.error_sum_y += errorY * self.elapsed_time
                    d_error_y = (errorY - self.last_error_y) / self.elapsed_time

                    finalErr_x = self.kp[0] * errorX + self.ki[0] * self.error_sum_x + self.kd[0] * d_error_x
                    finalErr_y = self.kp[1] * errorY + self.ki[1] * self.error_sum_y + self.kd[1] * d_error_y

                    servo_cam -= round(finalErr_x)
                    if servo_cam < 0: servo_cam = 0
                    if servo_cam > 180: servo_cam = 180
                    
                    response = self.SendData(f"servo_cam:{servo_cam},distance:0, #:#\n")
                    if type(response) == 'dict':
                        object_distance = response['Distance']

                    self.slider1.setValue(servo_cam)
                    
                    if (-0.3 < finalErr_x < 0.3):
                        targetDone +=1

                    if( targetDone > 3 ):
                        print(finalErr_x)
                        return finalErr_x

                    self.last_error_x = errorX
                    self.last_error_y = errorY
                    self.last_time = current_time

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(640, 480, Qt.KeepAspectRatio) # type: ignore
                self.image_label.setPixmap(scaled_pixmap)
                # self.update_plot()

                end_time = time()
                fps = round(1/(end_time - start_time), 2)
                print(f'FPS: {fps}')


    def closeEvent(self, event):
        global stop_threads
        self.video_stream.release()
        self.SendData("m_stop:1, #:#\n")
        event.accept()
        stop_threads = False
        try: ser.close()
        except: pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())