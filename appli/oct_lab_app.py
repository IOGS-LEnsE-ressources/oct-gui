# -*- coding: utf-8 -*-
"""*oct_lab_app.py* file.

*oct_lab_app* file that contains :class::OCTLabApp

This file is attached to a 3rd year of engineer training labwork in photonics.
Subject :

More about the development of this interface :
https://iogs-lense-ressources.github.io/camera-gui/

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
.. moduleauthor:: Julien MOREAU () <julien.moreau@institutoptique.fr>
"""
import sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from lensepy import load_dictionary, translate, dictionary
from PyQt6.QtWidgets import (
    QWidget, QPushButton,
    QMainWindow, QApplication, QMessageBox)

## Widgets
from lensepy.pyqt6 import *
from lensepy.pyqt6.widget_image_display import ImageDisplayWidget
from views.main_view import MainView
from lensecam.basler.camera_basler import CameraBasler, get_bits_per_pixel
from models.motor_control import *
from controllers.modes_manager import ModesController

def load_default_dictionary(language: str) -> bool:
    """Initialize default dictionary from default_config.txt file"""
    file_name_dict = f'./lang/dict_{language}.txt'
    load_dictionary(file_name_dict)


def load_default_parameters(file_path: str) -> dict:
    """
    Load parameter from a CSV file.

    :return: Dict containing 'key_1': 'language_word_1'.

    Notes
    -----
    This function reads a CSV file that contains key-value pairs separated by semicolons (';')
    and stores them in a global dictionary variable. The CSV file may contain comments
    prefixed by '#', which will be ignored.

    The file should have the following format:
        # comment
        # comment
        key_1 ; language_word_1
        key_2 ; language_word_2
    """
    dictionary_loaded = {}
    if os.path.exists(file_path):
        # Read the CSV file, ignoring lines starting with '//'
        data = np.genfromtxt(file_path, delimiter=';',
                             dtype=str, comments='#', encoding='UTF-8')
        # Populate the dictionary with key-value pairs from the CSV file
        for key, value in data:
            dictionary_loaded[key.strip()] = value.strip()
        return dictionary_loaded
    else:
        print('File error')
        return {}


