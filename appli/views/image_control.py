import cv2
import numpy as np
import sys
import time
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QSizePolicy, QHBoxLayout, QApplication, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal

class ImageControlView(QWidget):

    image_changed = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle("Paramètres image OCT")

        self.pixel_intensity_list = ['1', '2', '4', '8', '16']

        layout = QVBoxLayout()

        pixel_layout = QHBoxLayout()

        self.title = QLabel("OCT Image Display")
        self.title.setStyleSheet(styleH2)
        ### Pixel intensity factor

        self.pixel_int_label = QLabel("Pixel Intensity Factor")
        self.pixel_int_label.setStyleSheet(styleH3)
        self.pixel_int_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        # ComboBox for factor values
        self.combo_factor = QComboBox(self)
        self.combo_factor.addItems(self.pixel_intensity_list)
        self.combo_factor.currentTextChanged.connect(self.factor_changed)

        pixel_layout.addWidget(self.pixel_int_label)
        pixel_layout.addWidget(self.combo_factor)

        # Check box For log display
        self.check_log = QCheckBox("Log Display")
        self.check_log.stateChanged.connect(self.log_selected)

        layout.addWidget(self.title)
        layout.addLayout(pixel_layout)
        layout.addWidget(self.check_log)
        self.setLayout(layout)

    def factor_changed(self, text):
        print(f"Value : {text}")
        self.image_changed.emit("IntFactor=" + text)

    def log_selected(self, text):
        if self.check_log.isChecked():
            self.image_changed.emit("Log=1")
            self.combo_factor.setEnabled(False)
        else:
            self.image_changed.emit("Log=0")
            self.combo_factor.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = ImageControlView()
    fenetre.show()
    sys.exit(app.exec())