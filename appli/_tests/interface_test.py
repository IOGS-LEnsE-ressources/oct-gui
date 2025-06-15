from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QSplitter, QStackedWidget, QApplication, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
import sys, os
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from views.acquisition import AcquisitionView
from views.camera_params import CameraParamsView
from views.images import ImageDisplayGraph
from views.live_mode import liveWidget
from views.motors_display import MotorControlView
import numpy as np


class MainWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self.parent = parent

        self.camera = CameraParamsView(self)
        self.acq = AcquisitionView(self)
        self.motors = MotorControlView(self)

        self.numberOfAvgdImages = self.camera.num_value
        self.z_step = float(self.motors.step_z_section.text())*0.001
        self.v_step = float(self.motors.delta_v_value.text())

        self.image_graph = ImageDisplayGraph(self, '#404040')
        self.live_widget = liveWidget()

        self.live_widget.get_live_sequence(int(self.camera.num_value.text()), float(self.motors.delta_v_value.text()), float(self.motors.v0_value.text()))

        self.image1_widget = ImageDisplayGraph(self, bg_color='#909090')
        self.image1_widget.set_image_from_array(np.array(self.live_widget.image1), "image1")
        self.image2_widget = ImageDisplayGraph(self, bg_color='#909090')
        self.image2_widget.set_image_from_array(np.array(self.live_widget.image2), "image2")
        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_splitter.addWidget(self.image1_widget)
        self.top_splitter.addWidget(self.image2_widget)

        self.image_widget = ImageDisplayGraph(self, bg_color='#404040')
        self.image_widget.set_image_from_array(np.array(self.live_widget.image), "image2")

        # Zone dynamique pour image ou live
        self.stack = QStackedWidget()
        self.stack.addWidget(self.image_widget)  # index 0
        self.stack.addWidget(self.image_graph)  # index 1
        self.stack.setCurrentIndex(0)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.stack)
        self.main_splitter.setSizes([230,500])

        #self.start.clicked.connect(self.button_action)
        #self.stop.clicked.connect(self.button_action)

        self.layout = QGridLayout()

        """self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)
"""
        self.setLayout(self.layout)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)

        # Configuration des lignes
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)

        self.layout.addWidget(self.camera, 0, 0)
        self.layout.addWidget(self.acq, 1, 0)
        self.layout.addWidget(self.motors, 2, 0)

        self.layout.addWidget(self.main_splitter, 0, 1, 3, 1)

        self.live = 1

        self.camera.camThread.connect(self.cam_action)
        self.acq.acqThread.connect(self.acquisition_action)
        self.acq.folderThread.connect(self.folder_search, Qt.ConnectionType.QueuedConnection)
        self.motors.motThread.connect(self.motor_action)

        self.motors.changeZ(self.live_widget.control.motor.get_position())

    def acquisition_action(self, event):
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "Start" and self.live == 1:
            self.live = 0
            self.stack.setCurrentIndex(1)
        elif source == "Stop" and self.live == 0:
            self.live = 1
            self.stack.setCurrentIndex(0)
        elif source == "request":
            self.folder_search()
            #self.timer.stop()
            #self.timer.singleShot(0, self.delayed_folder_search)

    def cam_action(self, event):
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "int":
            self.live_widget.control.update_exposure(int(message))
        if source == "num":
            self.numberOfAvgdImages = int(message)

    def motor_action(self, event):
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "stepz":
            self.z_step = float(message)*0.001
        elif source == "up":
            self.live_widget.control.motor.set_motor_displacement(1, self.z_step)
            self.motors.changeZ(self.live_widget.control.motor.get_position())
        elif source == "down":
            self.live_widget.control.motor.set_motor_displacement(0, self.z_step)
            self.motors.changeZ(self.live_widget.control.motor.get_position())
        elif source == "deltaV":
            self.v_step = float(message)

    def update_frame(self):
        try:
            self.live_widget.get_live_sequence(int(self.camera.num_value.text()), float(self.motors.delta_v_value.text()), float(self.motors.v0_value.text()))
            self.image1_widget.set_image_from_array(np.array(self.live_widget.image1), "image1")
            self.image2_widget.set_image_from_array(np.array(self.live_widget.image2), "image2")
            self.image_widget.set_image_from_array(np.array(self.live_widget.image), "image")
            #print("updated")
        except Exception as e:
            return None
            #print(f"the update could not take place : {e}")

    def folder_search(self):
        print("IOGS")
        folder_request = QFileDialog.getExistingDirectory(None, "Choisir un fichier")
        if folder_request:
            #self.acq.acqThread.emit("dir=" + folder_request)
            print(f"the new destination is {folder_request}")
            #self.acq.directory.setText(folder_request)

    def closeEvent(self, event):
        """
        Close event.
        """
        if self.camera is not None:
            self.camera.stop_acquisition()
            self.camera.free_memory()

        print('End of APP')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    sys.exit(app.exec())