import serial
import time

ser = serial.Serial('COM10', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(2)

command = "servo_cam:180,distance:5, #:#\n"
ser.write(command.encode())

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode().rstrip()
        print(data)
        break

ser.close()