import serial
import time

ser = serial.Serial('COM10', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port

time.sleep(1)

arr = [[200, -200, 2], [300, 300, 2], [-200, 200, 2], [400, 400, 2]] #[m1,m2,delay]
# arr = [[400, 400, 2],[400, 400, 2] ]
# Off Position : servo_base:100, servo_1:78, servo_2:26

def move(m1_pos, m2_pos):
    command = f"m1_pos:{m1_pos},m2_pos:{m2_pos}, #:#\n"
    ser.write(command.encode())

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().rstrip()
            print(data)
            break

for item in arr:
    move(item[0], item[1])
    time.sleep(item[2])

ser.close()