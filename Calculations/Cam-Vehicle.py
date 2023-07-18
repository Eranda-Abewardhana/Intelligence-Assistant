import math
import matplotlib.pyplot as plt


distance_arm_cam = 29
angle_cam = 30
object_distance = 10

def calculate_baseAngle(angle_cam, object_distance):
    global distance_arm_cam
    grip_distance = math.sqrt( object_distance**2 + distance_arm_cam**2 - 2*distance_arm_cam*object_distance*math.cos(math.radians(angle_cam+50)) )
    grip_angle = math.degrees( math.asin( object_distance*math.sin(math.radians(angle_cam+50)) / grip_distance ) )
    return grip_distance, grip_angle

grip_distance, grip_angle = calculate_baseAngle(angle_cam, object_distance)

lx1 = grip_distance*math.cos(math.radians(grip_angle))
ly1 = grip_distance*math.sin(math.radians(grip_angle))

lx2 = distance_arm_cam - object_distance*math.cos(math.radians(angle_cam+50))
ly2 = object_distance*math.sin(math.radians(angle_cam+50))


fig, ax = plt.subplots()
ax.set_aspect('equal')

ax.plot((0,lx1),(0,ly1))
ax.plot((distance_arm_cam,lx2),(0,ly2))

ax.scatter(lx1, ly1)
plt.show()