import matplotlib.pyplot as plt
import numpy as np


num = 3
ax = []
ay = []
for i in range(num):
    ay.append([])
plt.ion()
num = 0

while True:
    gen = np.fromfile('gen.bin')
    for i in range(int(len(gen)/21)):
        ay[i].append(gen[i * 21 + 1])
    ax.append(num)
    plt.plot(ax, ay[0], 'r--')
    plt.plot(ax, ay[1], 'b--')
    plt.plot(ax, ay[2], 'g--')
    num += 1
    plt.pause(0.5)
