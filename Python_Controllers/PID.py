import time
import serial
import urllib.request
#defines function and_ classes which help in opening urls
#url handling module for python
root_url = "http://192.168.137.44"

# PID constants
kp = 1  # Proportional gain
ki = 0  # Integral gain
kd = 0  # Derivative gain

target_speed = 150.0  # Desired motor speed
measured_speed = 0.0  # Measured motor speed

error_sum = 0.0  # Cumulative error
last_error = 0.0  # Last error
last_time = 0  # Last time update occurred

errorX = 1200

def sendRequest(url):
	n = urllib.request.urlopen(url) # send request to ESP

# Main loop
while True:
   
    current_time = time.time()
    elapsed_time = current_time - last_time

        # PID calculations
    error_sum += errorX * elapsed_time
    d_error = (errorX - last_error) / elapsed_time

        # PID output
    output = kp * errorX + ki * error_sum + kd * d_error

    request = f"{root_url}/?err={output}&m_init=10"
    sendRequest(request)

    time.sleep(0.1)  # Delay for a short period
