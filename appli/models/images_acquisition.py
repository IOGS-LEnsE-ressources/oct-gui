
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
    images_ready = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.main_app = main_app
        self._running = True

    def run(self):
        while self._running:
            # Get images
            piezo = self.main_app.piezo
            camera = self.main_app.camera
            if piezo is not None and self.main_app.camera_connected:
                if not self.main_app.camera_acquiring:
                    print("Start ACQUISITION")
                    camera.alloc_memory()
                    camera.start_acquisition()
                    self.main_app.camera_acquiring = True

                nb_images_text = self.main_app.central_widget.mini_camera.camera_params_widget.num_value.text()
                try:
                    nb_images = int(nb_images_text)
                except Exception as e:
                    print(e)
                    nb_images = 1

                piezo.set_voltage_piezo(self.main_app.piezo_V0)
                images_list = camera.get_images(nb_images)
                self.main_app.image1 = np.mean(images_list, axis = 0)

                piezo.set_voltage_piezo(self.main_app.piezo_step_size + self.main_app.piezo_V0)
                images_list = camera.get_images(nb_images)
                self.main_app.image2 = np.mean(images_list, axis = 0)

                self.main_app.image_oct = np.sqrt((self.main_app.image1 - self.main_app.image2) ** 2)

            time.sleep(0.01)
            self.images_ready.emit()
        self.finished.emit()

    def stop(self):
        self._running = False


class ImageAcquisition(QObject):
    images_ready = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.main_app = main_app
        self._running = True
        self.number_of_samples = 0

    def run(self):
        while self._running:
            # Get images
            piezo = self.main_app.piezo
            camera = self.main_app.camera
            nb_avg_images_text = self.main_app.central_widget.mini_camera.camera_params_widget.num_value.text()

            try:
                nb_avg_images = int(nb_avg_images_text)
            except Exception as e:
                print(e)
                nb_avg_images = 1

            nb_images_text = self.main_app.central_widget.acquisition_options.step_num.text()
            try:
                nb_images = int(nb_images_text)
            except Exception as e:
                print(e)
                nb_images = 1

            print(nb_images)
            if piezo is not None and self.main_app.camera_connected:
                if not self.main_app.camera_acquiring:
                    print("Start ACQUISITION")
                    camera.alloc_memory()
                    camera.start_acquisition()
                    self.main_app.camera_acquiring = True

                piezo.set_voltage_piezo(self.main_app.piezo_V0)
                images_list = camera.get_images(nb_avg_images)
                self.main_app.image1 = np.mean(images_list, axis = 0)

                piezo.set_voltage_piezo(self.main_app.piezo_step_size + self.main_app.piezo_V0)
                images_list = camera.get_images(nb_avg_images)
                self.main_app.image2 = np.mean(images_list, axis = 0)

                self.main_app.image_oct = np.sqrt((self.main_app.image1 - self.main_app.image2) ** 2)

                self.number_of_samples += 1
                print(f'Sample nb = {self.number_of_samples}')

            else:
                self.main_app.image_oct = np.random.randint(0, 256, (50, 100), dtype=np.uint8)
                self.number_of_samples += 1
                print(f'Sample nb = {self.number_of_samples}')

            self.images_ready.emit()

            if self.number_of_samples >= nb_images:
                self.number_of_samples = 0
                self._running = False
                self.finished.emit()

        self.finished.emit()

    def stop(self):
        self._running = False