import cv2
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.css import *

if __name__ == '__main__':
    MIN_EXPO_VALUE = 50
    EXPOSURE = 1500
    MAX_EXPO_VALUE = 4000

class CameraParamsView(QWidget):

    camera_exposure_changed = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.setWindowTitle("Paramètres Caméra")
        self.parent = parent  # main_app

        layout = QVBoxLayout()
        layout_int_time = QHBoxLayout()
        layout_num = QHBoxLayout()

        self.min_expo_value = int(self.parent.min_expo_value)
        self.ini_expo_value = int(self.parent.ini_expo_value)
        self.max_expo_value = int(self.parent.max_expo_value)
        self.number_avgd_images = int(self.parent.number_avgd_images)

        self.title = QLabel("Camera / Images")
        self.title.setStyleSheet(styleH2)

        self.int_time_label = QLabel("Exposure time : ")
        self.int_time_label.setStyleSheet(styleH3)
        self.int_time_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.int_time_value = QLabel(f"{self.ini_expo_value} us")
        self.int_time_value.setStyleSheet(styleH3)
        self.int_time_value.setFixedWidth(50)  # largeur fixe pour garder l'alignement stable
        self.int_time_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout_int_time.addWidget(self.int_time_label)
        layout_int_time.addWidget(self.int_time_value)

        self.num_label = QLabel("Number of images (mean) : ")
        self.num_label.setStyleSheet(styleH3)
        self.num_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.num_value = QLineEdit(str(self.number_avgd_images))
        self.num_value.setEnabled(True)
        self.num_value.editingFinished.connect(self.update_num)

        layout_num.addWidget(self.num_label)
        layout_num.addWidget(self.num_value)

        # Créer un slider horizontal
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(self.min_expo_value)
        self.slider.setMaximum(self.max_expo_value)
        self.slider.setValue(self.ini_expo_value)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(int((self.max_expo_value - self.min_expo_value)/20))
        self.slider.valueChanged.connect(self.update_slider)

        # Ajouter le slider au layout
        layout.addWidget(self.title)
        layout.addLayout(layout_int_time)
        layout.addWidget(self.slider)
        layout.addLayout(layout_num)
        layout.addSpacing(40)

        # Appliquer le layout à la fenêtre
        self.setLayout(layout)

        #self.camera_exposure_changed.emit("int=" + str(self.ini_expo_value))

    def update_slider(self, tint):
        self.int_time_value.setText(str(tint) + " us")
        if __name__ == "__main__":
            print("integration time changed")
        self.camera_exposure_changed.emit("int=" + str(tint))

    def update_num(self):
        if __name__ == "__main__":
            print("Number of averaged images changed")
        self.camera_exposure_changed.emit("num=" + self.num_value.text())

    def moderate_interactions(self, activation : bool):
        self.int_time_value.setEnabled(activation)
        self.slider.setEnabled(activation)
        self.num_value.setEnabled(activation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = CameraParamsView(MIN_EXPO_VALUE, EXPOSURE, MAX_EXPO_VALUE)
    fenetre.show()
    sys.exit(app.exec())