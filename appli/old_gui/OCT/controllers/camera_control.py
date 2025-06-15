from fontTools.merge.util import avg_int

from models.motor_control import *
import numpy as np
from lensecam.basler.camera_basler import CameraBasler, get_bits_per_pixel
import matplotlib.pyplot as plt
import sys
import time

from views import motors_display

from PyQt6.QtWidgets import (
    QWidget, QApplication, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

class cameraControl(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.find_camera()

        if self.camera_connected:
            print(f"la caméra est connectée")
        else:
            print(f"la caméra n'a pas pu être connectée")

        self.exposure = 1500
        self.piezo = Piezo()
        self.motor = Motor()

        self.piezo_flag = self.piezo is not None
        self.motor_flag = self.motor is not None

        self.cam.set_exposure(self.exposure)

    def avg_images(self, N):
        print(N)
        images = self.cam.get_images(int(N))
        return np.mean(images, axis = 0)

    def acquisition_sequence(self, N, step_size, V0):
        self.piezo.set_voltage_piezo(V0)
        image1 = self.avg_images(N)
        self.piezo.set_voltage_piezo(step_size + V0)
        image2 = self.avg_images(N)

        image = np.sqrt((image1 - image2)**2)
        return image1, image2, image

    """def live_sequence(self, N, step_size, V0):
        self.piezo.set_voltage_piezo(V0)
        image1 = self.avg_images(N)
        self.piezo.set_voltage_piezo(step_size + V0)
        image2 = self.avg_images(N)
        image = np.sqrt((image1 - image2) ** 2)
        return image1, image2, image"""

    def acquisition_update(self,consigne, tolerance = 0.1, timeout = 300):
        self.motor.move_motor(consigne)
        a = 0
        while(self.motor.get_position() - consigne > tolerance and a < timeout):
            a+=1
            time.sleep(0.01)

    def store_acquisition_sequence(self, N, z_step_size, z0, v_step_size, V0, index, num, tolerance = 0.1, timeout = 300):
        """
        This function performs the entire measurement sequence of
        the OCT protocol, and returns a list containing the resulting
        images.
        :param z_step_size: motor step size
        :param Z: motor position
        :param v_step_size: piezo step size
        :param V0: piezo voltage
        :param N: number of averaged images
        :param num: number of steps
        :rtype: list
        """
        self.acquisition_update(z0 - num / 2 * z_step_size + index * z_step_size, tolerance, timeout)
        image1, image2, image = self.acquisition_sequence(N, v_step_size, V0)
        return image1, image2, image

    def update_exposure(self, exposure):
        self.exposure = exposure
        self.cam.set_exposure(self.exposure)

    def disconnect(self):
        if self.camera_connected:
            print("Disconnect Camera")
            self.cam.stop_acquisition()
            self.cam.disconnect()
        if self.piezo is not None:
            self.piezo.disconnect_piezo()
        if self.motor is not None:
            self.motor.disconnect_motor()

    def find_camera(self):
        self.cam = CameraBasler()
        self.camera_connected = self.cam.find_first_camera()
        if self.camera_connected:
            self.cam.init_camera()
            self.cam.set_color_mode('Mono12')
            self.cam.set_frame_rate(10)
            self.image_bits_depth = get_bits_per_pixel(self.cam.get_color_mode())
            print(f'Color mode = {self.image_bits_depth}')
            self.cam.start_acquisition()
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No Camera Connected")
            dlg.setText("No Basler Camera is connected to the computer...\n\nThe application will not start "
                        "correctly.\n\nYou will only access to a pre-established data set.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()

    def find_motors(self):
        self.piezo.find_piezo()
        self.motor.find_motor()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    control = cameraControl()
    control.motor.move_motor(3.125)
    control.update_exposure(300)
    fig, axs = plt.subplots(4, 4, figsize=(8, 8))
    control.piezo.set_voltage_piezo(12)
    image1 = control.cam.get_images(5)
    for i, ax in enumerate(axs.flat):
        control.piezo.set_voltage_piezo(12 + 0.1*i)
        image2 = control.cam.get_images(5)

        image = (np.mean(image1, axis=0) - np.mean(image2, axis=0)) ** 2

        #image = np.mean(image2, axis = 0)
        max_image = image.max()

        if max_image > 0:
            image = abs(image / max_image)

        plt.title(f"V = {2*i}")
        ax.imshow(image, cmap= "gray")
    control.disconnect()
    plt.show()