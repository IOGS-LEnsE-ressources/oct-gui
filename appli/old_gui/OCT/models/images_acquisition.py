
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import numpy as np
import time

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow


class ImageLive(QObject):
    finished = pyqtSignal()

    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.main_app = main_app
        self._running = True

    def run(self):
        control = self.main_app.main_widget.control
        while self._running:
            if not self.main_app.camera_acquiring:
                print("Start ACQUISITION")
                control.cam.alloc_memory()
                control.start_acquisition()
                self.main_app.camera_acquiring = True
            self.main_app.acq.set_start_enabled(1)
            self.main_app.acq.set_stop_enabled(0)
            self.main_app.update_frame()
            time.sleep(0.01)
        self.finished.emit()

    def stop(self):
        self._running = False


class ImageAcquisition(QObject):
    finished = pyqtSignal()

    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.main_app = main_app
        self._running = True
        self.number_of_samples = 0

    def run(self):
        control = self.main_app.main_widget.control
        while self._running:
            if not self.main_app.camera_acquiring:
                print("Start ACQUISITION")
                control.cam.alloc_memory()
                control.start_acquisition()
                self.main_app.camera_acquiring = True
            zstep = float(self.main_app.motors.step_z_section.text())
            z0 = self.main_app.z
            vstep = float(self.main_app.motors.delta_v_value.text())
            V0 = float(self.main_app.motors.v0_value.text())
            Nimg = int(self.main_app.camera.num_value.text())
            Nstep = int(self.main_app.acq.step_num.text())
            tol = 0.3
            timeout = 300
            self.main_app.main_widget.get_acquisition_sequence(zstep, z0, vstep, V0, Nimg, self.number_of_samples, Nstep, tol, timeout)
            self.number_of_samples += 1
            self.main_app.get_z()
            self.main_app.update_frame()
            self.main_app.folder.sendTo(self.main_app.main_widget.image, self.number_of_samples)
            time.sleep(0.01)

            if self.number_of_samples >= Nstep:
                self.number_of_samples = 0
                self._running = False
                self.finished.emit()
        self.finished.emit()

    def stop(self):
        self._running = False