import cv2
from ultralytics import YOLO

'''
- http://192.168.x.x/status
- http://192.168.x.x/control?var=VARIABLE_NAME&val=VALUE
- http://192.168.1.52:81/stream
'''

# URL = "http://192.168.137.122"

# cap = cv2.VideoCapture(URL + ":81/stream")
# cap.set(3, 640)
# cap.set(4, 480)


cap = cv2.VideoCapture(0)

model = YOLO("yolov8n.pt")

while True:
    ret, frame = cap. read()
    cv2.imshow("Test", frame)

    # results = model.predict(frame, show=True)
    
    result = model(frame)

    if(cv2.waitKey(30) == 27):
        break