import cv2
import numpy as np
import serial
import random
from time import time,sleep
from deep_sort_realtime.deepsort_tracker import DeepSort
from threading import Thread
from tensorflow.lite.python.interpreter import Interpreter  

errorX = 0
kp = 3  # Proportional gain
ki = 0.0  # Integral gain
kd = 0.0  # Derivative gain

last_time = 0  # Last time update occurred
error_sum = 0.0  # Cumulative error
last_error = 0.0  # Last error

ser = serial.Serial('/dev/ttyACM0', 9600)

class VideoStream:
    def __init__(self,resolution=(640,480),framerate=30):
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

def SendData(data, value):
    dataStr = f"{data}:{value}, ##:0"
    ser.write(dataStr.encode())
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().rstrip()
            print("Response:\n\t", data)
            break
def UltrasonicData():
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().rstrip()
            print(data,"\tResponse:\n")
            delimiterIndex = data.find('distance(cm): ')
            if delimiterIndex != -1:
                value = receivedString[delimiterIndex + 1:].strip()
                distance = int(value)
                print('distance(cm): ' + distance)
                if(distance < 20) :
                    Thread(target=SendData, args=("m_stop", 1)).start()
            break

# Start the UltrasonicData function in a separate thread
ultrasonic_thread = Thread(target=UltrasonicData)
ultrasonic_thread.start()

min_conf_threshold = float(0.5)
imW, imH = 640,360

PATH_TO_CKPT = "Image_Processing/TF_Lite/NEW/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29/detect.tflite"
PATH_TO_LABELS = "Image_Processing/TF_Lite/NEW/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29/labelmap.txt"

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

if labels[0] == '???':
    del(labels[0])

interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

outname = output_details[0]['name']

if ('StatefulPartitionedCall' in outname):
    boxes_idx, classes_idx, scores_idx = 1, 3, 0
else:
    boxes_idx, classes_idx, scores_idx = 0, 1, 2

frame_rate_calc = 1
freq = cv2.getTickFrequency()

videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
sleep(1)

tracker = DeepSort(max_age=5)
colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]
        

while True:
    t1 = cv2.getTickCount()

    frame1 = videostream.read()

    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0] # Confidence of detected objects

    detections = []
    for i in range(len(scores)):
        if (int(classes[i])==0 and (scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            detections.append([[xmin, ymin, xmax, ymax], scores[i], int(classes[i])])

    tracked = tracker.update_tracks(detections, frame=frame)
    
    for track in tracked:   
        if not track.is_confirmed():
            continue
        track_id = int(track.track_id)
        color = colors[track_id % len(colors)]
        
        x1, y1, x2, y2 = map(int, track.to_ltwh(orig=True))
        obj_mid = [int((x1+x2)/2),int((y1+y2)/2)]

        frame_width_mid = int(videostream.stream.get(cv2.CAP_PROP_FRAME_WIDTH)/2)
        frame_height_mid = int(videostream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)/2)

        errorX = (obj_mid[0] - frame_width_mid)
        errorY = (frame_height_mid - obj_mid[1])
                        
        # print("Change X : ", errorX, " | Change Y : ", errorY)
        cv2.line(frame, (frame_width_mid, frame_height_mid), (obj_mid[0], frame_height_mid), color, 2)
        cv2.line(frame, (frame_width_mid, frame_height_mid), (frame_width_mid, obj_mid[1]), color, 2)
        cv2.putText(frame,f'X:{errorX} | Y:{errorY}',(obj_mid[0],obj_mid[1]),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,255),1)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (color), 3)
        cv2.circle(frame,(obj_mid[0],obj_mid[1]),4,(255,0,0),-1)
        cv2.putText(frame,f'ID : {track_id}',(x1,y1),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)

        current_time = time()
        elapsed_time = current_time - last_time

        error_sum += errorX * elapsed_time
        d_error = (errorX - last_error) / elapsed_time

        finalErr = kp * errorX + ki * error_sum + kd * d_error
        Thread(target=SendData, args=("servo_base", -int(finalErr))).start()
        print(-int(finalErr))

        last_error = errorX
        last_time = current_time


    cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

    cv2.imshow('Object detector', frame)

    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1

    if cv2.waitKey(1) == ord('q'):
        Thread(target=SendData, args=("m_stop", 1)).start()
        ser.close()
        break

cv2.destroyAllWindows()
videostream.stop()
