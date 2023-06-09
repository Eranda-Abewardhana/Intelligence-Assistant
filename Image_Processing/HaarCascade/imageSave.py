import cv2
import os
import time

myPath = "Haar Cascade/images/image_"
cameraBrightness = 190
minBlur = 20
graylmage = False
saveData = True
showlmage = True
imgWidth = 640
imgHeight = 480
countSave = 0

countFolder = 0
cap = cv2.VideoCapture(0) # CAM
cap.set(3, 640)
cap.set(4, 480)
cap.set(10, cameraBrightness)


def saveData():
    global countFolder
    countFolder = 0
    while os.path.exists(myPath+str(countFolder)):
        countFolder = countFolder + 1
    os.makedirs(myPath + str(countFolder))

if saveData: saveData()

while True:
    success, img = cap.read()
    img = cv2. resize(img, (imgWidth, imgHeight))
    if graylmage : img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if saveData and (cv2.waitKey(1) & 0xFF) == 32:
        blur = cv2.Laplacian(img, cv2.CV_64F).var()
        if blur > minBlur:
            nowTime = time.time()       
            cv2.imwrite(f'{myPath + str(countFolder)}/{countSave}_{int(blur)}_{nowTime}.png', img)
            countSave += 1
            print("saved ", countSave)
        else:
            print("Not Focusing Cam")

    if showlmage:
        cv2.imshow("Image", img)
                   
    if(cv2.waitKey(30) == 27): break

cap.release()
cv2.destroyAllWindows()