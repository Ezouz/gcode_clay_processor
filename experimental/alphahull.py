import numpy as np
import matplotlib.pyplot as plt
from alpha_shapes import Alpha_Shaper, plot_alpha_shape


# points_2d = [(0., 0.), (0., 1.), (1., 1.), (1., 0.),
#           (0.5, 0.25), (0.5, 0.75), (0.25, 0.5), (0.75, 0.5)]
points_2d=[]
with open("1.point", "r") as file:
    for line in file:
        x, y = map(float, line.strip().split(","))
        points_2d.append((float(x), float(y)))

shaper = Alpha_Shaper(points_2d)
print(shaper)
# Calculate the shape for smaller alpha
alpha = 3.7
alpha_shape = shaper.get_shape(alpha=alpha)

fig, ax1 = plt.subplots()
ax1.scatter(*zip(*points_2d))
plot_alpha_shape(ax1, alpha_shape)
ax1.set_title(f"$\\alpha={alpha:.3}$")
ax1.set_aspect('equal')
plt.show()


