import math
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import QRect, Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QKeyEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
import numpy as np
import cv2
from torch import cuda
from ultralytics import YOLO
import tensorflow as tf
import random
from time import time,sleep
from deep_sort_realtime.deepsort_tracker import DeepSort

arm1_length = 23.75
arm2_length = 21.5
distance_arm_cam = 29
object_distance = 20
targetDoneCount = 0

getGripPos = False
gripObject = False
ObjectAvailable = False
UpdatePlot = True
reachObject = False
SearchObject = False

vehicle_angle = 0

servo_cam, servo_base, servo_grip, servo_1, servo_2 = 138,90,0,120,0

gripperLoc_x, gripperLoc_y = 25,10


Slope1 = 4.498256643245813
Intercept1 = 2.6

Slope2 = 4.460188933873144
Intercept2 = -4.5

def angle_to_motor1(angle):
    return int(Slope1*angle + Intercept1)

def angle_to_motor2(angle):
    return int(Slope2*angle + Intercept2)

def calculate_arm_angles(x, y):
    r = math.sqrt(x**2 + y**2)
    ang = math.atan2(y, x)
    y1 = math.acos((arm1_length**2+arm2_length**2-r**2)/(2*arm1_length*arm2_length))
    x1 = ang+math.asin(arm2_length*math.sin(y1)/r)
    return int(math.degrees(x1)),int(math.degrees(y1))

def calculate_baseAngle(angle_cam, object_distance):
    grip_distance = math.sqrt( object_distance**2 + distance_arm_cam**2 - 2*distance_arm_cam*object_distance*math.cos(math.radians(angle_cam+42)) )
    grip_angle = math.degrees( math.asin( object_distance*math.sin(math.radians(angle_cam+42)) / grip_distance ) )
    return int(grip_distance)+2, 90-int(grip_angle)-3


try: ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace '/dev/ttyACM0'
except: print("No Serial")

sleep(1)


