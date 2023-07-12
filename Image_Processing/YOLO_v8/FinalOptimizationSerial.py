from torch import cuda
import cv2
from ultralytics import YOLO
import random
from time import time
from deep_sort_realtime.deepsort_tracker import DeepSort
import serial
import math

try: ser = serial.Serial('COM10', 115200)
except: print("No serial")

def calculate_angle_base(angle, distance):
    numerator = float(distance) * math.sin(math.radians(angle))
    denominator = 28 - float(distance) * math.cos(math.radians(angle))
    return round( math.degrees( math.atan( numerator / denominator ) ) , 2)

def calculate_grip_distance(angleCam, angleBase, distance):
    return round( float(distance) * math.sin(math.radians(angleCam)) / math.sin(math.radians(angleBase)), 2)

k1 = 23.75
k2 = 21.5
k3 = 20

def calculate_arm_xy(a):
    part1 = math.asin( (k1**2 - k2**2 + k3**2 + a**2) / (2 * k1 * math.sqrt(k3**2 + a**2)) )
    part2 = math.asin( k3 / math.sqrt(k3**2 + a**2) )
    servo1 = part1 - part2
    numerator = k1 * math.cos(servo1) - k3
    denominator = k2
    servo2 = math.acos(numerator / denominator) - servo1
    servo1 = int( math.degrees(servo1) )
    servo2 = int( math.degrees(servo2) )
    return servo1,servo2


class ObjectDetection:

    kp = [0.02, 0.02]  # Proportional gain
    ki = [0.0, 0.0]  # Integral gain
    kd = [0.0, 0.0]  # Derivative gain

    last_time = 0  # Last time update occurred
    error_sum_x = 0.0  # Cumulative error
    last_error_x = 0.0  # Last error
    error_sum_y = 0.0  # Cumulative error
    last_error_y = 0.0  # Last error

    servoCam_pos = 30

    def __init__(self, videoCapture=1, windowResolution=480):
        self.capture_index = videoCapture
        self.device = 'cuda' if cuda.is_available() else 'cpu'
        print("Using Device: ", self.device)
        self.model = self.load_model()
        self.tracker = DeepSort(max_age=5)
        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]
        self.CLASS_NAMES_DICT = self.model.names
        self.setCap(windowResolution)
        self.SendData(f"servo_cam:{self.servoCam_pos}, #:#\n")
    
    def setCap(self, res):
        self.cap = cv2.VideoCapture(self.capture_index)
        assert self.cap.isOpened()
        width = 320 if res==240 else 640 if res==360 else 1280 if res==720 else 720
        print(f'Using Resolution : {res}x{width}')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res)

    def load_model(self):
        model = YOLO("yolov8n.pt")
        model.fuse()
        return model

    def predict(self, frame, show=False):
        results = self.model.predict(frame, show, verbose=False)
        return results[0]

    def exit(self):
        self.cap.release()
        cv2.destroyAllWindows()

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

    def gripper_run(self):
        while True:
            start_time = time()
            rect, frame = self.cap.read()
            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            results = self.predict(frame)

            detections = []
            for r in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = r
                if(class_id == 39):
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

                frame_width_mid = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
                frame_height_mid = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

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
                # Thread(target=SendData, args=("servo_base", -int(finalErr))).start()
                self.servoCam_pos -= finalErr_x
                if self.servoCam_pos < 0: self.servoCam_pos = 0
                if self.servoCam_pos > 180: self.servoCam_pos = 180
                
                self.SendData(f"servo_cam:{self.servoCam_pos}, #:#\n")
                # print(-int(finalErr))

                if (finalErr_x < 0.3):
                    return finalErr_x

                self.last_error_x = errorX
                self.last_error_y = errorY
                self.last_time = current_time

            end_time = time()
            fps = round(1/(end_time - start_time), 2)
            print(f'FPS: {fps}')

            cv2.imshow("RGB", frame)
            if(cv2.waitKey(30) == 27):
                self.SendData("m_stop:1, #:#\n")
                try: ser.close()
                except: pass
                break

    
detector = ObjectDetection(videoCapture = 0, windowResolution = 480)

final_x_err = detector.gripper_run()
detector.exit()

response = detector.SendData(f"distance:0, #:#\n")
distance = response['Distance']

angleCam = int(180-((134-detector.servoCam_pos)*17/18))
angleBase = calculate_angle_base(angleCam, distance)
print("AngleCam : ", angleCam, " | Distance : ", distance)

servoBase_pos = 85 - angleBase
if servoBase_pos < 5: servoBase_pos = 5
response = detector.SendData(f"servo_base:{servoBase_pos}, #:#\n")
print(response)

gripDistance = calculate_grip_distance(angleCam, angleBase, distance)
print("Grip Distance", gripDistance)

servo1, servo2 = calculate_arm_xy(gripDistance)
response = detector.SendData(f"servo_1:{servo1+20},servo_2:{servo2+30}, #:#\n")
print(response)