class MainWindow(QMainWindow):
    """
    Our main window.

    Args:
        QMainWindow (class): QMainWindow can contain several widgets.
    """

    def __init__(self):
        """
        Initialisation of the main Window.
        """
        super().__init__()
        load_default_dictionary('FR')
        # Read default parameters
        self.default_parameters = load_default_parameters('./assets/config.txt')

        # Main objects
        # ------------
        self.piezo = None
        self.step_motor = None
        self.camera = None
        self.camera_connected = False
        self.camera_acquiring = False
        self.image1 = None
        self.image2 = None
        self.image_oct = None

        self.image_bits_depth = 12

        # Main variables
        if 'PiezoDV' in self.default_parameters:
            self.piezo_step_size = float(self.default_parameters['PiezoDV'])
        if 'PiezoV0' in self.default_parameters:
            self.piezo_V0 = float(self.default_parameters['PiezoV0'])
        if 'StepperInitPosition' in self.default_parameters:
            self.stepper_init_value = float(self.default_parameters['StepperInitPosition'])
        if 'StepperInitStep' in self.default_parameters:
            self.stepper_step = float(self.default_parameters['StepperInitStep'])
        if 'MaxExpoTime' in self.default_parameters:
            self.max_expo_value = self.default_parameters['MaxExpoTime']
        if 'MinExpoTime' in self.default_parameters:
            self.min_expo_value = self.default_parameters['MinExpoTime']
        if 'ExposureTime' in self.default_parameters:
            self.ini_expo_value = self.default_parameters['ExposureTime']
        if 'NumberAvgdImages' in self.default_parameters:
            self.number_avgd_images = self.default_parameters['NumberAvgdImages']
        if 'MotorMaxPos' in self.default_parameters:
            self.motor_max_pos = self.default_parameters['MotorMaxPos']
        if 'AcquisitionStepSize' in self.default_parameters:
            self.init_acq_step_size = self.default_parameters['AcquisitionStepSize']
        if 'AcquisitionStepNumber' in self.default_parameters:
            self.init_acq_step_num = self.default_parameters['AcquisitionStepNumber']

        ### Buttons style sheet
        self.style_but_enabled = """QPushButton {
                                background-color: #ff960a;
                                color: white;
                                border-radius: 5px;
                                padding: 8px 16px;
                            }
                            QPushButton:hover {
                                background-color: #d7861c;
                            }
                            QPushButton:pressed {
                                background-color: #aa752f;
                            }"""
        self.style_but_disabled = """QPushButton {
                                background-color: #555555;
                                color: white;
                                border-radius: 5px;
                                padding: 8px 16px;
                            }"""

        self.dir_images = os.path.expanduser("~")
        if 'DirImages' in self.default_parameters:
            self.dir_images = self.default_parameters['DirImages']
        self.file_name = ''

        ## GUI structure
        self.central_widget = MainView(self)
        self.setCentralWidget(self.central_widget)

        # Initialization
        self.init_app()
        self.controller = ModesController(self)

    def init_app(self):
        """
        Initialization of the application : camera, piezo, step motor, gui.
        """
        # Initialization of the camera
        # ----------------------------
        print('Camera Initialization')
        self.camera = CameraBasler()
        self.camera_connected = self.camera.find_first_camera()
        if self.camera_connected:
            self.camera.init_camera()
            self.camera.set_color_mode('Mono12')
            if 'Exposure Time' in self.default_parameters:
                self.camera.set_exposure(float(self.default_parameters['Exposure Time'])*1000)  # in us
            else:
                self.camera.set_exposure(1000) # in us
            self.camera.set_frame_rate(80)

            print(f'FPS = {self.camera.get_frame_rate()}')
            self.image_bits_depth = get_bits_per_pixel(self.camera.get_color_mode())
            # Binning 2x2
            self.camera.camera_device.Open()
            self.camera.camera_device.BinningVertical.Value = 2
            self.camera.camera_device.BinningHorizontal.Value = 2
            self.camera.camera_device.Close()

            print(f'Color mode = {self.image_bits_depth}')
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Warning - No Camera Connected")
            dlg.setText("No Basler Camera is connected to the computer...\n\nThe application will not start "
                        "correctly.\n\nYou will only access to a pre-established data set.")
            dlg.setStandardButtons(
                QMessageBox.StandardButton.Ok
            )
            dlg.setIcon(QMessageBox.Icon.Warning)
            button = dlg.exec()

        # Initialization of the piezo
        # ---------------------------
        print('Piezo Initialization')
        if 'PiezoSN' in self.default_parameters:
            self.piezo = Piezo(serial_no=self.default_parameters['PiezoSN'])
        else:
            self.piezo = Piezo()
        serial = self.piezo.serial_no
        print(f'Piezo connected / SN = {serial}')

        # Initialization of the step motor
        # --------------------------------
        print('Step Motor Initialization')
        if 'StepSN' in self.default_parameters:
            self.step_motor = Motor(self, serial_no=self.default_parameters['StepSN'])
        else:
            self.step_motor = Motor(self)
        serial = self.step_motor.serial_no
        print(f'Step Motor connected / SN = {serial}')
        if 'StepperInitPosition' in self.default_parameters:
            position = float(self.default_parameters['StepperInitPosition'])
        else:
            position = 3.2
        self.step_motor.move_motor(position)
        new_position = self.step_motor.get_position()
        print(f'Step Motor moved to position {new_position} mm')

        # At the end, start LIVE mode

    def acquisition_update(self,consigne, tolerance = 0.1, timeout = 300):
        self.step_motor.move_motor(consigne)
        a = 0
        print(consigne)
        while(self.step_motor.get_position() - consigne > tolerance and a < timeout):
            a+=1
            time.sleep(0.01)


    def resizeEvent(self, event):
        """
        Action performed when the main window is resized.
        :param event: Object that triggered the event.
        """
        pass

    def closeEvent(self, event):
        """
        closeEvent redefinition. Use when the user clicks
        on the red cross to close the window
        """
        reply = QMessageBox.question(self, 'Quit', 'Do you really want to close ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.controller.worker is not None:
                self.controller.worker.stop()
                self.controller.thread.quit()
                self.controller.thread.wait()
            if self.camera_connected:
                print("Disconnect Camera")
                self.camera.stop_acquisition()
                self.camera.disconnect()
            if self.piezo is not None:
                self.piezo.disconnect_piezo()
            if self.step_motor is not None:
                self.step_motor.disconnect_motor()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())