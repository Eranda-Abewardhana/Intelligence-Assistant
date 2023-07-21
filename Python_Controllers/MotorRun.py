import serial
import time

ser = serial.Serial('/dev/ttyACM0', 115200)  # Replace '/dev/ttyUSB0' with the appropriate port

Slope1 = 4.498256643245813
Intercept1 = 2.6

Slope2 = 4.460188933873144
Intercept2 = -4.5

def angle_to_motor1(angle):
    return Slope1*angle + Intercept1

def angle_to_motor2(angle):
    return Slope2*angle + Intercept2

time.sleep(1)

arr = [[-400 ,0, 0]] #[m1,m2,delay] 100-23, 300-69
# arr = [[400, 400, 2] ]
# Off Position : servo_base:100, servo_1:78, ser

def move(m1_angle, m2_angle):
    m1 = angle_to_motor1(m1_angle)
    m2 = angle_to_motor2(m2_angle)
    # m1 = -m1 if m1_angle<0 else m1
    # m2 = -m2 if m2_angle<0 else m2

    command = f"m1_pos:{m1_angle},m2_pos:{m2_angle}, #:#\n"
    ser.write(command.encode())

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode().rstrip()
            print(data)
            break
        # time.sleep(0.0005)

for item in arr:
    move(item[0], item[1])
    time.sleep(item[2])

ser.close()