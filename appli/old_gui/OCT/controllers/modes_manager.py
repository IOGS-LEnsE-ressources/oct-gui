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

        # Variables
        self.stepper_z_step = self.main_app.z_step

        acq_widget = self.main_app.acq
        acq_widget.folderThread.connect(self.handle_folder)
        acq_widget.acqThread.connect(self.handle_acquisition)

        # Start first mode : Live
        self.mode = 'live'
        self.start_live()


    def start_live(self):
        self.worker = ImageLive(self.main_app)
        self.worker.moveToThread(self.thread)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()


    def start_acquisition(self):
        self.worker = ImageAcquisition(self.main_app)
        self.worker.moveToThread(self.thread)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()


    '''def store_acquisition_images(self):
        """Store and display images."""
        self.display_live_images()
        z0 = self.main_app.stepper_init_value
        z_step = self.main_app.stepper_init_value
        image_number = self.worker.number_of_samples
        print(f'Acq N-{image_number}')
        # Store images in
        img = Image.fromarray(self.main_app.image_oct)
        dir_name = self.main_app.dir_images+'/'+self.main_app.file_name+'/'
        name = dir_name+self.main_app.file_name+f'_{image_number}.tiff'
        img.save(name)
        # Move motor to new position
        self.main_app.step_motor.move_motor(z0 + image_number * z_step)

        # Update Progression bar !


    def display_live_images(self):
        """
        Display images for live mode in the main_view
        """
        image_view = self.main_app.central_widget
        piezo = self.main_app.piezo
        if piezo is not None and self.main_app.camera_connected:
            image_view.image1_widget.set_image_from_array(self.main_app.image1, 'Image 1')
            image_view.image2_widget.set_image_from_array(self.main_app.image2, 'Image 2')
            image_view.image_oct_graph.set_image_from_array(self.main_app.image_oct, 'OCT')
        else:
            black = np.random.normal(size=(100, 100))
            image_view.image1_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image2_widget.set_image_from_array(black, "No Piezo or camera")
            image_view.image_oct_graph.set_image_from_array(black, "No Piezo or camera")

    def handle_camera_exposure(self, event):
        """Action performed when camera exposure time slider changed."""
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        if source == "int":
            self.main_app.camera.set_exposure(int(message))
        if source == "num":
            self.main_app.number_avgd_images = int(message)

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
            self.v_step = float(message)'''

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

            dialog = QFileDialog(self.main_app)
            dialog.setFileMode(QFileDialog.FileMode.Directory)  # Pour choisir un dossier
            dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)  # Pour n’afficher que des dossiers
            dialog.setDirectory(dir_images)
            dialog.fileSelected.connect(self.folder_selected)
            dialog.show()

            '''
            folder_request = QFileDialog.getExistingDirectory(None, "Select a directory...",
                                                              dir_images, QFileDialog.Option.ShowDirsOnly)
            if folder_request:
                acquisition.directory.setText(folder_request)
                if acquisition.name.text() != '':
                    acquisition.set_start_enabled(True)
            self.start_live()
            '''
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

    def handle_acquisition(self, event):
        """Action to performed when acquisition is started."""
        acquisition = self.main_app.acq
        print(event)
        source_event = event.split("=")
        source = source_event[0]
        message = source_event[1]
        # Stop all threads
        self.worker.stop()
        time.sleep(0.1)
        self.thread.quit()
        self.thread.wait()
        # Restart in the good mode
        if source == 'Start' and not self.mode == 'acq':
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
            print('Start Acq')
            acquisition.set_start_enabled(False)
            acquisition.set_stop_enabled(True)
            self.main_app.stepper_init_value = self.main_app.step_motor.get_position()
            self.start_acquisition()
        elif source == 'Stop':
            self.mode = 'live'
            print('Stop Acq')
            acquisition.set_start_enabled(True)
            acquisition.set_stop_enabled(False)
            self.start_live()
        elif source == "name":
            self.main_app.folder.name = message