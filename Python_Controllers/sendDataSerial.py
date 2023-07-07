import serial
import time

ser = serial.Serial('COM8', 9600)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(2)

command = "m1_pos:100, #:#"
ser.write(command.encode())

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode().rstrip()
        print('Arduino response:', data)
        break

ser.close()