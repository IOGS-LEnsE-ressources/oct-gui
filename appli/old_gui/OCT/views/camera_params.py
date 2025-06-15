import cv2
import numpy as np
import sys
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from lensepy.css import *

MIN_EXPO_VALUE = 50
MAX_EXPO_VALUE = 4000

class CameraParamsView(QWidget):

    #camera_exposure_changed = pyqtSignal(str)
    camThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.setWindowTitle("Paramètres Caméra")
        self.parent = parent  # main_app

        layout = QVBoxLayout()
        layout_int_time = QHBoxLayout()
        layout_num = QHBoxLayout()

        self.title = QLabel("Camera / Images")
        self.title.setStyleSheet(styleH2)

        self.int_time_label = QLabel("Exposure time : ")
        self.int_time_label.setStyleSheet(styleH3)
        self.int_time_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        '''
        if self.parent.camera_connected:
            init_value = self.parent.camera.get_exposure()
        else:
            init_value = 0
        '''
        self.int_time_value = QLabel(f"100 us")
        self.int_time_value.setStyleSheet(styleH3)
        self.int_time_value.setFixedWidth(50)  # largeur fixe pour garder l'alignement stable
        self.int_time_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout_int_time.addWidget(self.int_time_label)
        layout_int_time.addWidget(self.int_time_value)

        self.num_label = QLabel("Number of images (mean) : ")
        self.num_label.setStyleSheet(styleH3)
        self.num_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        init_value = 5 #self.parent.number_avgd_images
        self.num_value = QLineEdit(str(init_value))
        self.num_value.setEnabled = True
        self.num_value.editingFinished.connect(self.update_num)

        layout_num.addWidget(self.num_label)
        layout_num.addWidget(self.num_value)

        # Créer un slider horizontal
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(MIN_EXPO_VALUE)
        self.slider.setMaximum(MAX_EXPO_VALUE)
        if MIN_EXPO_VALUE <= init_value <= MAX_EXPO_VALUE:
            self.slider.setValue(init_value)
        else:
            self.slider.setValue(MIN_EXPO_VALUE)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)

        self.slider.valueChanged.connect(self.update_slider)

        # Ajouter le slider au layout
        layout.addWidget(self.title)
        layout.addLayout(layout_int_time)
        layout.addWidget(self.slider)
        layout.addLayout(layout_num)
        layout.addSpacing(40)

        # Appliquer le layout à la fenêtre
        self.setLayout(layout)

    def update_slider(self, tint):
        self.int_time_value.setText(str(tint) + " us")
        if __name__ == "__main__":
            print("integration time changed")
        self.camThread.emit("int=" + str(tint))

    def update_num(self):
        if __name__ == "__main__":
            print("Number of averaged images changed")
        self.camThread.emit("num=" + self.num_value.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = CameraParamsView()
    fenetre.show()
    sys.exit(app.exec())