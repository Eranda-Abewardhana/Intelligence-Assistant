import math
import sys
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

servo_cam, servo_base, servo_grip, servo_1, servo_2 = 30,90,0,120,0

gripperLoc_x, gripperLoc_y = 25,10


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


try: ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace '/dev/ttyACM0' with the appropriate port
except: print("No Serial")

sleep(1)


# # Load the TFLite model
# interpreter = tf.lite.Interpreter("Image_Processing/TF_Lite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29/detect.tflite")
# interpreter.allocate_tensors()
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()


class MainWindow(QMainWindow):
    kp = [0.02, 0.02]  # Proportional gain


    def __init__(self):
        super().__init__()
        global gripperLoc_x, gripperLoc_y, servo_cam, servo_base, servo_grip, servo_1, servo_2

        self.device = 'cuda' if cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = YOLO("yolov8n.pt")
        self.model.fuse()
        self.tracker = DeepSort(max_age=5)
        self.CLASS_NAMES_DICT = self.model.names

        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]

        self.SendData(f"servo_cam:{servo_cam}, #:#\n")

        self.resize(1200, 600)

        self.image_label = QLabel(self)
        self.video_stream = cv2.VideoCapture(1)
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

        self.timer = QTimer()
        self.timer.timeout.connect(self.flow) # type: ignore
        self.timer.start(1)  # (30 FPS)


    def flow(self):
        if not getGripPos:
            self.getGripPos()
            return
        
        if not gripObject:
            self.gripObject()
            return
        
        print("<<<<<<<<<< done >>>>>>>>>>>>")


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


    def gripObject(self):
        global gripObject, servo_cam, object_distance, servo_1, servo_2, servo_base
        try:
            grip_distance, servo_base = calculate_baseAngle(servo_cam, object_distance)
            for angle in range(90, servo_base, -1):
                self.slider2.setValue(angle)
                sleep(0.05)

            for distance in range(5, grip_distance):
                servo_1, servo_2 = calculate_arm_angles(distance, 5)
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
                self.update_plot()
                sleep(0.05)

            servo_grip = 20
            self.slider3.setValue(servo_grip)
            sleep(0.5)

            for distance in range(grip_distance, 5, -1):
                servo_1, servo_2 = calculate_arm_angles(distance, 5)
                servo_2 = 180 - servo_1
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
                self.update_plot()
                sleep(0.05)

            for angle in range(servo_base, 90):
                self.slider2.setValue(angle)
                sleep(0.05)

            gripObject = True
        except:
            print("Math err")


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
        self.ax.set_zlim3d(0, 50)

        self.canvas.draw()


    def sliderChanged(self):
        global servo_cam,servo_base,servo_grip,servo_1,servo_2
        global gripperLoc_x, gripperLoc_y
        
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
                self.SendData(f"servo_1:{servo_1},servo_2:{servo_2}, #:#\n")
            except:
                print("Math err")

        self.update_plot()


    def getGripPos(self):
        global targetDoneCount, getGripPos, object_distance, servo_cam
        ret, frame = self.video_stream.read()
        if ret:
            start_time = time()
            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

            #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # input_shape = input_details[0]['shape']
            # resized_frame = cv2.resize(frame, (input_shape[2], input_shape[1]))

            # if len(input_shape) == 4:
            #     resized_frame = np.expand_dims(resized_frame, axis=0)

            # resized_frame = resized_frame.astype(np.uint8)

            # interpreter.set_tensor(input_details[0]['index'], resized_frame)
            # interpreter.invoke()

            # output_locations = interpreter.get_tensor(output_details[0]['index'])
            # output_classes = interpreter.get_tensor(output_details[1]['index'])
            # output_scores = interpreter.get_tensor(output_details[2]['index'])
            # num_detections = int(output_details[3]['index'])

            # # print(f"Output locations shape: {output_locations.shape}")
            # # print(f"Output classes shape: {output_classes.shape}")
            # # print(f"Output scores shape: {output_scores.shape}")

            # # print(output_classes)

            # for i in range(len(output_classes[0])):
            #     # print(output_classes[0][i])
            #     class_id = int(output_classes[0][i])
            #     score = float(output_scores[0][i])
            #     if score > 0.5:
            #         ymin, xmin, ymax, xmax = output_locations[0][i]
            #         xmin = int(xmin * frame.shape[1])
            #         xmax = int(xmax * frame.shape[1])
            #         ymin = int(ymin * frame.shape[0])
            #         ymax = int(ymax * frame.shape[0])
            #         color = self.colors[class_id % len(self.colors)]

            #         left, top, right, bottom = xmin, ymin, xmax, ymax

            #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            results = self.model.predict(frame, verbose=False)[0]

            detections = []
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                if(class_id == 1):
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    detections.append([[x1, y1, x2, y2], score, class_id])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 3)

            # tracked = self.tracker.update_tracks(detections, frame=frame)
            
            # for track in tracked:   
            #         if not track.is_confirmed():
            #             continue
            #         class_id = int(track.track_id)
            #         color = self.colors[class_id % len(self.colors)]
                    
            #         left, top, right, bottom = map(int, track.to_ltwh(orig=True))

            # #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

            #         obj_mid = [int((left+right)/2),int((top+bottom)/2)]

            #         frame_width_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
            #         frame_height_mid = int(self.video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

            #         errorX = (obj_mid[0] - frame_width_mid)
            #         errorY = (frame_height_mid - obj_mid[1])
                                    
            #         # print("Change X : ", errorX, " | Change Y : ", errorY)
            #         cv2.line(frame, (frame_width_mid, frame_height_mid), (obj_mid[0], frame_height_mid), color, 2)
            #         cv2.line(frame, (frame_width_mid, frame_height_mid), (frame_width_mid, obj_mid[1]), color, 2)
            #         cv2.putText(frame,f'X:{errorX} | Y:{errorY}',(obj_mid[0],obj_mid[1]),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,255),1)

            #         cv2.rectangle(frame, (left, top), (right, bottom), (color), 3)
            #         # cv2.circle(frame,(obj_mid[0],obj_mid[1]),4,(255,0,0),-1)
            #         cv2.putText(frame,f'ID : {class_id}',(left,top),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)


            #         finalErr_x = self.kp[0] * errorX
            #         finalErr_y = self.kp[1] * errorY

            #         servo_cam -= round(finalErr_x)
            #         if servo_cam < 0: servo_cam = 0
            #         if servo_cam > 180: servo_cam = 180
                    
            #         response = self.SendData(f"servo_cam:{servo_cam},distance:0, #:#\n")
            #         if type(response) == 'dict':
            #             object_distance = response['Distance']

            #         self.slider1.setValue(servo_cam)
            #         if (-0.3 < finalErr_x < 0.3):
            #             targetDoneCount +=1
            #             print(finalErr_x)

            #         if( targetDoneCount > 5 ):
            #             getGripPos = True


            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(640, 480, Qt.KeepAspectRatio) # type: ignore
            self.image_label.setPixmap(scaled_pixmap)

            end_time = time()
            fps = round(1/(end_time - start_time), 2)
            # print(f'FPS: {fps}')


    def closeEvent(self, event):
        self.video_stream.release()
        self.timer.stop()
        self.SendData("m_stop:1, #:#\n")
        event.accept()
        try: ser.close()
        except: pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())