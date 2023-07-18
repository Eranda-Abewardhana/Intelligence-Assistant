import math
import matplotlib.pyplot as plt


l1=23.75
l2=21.5
x = 25
y = 10

r = math.sqrt(x**2 + y**2)
ang = math.atan2(y, x)

y1 = math.acos((l1**2+l2**2-r**2)/(2*l1*l2))
x1 = ang+math.asin(l2*math.sin(y1)/r)

print(math.degrees(x1),math.degrees(y1))

lx1 = l1 * math.cos(x1)
ly1 = l1 *math.sin(x1)

realY=(-1)*(math.pi-x1-y1)
lx2 = l2 * math.cos(realY)
ly2 = l2 *math.sin(realY)

fig, ax = plt.subplots()
ax.set_aspect('equal')

ax.plot((0,lx1),(0,ly1))
ax.plot((lx1,lx2+lx1),(ly1,ly2+ly1))

ax.scatter(x, y)
plt.show()