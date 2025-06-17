import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
import time
import numpy as np
from PIL import Image
from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from models.images_acquisition import ImageLive, ImageAcquisition

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow

### Timings of the motor during acquisition phase
TOLERANCE = 0.01 #(tolerance in position in um)
TIMEOUT = 3 #(motor displacement timeout in s)


class ModesController:
    """
    Modes manager.
    """

    def __init__(self, main_app: "MainWindow"):
        """
        Default constructor.
        :param manager: Main manager of the application (ModesManager).
        """
        self.main_app: "MainWindow" = main_app
        # For image processing and displaying / Thread
        self.thread = QThread()
        self.worker = None
        self.dialog = None

        ### Initial values
        self.number_samples = int(self.main_app.init_acq_step_num)
        self.acq_stepper_step_size = float(self.main_app.init_acq_step_size) * 0.001
        self.position = float(self.main_app.stepper_init_value)

        # Signals management
        camera_widget = self.main_app.central_widget.mini_camera.camera_params_widget
        camera_widget.camera_exposure_changed.connect(self.handle_camera_exposure)
        motor_widget = self.main_app.central_widget.motors_options
        motor_widget.motor_changed.connect(self.handle_stepper_move)
        image_widget = self.main_app.central_widget.image_params
        image_widget.image_changed.connect(self.handle_image_display)
        acq_widget = self.main_app.central_widget.acquisition_options
        acq_widget.filename_changed.connect(self.handle_folder)
        acq_widget.acqThread.connect(self.handle_acquisition)

        # Variables
        self.stepper_z_step = float(self.main_app.stepper_step) * 0.001

        motors = self.main_app.central_widget.motors_options
        new_position = np.round(self.main_app.step_motor.get_position(), 3)
        motors.changeZ(new_position)

        # Start first mode : Live
        self.mode = 'live'
        self.start_live()


    def start_live(self):
        self.worker = ImageLive(self.main_app)
        self.worker.moveToThread(self.thread)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.images_ready.connect(self.display_live_images)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()


    def start_acquisition(self):
        self.worker = ImageAcquisition(self.main_app)
        self.worker.moveToThread(self.thread)

        # Motor displacement
        self.position = self.main_app.step_motor.get_position()
        self.moderate_interactions(False)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.images_ready.connect(self.store_acquisition_images)
        self.worker.finished.connect(self.stop_acquisition)
        self.thread.start()

    def stop_acquisition(self):
        acquisition = self.main_app.central_widget.acquisition_options
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

        z0 = self.position
        self.main_app.acquisition_update(z0, TOLERANCE, TIMEOUT)
        acquisition.set_start_enabled(True)
        acquisition.set_stop_enabled(False)

        self.moderate_interactions(True)

        self.start_live()

    def store_acquisition_images(self):
        """Store and display images."""
        self.display_live_images()
        z0 = self.position
        z_step = self.acq_stepper_step_size
        image_number = self.worker.number_of_samples
        print(f'Acq N-{image_number}')
        # Store images in
        image_float64 = self.main_app.image_oct.astype(np.uint16)
        img = Image.fromarray(image_float64 * 16)
        dir_name = self.main_app.dir_images+'/'+self.main_app.file_name+'/'
        name = dir_name+self.main_app.file_name+f'_{image_number}.tiff'
        img.save(name)
        # Move motor to new position
        self.main_app.acquisition_update(z0 + image_number * z_step, TOLERANCE, TIMEOUT)

        # Update Progression bar !
        nb_images_text = self.main_app.central_widget.acquisition_options.step_num.text()
        try:
            nb_images = int(nb_images_text)
        except Exception as e:
            print(e)
            nb_images = 1

        progress = image_number/nb_images
        if 1 >= progress >= 0:
            self.main_app.central_widget.acquisition_options.update_progress_bar(progress)
        elif progress < 0:
            self.main_app.central_widget.acquisition_options.update_progress_bar(0.)
        else:
            self.main_app.central_widget.acquisition_options.update_progress_bar(1.)

    def convertTo_uint8(self, image):
        type = image.dtype
        if type == "uint8":
            return image
        if type == "float16":
            image_float32 = image.astype(np.float32)
        elif type == "float32":
            image_float32 = image
        elif type == "float64":
            image_float32 = image.astype(np.float32)
        image_normalized = image_float32/16 # - np.min(image_float32)) / (np.max(image_float32) - np.min(image_float32) + 1e-8)
        image_uint8 = image_normalized.astype(np.uint8) # (image_normalized * 255).astype(np.uint8)
        return image_uint8

    def display_live_images(self):
        """
        Display images for live mode in the main_view
        """
        image_view = self.main_app.central_widget
        piezo = self.main_app.piezo
        if piezo is not None and self.main_app.camera_connected:
            self.main_app.image1 = self.convertTo_uint8(self.main_app.image1)
            self.main_app.image2 = self.convertTo_uint8(self.main_app.image2)

            image_view.image1_widget.set_image_from_array(self.main_app.image1, 'Image 1')
            image_view.image2_widget.set_image_from_array(self.main_app.image2, 'Image 2')
            image_oct = self.convertTo_uint8(self.main_app.image_oct)
            if self.main_app.image_log_display:
                image_oct_disp = np.log(image_oct+0.01)
                image_view.image_oct_graph.set_image_from_array(image_oct_disp, 'OCT - LOG')
            else:
                coeff = self.main_app.image_intensity_factor
                image_oct_disp = coeff * image_oct
                image_view.image_oct_graph.set_image_from_array(image_oct_disp, f'OCT - x {coeff}')

        else:
            black = np.random.normal(size=(100, 100))
            image_view.image1_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image2_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image_oct_graph.set_image_from_array(black, "No Piezo or camera")

    def handle_image_display(self, event):
        """Action performed when display image parameters changed."""
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == 'IntFactor':
            self.main_app.image_intensity_factor = int(message)
        elif source == "Log":
            if message == '1':
                self.main_app.image_log_display = True
            else:
                self.main_app.image_log_display = False


    def handle_camera_exposure(self, event):
        """Action performed when camera exposure time slider changed."""
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "int":
            self.main_app.camera.set_exposure(int(message))
        if source == "num":
            self.worker.stop()
            time.sleep(0.1)
            self.thread.quit()
            self.thread.wait()
            self.main_app.number_avgd_images = int(message)
            self.start_live()

    def handle_stepper_move(self, event):
        """Action performed when Up or Down button is clicked."""
        motors = self.main_app.central_widget.motors_options
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "stepz":
            self.stepper_z_step = float(message) * 0.001
        elif source == "up":
            self.main_app.step_motor.set_motor_displacement(1, self.stepper_z_step)
            new_position = np.round(self.main_app.step_motor.get_position(), 3)
            motors.changeZ(new_position)
            # Update widget ?
        elif source == "down":
            self.main_app.step_motor.set_motor_displacement(0, self.stepper_z_step)
            new_position = np.round(self.main_app.step_motor.get_position(), 3)
            motors.changeZ(new_position)
        elif source == "deltaV":
            self.v_step = float(message)
        elif source == "V0":
            self.main_app.piezo_V0 = int(message)

    def handle_folder(self, event):
        """Action performed when Up or Down button is clicked."""
        acquisition = self.main_app.central_widget.acquisition_options
        dir_images = self.main_app.dir_images
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        print(dir_images)
        if source == "request":
            self.worker.stop()

            self.dialog = QFileDialog(self.main_app)
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)  # Pour choisir un dossier
            self.dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)  # Pour n’afficher que des dossiers
            self.dialog.setDirectory(dir_images)
            self.dialog.fileSelected.connect(self.folder_selected)
            self.dialog.show()

        if source == "name":
            if acquisition.directory.text() != '':
                # Check Name ?? (only "normal" character)
                self.main_app.file_name = acquisition.name.text()
                acquisition.set_start_enabled(True)

    def folder_selected(self, directory):
        acquisition = self.main_app.central_widget.acquisition_options
        self.main_app.dir_images = directory
        acquisition.directory.setText(directory)
        if acquisition.name.text() != '':
            acquisition.set_start_enabled(True)

        self.start_live()

    def moderate_interactions(self, activation : bool):
        self.main_app.central_widget.motors_options.moderate_interactions(activation)
        self.main_app.central_widget.acquisition_options.moderate_interactions(activation)
        self.main_app.central_widget.mini_camera.camera_params_widget.moderate_interactions(activation)

    def handle_acquisition(self, event):
        """Action to performed when acquisition is started."""
        print(event)
        acquisition = self.main_app.central_widget.acquisition_options
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        # Stop all threads
        self.worker.stop()
        time.sleep(0.1)
        self.thread.quit()
        self.thread.wait()
        # Restart in the good mode
        if source == 'Start':
            dir_images = self.main_app.dir_images
            file_name = self.main_app.file_name
            if not os.path.exists(dir_images+'/'+file_name):
                os.makedirs(dir_images+'/'+file_name)
            else:
                dlg = QMessageBox(self.main_app)
                dlg.setWindowTitle("Warning - Directory already exists")
                dlg.setText("The file name is already existing ! \r\nNo acquisition will be done")
                dlg.setStandardButtons(
                    QMessageBox.StandardButton.Ok
                )
                dlg.setIcon(QMessageBox.Icon.Warning)
                button = dlg.exec()
                acquisition.set_start_enabled(True)
                acquisition.set_stop_enabled(False)
                self.start_live()
                return
            self.mode = 'acq'
            self.worker.images_ready.disconnect(self.display_live_images)
            print('Start Acq')
            acquisition.set_start_enabled(False)
            acquisition.set_stop_enabled(True)
            self.main_app.stepper_init_value = self.main_app.step_motor.get_position()
            self.start_acquisition()
        elif source == 'Stop':
            self.mode = 'live'
            self.worker.images_ready.disconnect(self.store_acquisition_images)
            print('Stop Acq')
            acquisition.set_start_enabled(True)
            acquisition.set_stop_enabled(False)
            self.start_live()
        elif source == "StepNum":
            self.number_samples = int(message)
            print(event)
            self.start_live()
        elif source == "StepSize":
            self.acq_stepper_step_size = float(message) * 0.001
            print(self.main_app.stepper_step)
            print(event)
            self.start_live()
