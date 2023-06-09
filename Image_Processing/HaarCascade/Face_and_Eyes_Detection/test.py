import cv2
import numpy as np

face_classifier = cv2.CascadeClassifier('Haar Cascade\Computer-Vision-Tutorial-master\Haarcascades\haarcascade_frontalface_default.xml')
eye_classifier = cv2.CascadeClassifier('Haar Cascade\Computer-Vision-Tutorial-master\Haarcascades\haarcascade_eye.xml')

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Failed to open the camera")
    exit()
def empty(x):
    pass

cv2.namedWindow("result")
cv2.createTrackbar("Scale", "result", 50,1000, empty)
cv2.createTrackbar("Neig", "result", 2,20, empty)
cv2.createTrackbar("Min Area", "result", 20000,100000, empty)
cv2.createTrackbar("Brightness", "result", 180,255, empty)

def face_detector(img, size=0.5):
    # Convert image to grayscale
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    scaleVal = 1+(cv2.getTrackbarPos("Scale", "result") / 1000)
    neig = cv2.getTrackbarPos("Neig", "result")

    faces = face_classifier.detectMultiScale2(gray, scaleVal, neig)
    if faces == ():
        return img

    for (x, y, w, h), w1 in zip(faces[0], faces[1]):
        if w1 > min(faces[1])*3:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img,f'W:{w1}',(x,y),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0),1)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            eyes = eye_classifier.detectMultiScale2(gray)
            
            for (ex, ey, ew, eh), w2 in zip(eyes[0], eyes[1]):
                if w2 > min(eyes[1])*3:
                    cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,0,255),2) 
                    cv2.putText(img,f'W:{w2}',(ex,ey),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0),1)
                    
    return img


while True:

    bightness = cv2.getTrackbarPos("Brightness", "result")
    cap.set(10, bightness)

    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break
    
    cv2.imshow('Our Face Extractor', face_detector(frame))
    if cv2.waitKey(1) == 27: #13 is the Enter Key
        break
        
cap.release()
cv2.destroyAllWindows()      