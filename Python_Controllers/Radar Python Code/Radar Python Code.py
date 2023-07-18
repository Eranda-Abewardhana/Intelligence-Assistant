from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import serial
import time

# Establish serial connection
ser = serial.Serial('COM10', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=2)

# Create the plot figure
fig = plt.figure(facecolor='w')
fig.canvas.toolbar.pack_forget()
fig.canvas.manager.set_window_title('Ultrasonic Radar Plot')
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')

# Add a polar subplot to the figure
ax = fig.add_subplot(1, 1, 1, polar=True, facecolor='#000000')

# Set tick colors
ax.tick_params(axis='both', colors='blue')

# Set the maximum radius of the plot
r_max = 100.0
ax.set_ylim([0.0, r_max])

# Set the angle limits to a half circle
ax.set_xlim([0.0, np.pi])

# Adjust the subplot position
ax.set_position([-0.05, -0.05, 1.1, 1.05])

# Set radial ticks for distance markers
ax.set_rticks(np.linspace(0.0, r_max, 5))

# Set angular ticks for angle markers
ax.set_thetagrids(np.linspace(0, 360, 15))

# Add gridlines with green color and transparency
ax.grid(color='green', alpha=0.4)

# Generate angles in degrees from 0 to 180 with a step of 1
angles = np.arange(0, 361, 1)

# Convert angles to radians
theta1 = angles * (np.pi / 180.0)
theta2 = angles * (np.pi / 180.0) + np.pi

# Create an empty plot object for data points
pols, = ax.plot([], linestyle='', marker='o', markerfacecolor='r',
                markeredgecolor='w', markeredgewidth=0, markersize=3.0,
                alpha=0.9)

# Create an empty plot object for a line from the center to a distance point
line1, = ax.plot([], color='green', linewidth=2.0)
line2, = ax.plot([], color='green', linewidth=2.0)

# Draw the initial plot
fig.canvas.draw()

# Initialize an array to store distance values for each angle
dists1 = np.ones((len(angles),))
dists2 = np.ones((len(angles),))

# Show the figure
fig.show()

# Blit the figure canvas to optimize rendering
fig.canvas.blit(ax.bbox)
fig.canvas.flush_events()

# Copy the background of the axes for efficient restoration
axbackground = fig.canvas.copy_from_bbox(ax.bbox)

def rotate(angle):
    try:
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

        dist1,dist2 = 0,0
        for key, value in key_value_pairs.items():
            if key=="servo_cam":
                angle = value
            elif key=="Distance":
                dist1 = value
                dist2 = value
        print(angle, dist1)

        # Update the distance value for the corresponding angle
        dists1[int(angle)] = dist1
        dists2[int(angle)] = dist2

        # Restore the background of the axes
        fig.canvas.restore_region(axbackground)
        
        # Update the data points on the polar plot
        # Redraw the data points on the polar plot
        pols.set_data(theta1, dists1)
        # ax.draw_artist(pols)
        
        pols.set_data(theta2, dists2)
        ax.draw_artist(pols)

        # Draw a line from the center to the distance point
        line1.set_data(np.repeat((angle * (np.pi / 180)), 2), np.linspace(0.0, r_max, 2))
        line2.set_data(np.repeat((angle * (np.pi / 180)) + np.pi, 2), np.linspace(0.0, r_max, 2))
        
        # Redraw the line on the polar plot
        ax.draw_artist(line1)
        ax.draw_artist(line2)
        
        # Blit the figure canvas to optimize rendering
        fig.canvas.blit(ax.bbox)
        fig.canvas.flush_events()

    except:
        pass

while True:
    for i in range(1,180):
        rotate(i)
        time.sleep(0.005)
    for i in range(180,1,-1):
        rotate(i)
        time.sleep(0.005)