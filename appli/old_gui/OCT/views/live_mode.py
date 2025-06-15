if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from lensecam.basler.camera_basler import CameraBasler

from _tests.camera_test import *
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage
import numpy as np
from controllers.camera_control import cameraControl

def find_camera():
    cam = CameraBasler()
    cam_connected = cam.find_first_camera()
    print(cam_connected)
    return cam


class mainWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()

        self.control = cameraControl()
        self.layout = QHBoxLayout()
        self.parent = parent
        self.motor_position = 3.125
        self.timer = None
        self.label = None

        self.control.update_exposure(300)

        self.control.motor.move_motor(self.motor_position)

        self.image1 = None
        self.image2 = None
        self.image = None

    def generate_frame(self, step_size = 0.75, V0 = 0):
        try:
            image1, image2, image = self.control.live_sequence(step_size, V0)
            if image is None:
                return
            image = self.convertTo_uint8(image)

            h, w = image.shape
            qimage = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.label.setPixmap(scaled_pixmap)
        
        except Exception as e:
            print(f"Erreur lors de l'affichage de la caméra : {e}")
            self.timer.stop()
            self.label.setText("Erreur : impossible de lire la caméra.")

    def convertTo_uint8(self, image):
        type = image.dtype
        if type == "uint8":
            return image
        image_float32 = image.astype(np.float32)
        image_normalized = (image_float32 - np.min(image_float32)) / (
                np.max(image_float32) - np.min(image_float32) + 1e-8)
        image_uint8 = (image_normalized * 255).astype(np.uint8)
        return image_uint8

    def get_live_sequence(self, N, step_size, V0):
        image1, image2, image = self.control.acquisition_sequence(N, step_size, V0)
        if image is None:
            print(f"Pas d'image détectée")
            return
        self.image1 = self.convertTo_uint8(image1)
        self.image2 = self.convertTo_uint8(image2)
        self.image = self.convertTo_uint8(image)

    def if_main_video(self):
        self.label = QLabel("Initialisation")
        self.label.setMinimumSize(320, 240)
        self.layout.addWidget(self.label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_frame)
        self.timer.start(33)

        self.setLayout(self.layout)

    def set_pixmap(self, image, label):
        h, w = image.shape
        qimage = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)

    def get_acquisition_sequence(self, zstep, z0, vstep, V0, Nimg, i, Nstep, tol = 0.3, timeout = 300):
        image1, image2, image = self.control.store_acquisition_sequence(Nimg, zstep, z0, vstep, V0, i, Nstep, z0, tol, timeout)
        if image is None:
            print(f"Pas d'image détectée")
            return
        self.image1 = self.convertTo_uint8(image1)
        self.image2 = self.convertTo_uint8(image2)
        self.image = self.convertTo_uint8(image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = mainWidget()
    widget.if_main_video()
    widget.show()
    sys.exit(app.exec())