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
from controllers import MotCam_control
from controllers.MotCam_control import cameraControl


class liveWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__()

        self.control = cameraControl()
        self.layout = QHBoxLayout()
        self.parent = parent
        self.motor_position = 3.09
        self.timer = None
        self.label = None

        self.control.update_exposure(300)

        self.control.motor.move_motor(self.motor_position)

        self.image1 = None
        self.image2 = None
        self.image = None

    def generate_frame(self, step_size = 1.25, V0 = 12):
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
        if type == "float16":
            image_float32 = image.astype(np.float32)
        elif type == "float32":
            image_float32 = image
        image_normalized = (image_float32 - np.min(image_float32)) / (
                np.max(image_float32) - np.min(image_float32) + 1e-8)
        image_uint8 = (image_normalized * 255).astype(np.uint8)
        return image_uint8

    def get_live_sequence(self, step_size, V0):
        image1, image2, image = self.control.live_sequence(step_size, V0)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = liveWidget()
    widget.if_main_video()
    widget.show()
    sys.exit(app.exec())