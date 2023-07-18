import cv2
import numpy as np
import math
import serial
import time

# Establish serial connection
ser = serial.Serial('COM10', 115200)
time.sleep(1)

# Create a blank canvas
canvas_width = 1000
canvas_height = 700
canvas = 255 * np.ones((canvas_height, canvas_width, 3), dtype=np.uint8)  # White canvas

# Initial position of the rover
x1 = 500
y1 = 680
img = cv2.circle(canvas, (x1, y1), 5, (0, 0, 255), -1)

# Function to update the map with ultrasonic sensor data and rover position
def update_map(length, angle, x, y):
    global x1, y1, img

    r = length 
    a = angle
    x1 = x
    y1 = y

    # Find the representative points on canvas of the objects (Black)
    x2 = x1 - r * math.sin(a)
    y2 = y1 - r * math.cos(a)
    img = cv2.circle(img, (int(x2), int(y2)), 5, (0, 0, 0), -1)

    # Update the position of the rover (Red)
    img = cv2.circle(img, (int(x1), int(y1)), 5, (0, 0, 255), -1)

    # Display the map
    cv2.imshow("Map for Rover", img)
    cv2.waitKey(1)

def rotate(angle):
    x = 300  # Example x position value
    y = 400  # Example y position value

    command = f"servo_cam:{angle},distance:0, #:#\n"
    ser.write(command.encode())
    string = ""

    while True:
        if ser.in_waiting > 0:
            string = ser.readline().decode().rstrip()
            break
        
    segments = string.split(",")

    key_value_pairs = {}
    for segment in segments:
        colon_index = segment.find(":")
        if colon_index != -1:
            key = segment[:colon_index].strip()
            value = segment[colon_index+1:].strip()
            key_value_pairs[key] = value

    dist1, dist2 = 0, 0
    for key, value in key_value_pairs.items():
        if key == "servo_cam":
            angle = int(value)
        elif key == "Distance":
            dist1 = int(value)
    print(angle, dist1)

    update_map(dist1, angle, x, y)  # Update the map

while True:
    for i in range(1, 180):
        rotate(i)
        time.sleep(0.005)
    for i in range(180, 1, -1):
        rotate(i)
        time.sleep(0.005)

ser.close()  # Close the serial connection
cv2.destroyAllWindows()
