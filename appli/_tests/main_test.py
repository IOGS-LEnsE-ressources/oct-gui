from models.motor_control import *
from _tests.camera_test import *
import numpy as np

exposure = 1500
N = 10
n= 9
delta_z = 0.1

P = Piezo()
size = 3
position_initiale = 2

cam = find_camera()
cam.set_exposure(exposure)

fig, axs = plt.subplots(size, size, figsize=(8, 8))

for i, ax in enumerate(axs.flat):
    if i<n:
        image1 = cam.get_images(N)
        P.set_voltage_piezo(0.2*i+0.02)
        image2 = cam.get_images(N)
        P.set_zero_piezo()

    image = (np.mean(image1, axis=0) - np.mean(image2, axis=0))**2

    max_image = image.max()

    if max_image>0:
        image = abs(image/max_image)

    ax.imshow(image, cmap='gray')

cam.disconnect()
P.disconnect()
plt.show()