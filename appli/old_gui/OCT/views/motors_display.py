import cv2
import numpy as np
import sys
import time
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QFrame,
    QSizePolicy, QSpacerItem, QMainWindow, QHBoxLayout, QApplication, QSlider, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal

class MotorControlView(QWidget):

    motThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.parent = parent
        self.setWindowTitle("Contrôle Moteur")
        self.Z = 2 # self.parent.stepper_init_value

        layout = QVBoxLayout()

        stepper_layout = QHBoxLayout()
        step_z_layout = QHBoxLayout()
        piezo_layout = QHBoxLayout()
        step_v_layout = QHBoxLayout()

        self.title = QLabel("Stepper Motor Control")
        self.title.setStyleSheet(styleH2)
        ### Direction du moteur

        self.stepper_label = QLabel("Stepper Motor")
        self.stepper_label.setStyleSheet(styleH3)
        self.stepper_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        self.stepper_down = QPushButton("DOWN")
        self.stepper_down.setStyleSheet("""
                            QPushButton {
                                background-color: #ee0000; 
                                color: white;                
                                border-radius: 5px;
                                padding: 8px 16px;
                            }
                            QPushButton:hover {
                                background-color: #ce0000;
                            }
                            QPushButton:pressed {
                                background-color: #ae0000;
                            }
                        """)
        self.stepper_down.clicked.connect(self.motor_action)

        self.stepper_up = QPushButton("UP")
        self.stepper_up.setStyleSheet("""
                            QPushButton {
                                background-color: #ee0000; 
                                color: white;                
                                border-radius: 5px;
                                padding: 8px 16px;
                            }
                            QPushButton:hover {
                                background-color: #ce0000;
                            }
                            QPushButton:pressed {
                                background-color: #ae0000;
                            }
                        """)
        self.stepper_up.clicked.connect(self.motor_action)

        stepper_layout.addWidget(self.stepper_label)
        stepper_layout.addWidget(self.stepper_down, alignment = Qt.AlignmentFlag.AlignCenter)
        stepper_layout.addWidget(self.stepper_up, alignment = Qt.AlignmentFlag.AlignCenter)

        ### Pas en z du moteur

        self.step_z_label = QLabel("Pas \u0394z (\u03bcm) : ")
        self.step_z_label.setStyleSheet(styleH3)
        self.step_z_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        init_value = 100 # self.parent.stepper_step
        self.step_z_section = QLineEdit(f"{init_value}")
        self.step_z_section.setEnabled(True)
        self.step_z_section.setFixedWidth(50)
        self.step_z_section.editingFinished.connect(self.motor_action)

        self.z_value = QLabel(f"Z = {self.Z} mm")
        self.z_value.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        step_z_layout.addWidget(self.step_z_label)
        step_z_layout.addWidget(self.step_z_section, alignment= Qt.AlignmentFlag.AlignLeft)
        step_z_layout.addWidget(self.z_value, alignment=Qt.AlignmentFlag.AlignCenter)


        self.piezo_title = QLabel("Piezo Parameters")
        self.piezo_title.setStyleSheet(styleH2)
        ### Valeur tension Piezo

        self.v0_section = QLabel("Piezo Motor - V0 (V) : ")
        self.v0_section.setStyleSheet(styleH3)
        self.v0_section.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        init_value = 0 # self.parent.piezo_V0
        self.v0_value = QLabel(f"{init_value}")
        self.v0_value.setFixedWidth(50)

        # Créer un slider horizontal
        """self.slider_v0 = QSlider(Qt.Orientation.Horizontal)
        self.slider_v0.setMinimum(0)
        self.slider_v0.setMaximum(75)
        self.slider_v0.setValue(int(init_value))
        self.slider_v0.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_v0.setTickInterval(5)

        self.slider_v0.valueChanged.connect(self.piezoAction)"""

        #L'indication de V0 n'est pas utile

        piezo_layout.addWidget(self.v0_section)
        piezo_layout.addWidget(self.v0_value, alignment = Qt.AlignmentFlag.AlignLeft)

        ### Valeur pas en tension
        self.delta_v_section = QLabel("Step \u0394V : ")
        self.delta_v_section.setStyleSheet(styleH3)
        self.delta_v_section.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        init_value = 10 # self.parent.piezo_step_size
        self.delta_v_value = QLineEdit(f"{init_value}")
        self.delta_v_value.setFixedWidth(50)
        self.delta_v_value.editingFinished.connect(self.motor_action)

        step_v_layout.addWidget(self.delta_v_section)
        step_v_layout.addWidget(self.delta_v_value, alignment = Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.title)
        layout.addLayout(stepper_layout)
        layout.addLayout(step_z_layout)
        layout.addSpacing(20)
        layout.addWidget(self.piezo_title)
        layout.addLayout(piezo_layout)
        #layout.addWidget(self.slider_v0)
        layout.addLayout(step_v_layout)
        layout.addSpacing(80)

        self.setLayout(layout)

    def changeZ(self, Z):
        self.Z = Z
        self.z_value.setText(f"Z = {Z} \u03bcm")

    def motor_action(self):
        sender = self.sender()
        if sender == self.stepper_down:
            self.motThread.emit("down=")
            if __name__ == "__main__":print(f"the stepper motor position has been updated")
        elif sender == self.stepper_up:
            self.motThread.emit("up=")
            if __name__ == "__main__":print(f"the stepper motor position has been updated")
        elif sender == self.step_z_section:
            self.motThread.emit("stepz=" + self.step_z_section.text())
            if __name__ == "__main__":print(f"the motor's z-axis step size has been updated")
        elif sender == self.delta_v_value:
            self.motThread.emit("deltaV=" + self.delta_v_value.text())

    def piezoAction(self):
        sender = self.sender()
        if sender == self.slider_v0:
            self.motThread.emit("V0=" + str(self.slider_v0.value()))
            self.v0_value.setText(f'{self.slider_v0.value()} V')
            if __name__ == "__main__":print(f"the tension value of the piezo actuator has been updated")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MotorControlView()
    fenetre.show()
    sys.exit(app.exec())