interpreter = tf.lite.Interpreter("Image_Processing/TF_Lite/NEW/lite-model_ssd_spaghettinet_edgetpu_large_320_uint8_nms_1.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

boxes = []
classes = []
scores = []


class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        global boxes, classes, scores, output_details, input_details, interpreter
        while True:
        #     if not getGripPos:
        #         self.parent.getGripPos()
        #         continue
            
        #     if not gripObject:
        #         self.parent.gripObject()
        #         break
            try:
                ret, frame = self.parent.video_stream.read()
                if ret:
                    start_time = time()

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    input_shape = input_details[0]['shape']
                    frame_resized = cv2.resize(frame_rgb, (input_shape[2], input_shape[1]))
                    input_data = np.expand_dims(frame_resized, axis=0)

                    interpreter.set_tensor(input_details[0]['index'],input_data)
                    interpreter.invoke()

                    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
                    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
                    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

                    for i in range(len(scores)):
                        # continue
                        class_id = int(classes[i])
                        if (int(class_id)==43 and scores[i] > 0.5):
                            # int(class_id)==0 and
                            ymin = int(max(1,(boxes[i][0] * 360)))
                            xmin = int(max(1,(boxes[i][1] * 640)))
                            ymax = int(min(360,(boxes[i][2] * 360)))
                            xmax = int(min(640,(boxes[i][3] * 640)))

                            color = self.parent.colors[class_id % len(self.parent.colors)]
                            # cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (color), 3)
                            # cv2.putText(frame,f'ID : {class_id}',(xmin,ymin),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)

                            left, top, right, bottom = xmin, ymin, xmax, ymax
                            # detections.append([[xmin, ymin, xmax, ymax], scores[i], int(classes[i])])

                            obj_mid = [int((left+right)/2),int((top+bottom)/2)]

                            frame_width_mid = int(self.parent.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
                            frame_height_mid = int(self.parent.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

                            errorX = (obj_mid[0] - frame_width_mid)
                            errorY = (frame_height_mid - obj_mid[1])
                                            
                            # print("Change X : ", errorX, " | Change Y : ", errorY)
                            cv2.line(frame, (frame_width_mid, frame_height_mid), (obj_mid[0], frame_height_mid), color, 2)
                            cv2.line(frame, (frame_width_mid, frame_height_mid), (frame_width_mid, obj_mid[1]), color, 2)
                            cv2.putText(frame,f'X:{errorX} | Y:{errorY}',(obj_mid[0],obj_mid[1]),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,255),1)

                            cv2.rectangle(frame, (left, top), (right, bottom), (color), 3)
                            # cv2.circle(frame,(obj_mid[0],obj_mid[1]),4,(255,0,0),-1)
                            cv2.putText(frame,f'ID : {class_id}',(left,top),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)

                    end_time = time()
                    fps = round(1/(end_time - start_time), 2)
                    cv2.putText(frame,f'FPS : {fps}',(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),1)

                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)
                    scaled_pixmap = pixmap.scaled(640, 360, Qt.KeepAspectRatio) # type: ignore
                    self.parent.image_label.setPixmap(scaled_pixmap)

            except: pass
        print("finished")

        self.finished.emit()


class MainWindow(QMainWindow):
    kp_cam = [0.01, 1]  # Proportional gain
    kp_vehicle = [0.041, 1]  # Proportional gain


    def __init__(self):
        super().__init__()
        global gripperLoc_x, gripperLoc_y, servo_cam, servo_base, servo_grip, servo_1, servo_2

        # self.device = 'cuda' if cuda.is_available() else 'cpu'
        # print("Using Device: ", self.device)
        # self.model = YOLO("yolov8n.pt")
        # self.model.fuse()
        # self.tracker = DeepSort(max_age=5)
        # self.CLASS_NAMES_DICT = self.model.names

        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]

        self.SendData(f"servo_cam:{servo_cam}, #:#\n")

        self.resize(1300, 800)

        self.image_label = QLabel(self)
        self.video_stream = cv2.VideoCapture(0)
        self.video_stream.set(3,640)
        self.video_stream.set(4,360)
        assert self.video_stream.isOpened()
        print("running")

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

        self.thread = WorkerThread(parent=self)
        # self.thread.finished.connect(self.task_completed)
        self.thread.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.flow) # type: ignore
        self.timer.start(1)  # (30 FPS)


    def flow(self):
        global gripObject, SearchObject

        if not SearchObject:
            self.SearchObject()
            return
        
        if not gripObject:
            self.gripObject()
            return
        
        print(">>>>>>>>>>>> ALL DONE <<<<<<<<<<<<<<")
        
    def SearchObject(self):
        global ObjectAvailable
        if not ObjectAvailable:
            self.SendData(f"m1_pos:6,m2_pos:-6, #:#\n")
            sleep(0.2)
            self.ObjectAvailable()
        else:
            self.reachObject()


    def gotoObjectLeft(self):
        global SearchObject, servo_cam, targetDoneCount
        arr = [[80 ,0, 3], [10, 10, 1.5], [0, 80, 3], [20, 20, 1.5]]
        for item in arr:
            if item[0]==0 and item[1]!=0:
                if item[1] > 0:
                    m2 = angle_to_motor2(item[1])
                    for _ in range(m2):
                        self.SendData(f"m2_pos:-1, #:#\n")
                else:
                    m2 = angle_to_motor2(-item[1])
                    for _ in range(m2):
                        self.SendData(f"m2_pos:1, #:#\n")
            elif item[1]==0 and item[0]!=0:
                if item[0] > 0:
                    m1 = angle_to_motor1(item[0])
                    for _ in range(m1):
                        self.SendData(f"m1_pos:-1, #:#\n")
                else:
                    m1 = angle_to_motor1(-item[0])
                    for _ in range(m1):
                        self.SendData(f"m1_pos:1, #:#\n")
            else:
                if item[0] > 0:
                    m1 = angle_to_motor1(item[0])
                    for _ in range(m1):
                        self.SendData(f"m1_pos:-1,m2_pos:-1, #:#\n")
                else:
                    m1 = angle_to_motor1(-item[0])
                    for _ in range(m1):
                        self.SendData(f"m1_pos:1,m2_pos:1, #:#\n")
            sleep(0.5)
            
        SearchObject = True
        servo_cam = 30
        targetDoneCount = 0
        self.SendData(f"servo_cam:{servo_cam}, #:#\n")
        print("gripping.............")


    def reachObject(self):
        global boxes, classes, scores
        global object_distance, servo_cam, reachObject, targetDoneCount
    
        # print(scores)
        # print(classes)

        if 43 not in map(int, classes):
            targetDoneCount = 0

        for i in range(len(scores)):
            class_id = int(classes[i])
            if (int(class_id)==43 and scores[i] > 0.6):
                ymin = int(max(1,(boxes[i][0] * 360)))
                xmin = int(max(1,(boxes[i][1] * 640)))
                ymax = int(min(360,(boxes[i][2] * 360)))
                xmax = int(min(640,(boxes[i][3] * 640)))

                left, top, right, bottom = xmin, ymin, xmax, ymax

                obj_mid = [int((left+right)/2),int((top+bottom)/2)]

                frame_width_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
                frame_height_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

                errorX = (obj_mid[0] - frame_width_mid)
                errorY = (frame_height_mid - obj_mid[1])

                print("Final ERR : ", errorX)

                if (-30 < errorX < 30):
                    targetDoneCount +=1
                else:
                    targetDoneCount = 0

                finalErr_x = self.kp_vehicle[0] * errorX
                finalErr_y = self.kp_vehicle[1] * errorY

                intErr = round(finalErr_x)

                if intErr > 0:
                    self.SendData(f"m2_pos:{-intErr}, #:#\n", 0)
                else:
                    self.SendData(f"m1_pos:{intErr}, #:#\n", 0)

        if( targetDoneCount > 10 ):
            Distance = []
            for i in range(11):
                response = self.SendData(f"distance:0, #:#\n", 0)
                if response['Distance']:
                    Distance.append(int(response['Distance']))
                    if i%2==0:
                        self.SendData(f"m1_pos:-5,m2_pos:-5, #:#\n", 0)
                sleep(0.02)
            object_distance = int(np.percentile(Distance, 50))
            if object_distance < 25:
                self.gotoObjectLeft()
            print("Object_distance : ", object_distance)

            reachObject = True
        else:
            sleep(0.1)
                        

    def SendData(self, dataStr, show=1):
        try:
            ser.write(dataStr.encode())

            string = ""
            while True:
                if ser.in_waiting > 0:
                    string = ser.readline().decode().rstrip()
                    break
            
            if show==1: print(string)

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


    def gripObject(self):
        global gripObject, getGripPos, servo_cam, object_distance, UpdatePlot, ObjectAvailable
        try:
            UpdatePlot = False
            
            if ObjectAvailable:
                self.getGripPos()
                if not getGripPos: return

                grip_distance, servo_base_tmp = calculate_baseAngle(servo_cam, object_distance)
                print(">>>>>>>>>>>>>>>>",grip_distance, servo_base_tmp,">>>>>>>>>>>>>>>>>>")
                # self.slider2.setValue(servo_base)
                # self.slider4.setValue(grip_distance)
                # return

                self.slider2.setValue(servo_base_tmp)

                sleep(1)
                servo_grip = 0
                self.slider3.setValue(servo_grip)

                sleep(1)
                
                for distance in range(10, grip_distance+1):
                    self.slider4.setValue(distance)
                    self.slider5.setValue(int(5-(distance-10)/3))
                    sleep(0.06)

                sleep(1)
                servo_grip = 50
                self.slider3.setValue(servo_grip)
                sleep(2.5)

                for distance in range(grip_distance, 10, -1):
                    self.slider4.setValue(distance)
                    self.slider5.setValue(int(5-(distance-10)/3))
                    sleep(0.06)

                sleep(1)

                getGripPos = False
                self.ObjectAvailable()

            else:
                print("got<<<<<<<<<<<<<<<<<<")
                for angle in range(servo_base, 91):
                    self.slider2.setValue(angle)
                    sleep(0.04)

                sleep(1)
                servo_grip = 0
                self.slider3.setValue(servo_grip)

                gripObject = True
                UpdatePlot = True

                print("<<<<<<<<<< done >>>>>>>>>>>>")
        except:
            print("Math err")


    def update_plot(self):
        lx1 = arm1_length * math.cos(math.radians(servo_1)) * math.cos(math.radians(servo_base-90))
        lz1 = arm1_length * math.sin(math.radians(servo_1))
        ly1 = arm1_length * math.cos(math.radians(servo_1)) * math.sin(math.radians(servo_base-90))

        realY = math.radians(servo_1) + math.radians(servo_2) - math.pi
        lx2 = arm2_length * math.cos(realY) * math.cos(math.radians(servo_base-90))
        lz2 = arm2_length * math.sin(realY)
        ly2 = arm2_length * math.cos(realY) * math.sin(math.radians(servo_base-90))

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

        lx2 = distance_arm_cam - object_distance*math.cos(math.radians(servo_cam+42))
        ly2 = object_distance*math.sin(math.radians(servo_cam+42))

        x = np.array([distance_arm_cam, lx2, 0])
        y = np.array([0, -ly2, 0])
        z = np.array([0, 0, 0])

        self.ax.plot(x, y, z, linewidth=1, color='red')

        # Object
        self.ax.scatter(lx2, -ly2, 0, color='red', s=10)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Robot Arm')

        self.ax.set_xlim3d(-15, 35)
        self.ax.set_ylim3d(-25, 25)
        self.ax.set_zlim3d(0, 50)

        self.canvas.draw()


    def sliderChanged(self):
        global servo_cam, servo_base, servo_grip, servo_1, servo_2
        global gripperLoc_x, gripperLoc_y, UpdatePlot
        
        slider1_value = self.slider1.value()
        slider2_value = self.slider2.value()
        slider3_value = self.slider3.value()
        slider4_value = self.slider4.value()
        slider5_value = self.slider5.value()

        if slider1_value != servo_cam:
            self.SendData(f"servo_cam:{slider1_value}, #:#\n")
            servo_cam = slider1_value
        if slider2_value != servo_base:
            self.SendData(f"servo_base:{slider2_value}, #:#\n")
            servo_base = slider2_value
        if slider3_value != servo_grip:
            self.SendData(f"servo_grip:{slider3_value}, #:#\n")
            servo_grip = slider3_value
        if slider4_value != gripperLoc_x or slider5_value != gripperLoc_y:
            print(gripperLoc_x, gripperLoc_y)
            try:
                if gripperLoc_x > slider4_value:
                    servo_1, servo_2 = calculate_arm_angles(gripperLoc_x, gripperLoc_y)
                    servo_2 = 180 - servo_1
                else:
                    servo_1, servo_2 = calculate_arm_angles(gripperLoc_x, gripperLoc_y)
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
            except:
                print("Math err")
            gripperLoc_x = slider4_value
            gripperLoc_y = slider5_value

        # if UpdatePlot: self.update_plot()


    def ObjectAvailable(self):
        global ObjectAvailable, classes, scores

        available = []
        for _ in range(20):
            for i in range(len(classes)):
                class_id = int(classes[i])
                if class_id==43 and scores[i] > 0.5:
                    available.append(True)

            available.append(False)

        ObjectAvailable = max(available, key=available.count)
        # print(available)


    def getGripPos(self):
        global targetDoneCount, getGripPos, object_distance, servo_cam
        global boxes, classes, scores

        # print(scores)
        # print(classes)

        for i in range(len(scores)):
            class_id = int(classes[i])
            if (int(class_id)==43 and scores[i] > 0.6):
                ymin = int(max(1,(boxes[i][0] * 360)))
                xmin = int(max(1,(boxes[i][1] * 640)))
                ymax = int(min(360,(boxes[i][2] * 360)))
                xmax = int(min(640,(boxes[i][3] * 640)))

                left, top, right, bottom = xmin, ymin, xmax, ymax
        #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        # results = self.model.predict(frame, verbose=False)[0]

        # detections = []
        # for r in results.boxes.data.tolist():
        #     x1, y1, x2, y2, score, class_id = r
        #     # if(class_id == 1):
        #     x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        #     detections.append([[x1, y1, x2, y2], score, class_id])
        #     cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 3)

        # tracked = self.tracker.update_tracks(detections, frame=frame)
        
        # for track in tracked:   
        #         if not track.is_confirmed():
        #             continue
        #         class_id = int(track.track_id)
        #         color = self.colors[class_id % len(self.colors)]
                
        #         left, top, right, bottom = map(int, track.to_ltwh(orig=True))

        # #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

                obj_mid = [int((left+right)/2),int((top+bottom)/2)]

                frame_width_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
                frame_height_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

                errorX = (obj_mid[0] - frame_width_mid)
                errorY = (frame_height_mid - obj_mid[1])

                finalErr_x = self.kp_cam[0] * errorX
                finalErr_y = self.kp_cam[1] * errorY

                servo_cam_ = servo_cam - round(finalErr_x)
                if servo_cam_ < 0: servo_cam_ = 0
                if servo_cam_ > 180: servo_cam_ = 180
                
                self.slider1.setValue(servo_cam_)

                if (-0.4 < finalErr_x < -0.2 or 0.2 < finalErr_x < 0.4):
                    self.SendData(f"m1_pos:1, #:#\n")
                    print(finalErr_x)
                    sleep(0.05)

                if (-0.2 < finalErr_x < 0.2):
                    targetDoneCount +=1

                if( targetDoneCount > 10 ):
                    while True:
                        Distance = []
                        for _ in range(15):
                            response = self.SendData(f"distance:0, #:#\n", 0)
                            if response['Distance']:
                                Distance.append(int(response['Distance']))
                            sleep(0.02)
                        object_distance = int(np.percentile(Distance, 50))
                        print(object_distance)
                        if object_distance > 35:
                            self.SendData(f"m1_pos:1, #:#\n")
                        else:
                            break

                    print(">>>>>>>>>>> object_distance : ", object_distance)

                    getGripPos = True


    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == Qt.Key_W:
            self.SendData(f"m1_pos:-3,m2_pos:-3, #:#\n")
        elif key == Qt.Key_S:
            self.SendData(f"m1_pos:3,m2_pos:3, #:#\n")
        elif key == Qt.Key_A:
            self.SendData(f"m1_pos:-3,m2_pos:3, #:#\n")
        elif key == Qt.Key_D:
            self.SendData(f"m1_pos:3,m2_pos:-3, #:#\n")


    def closeEvent(self, event):
        self.video_stream.release()
        self.SendData("m_stop:1, #:#\n")
        event.accept()
        try: ser.close()
        except: pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())