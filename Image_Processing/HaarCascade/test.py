import cv2

cascade_path = "Haar Cascade\cascades\classifier\cascade.xml"

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open the camera")
    exit()

def empty(x):
    pass

cv2.namedWindow("result")
cv2.createTrackbar("Scale", "result", 50,1000, empty)
cv2.createTrackbar("Neig", "result", 4,20, empty)
cv2.createTrackbar("Min Area", "result", 0,100000, empty)
cv2.createTrackbar("Brightness", "result", 180,255, empty)

cascade = cv2.CascadeClassifier(cascade_path)

while True:
    bightness = cv2.getTrackbarPos("Brightness", "result")
    cap.set(10, bightness)

    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    scaleVal = 1+(cv2.getTrackbarPos("Scale", "result") / 1000)
    neig = cv2.getTrackbarPos("Neig", "result")
    objects = cascade.detectMultiScale2(gray, scaleVal, neig) # minSize=(30, 30)
    print(objects)

    for (x, y, w, h), weight in zip(objects[0], objects[1]):
        area = w*h
        minArea = cv2.getTrackbarPos("Min Area", "result")
        if area > minArea:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame,f'Weight : {weight}',(x,y),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,0,0),1)

    cv2.imshow("result", frame)

    if(cv2.waitKey(30) == 27): break

cap.release()
cv2.destroyAllWindows()