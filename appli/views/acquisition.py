import cv2
import numpy as np
import sys
from lensepy.css import *
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel,  QPushButton,
    QSizePolicy, QProgressBar, QHBoxLayout, QApplication, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow


class AcquisitionView(QWidget):

    filename_changed = pyqtSignal(str)
    acqThread = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__()

        self.setWindowTitle("Acquisition")
        self.parent: "MainWindow" = parent

        layout = QVBoxLayout()

        directory_layout = QHBoxLayout()
        name_layout = QHBoxLayout()
        step_size_layout = QHBoxLayout()
        step_num_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        self.title = QLabel("Acquisition Mode")
        self.title.setStyleSheet(styleH2)

        ### Destination

        self.directory_label = QLabel("Directory")
        self.directory_label.setMaximumWidth(100)
        self.directory_label.setStyleSheet(styleH3)
        self.directory_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.directory = QLineEdit("")
        if self.parent.dir_images != '':
            self.directory.setText(self.parent.dir_images)
        self.directory.setStyleSheet("background-color:white;")
        self.directory.setEnabled(False)
        self.directory.editingFinished.connect(self.directory_action)

        self.search = QPushButton("Browse...")
        self.search.setMinimumWidth(100)
        self.search.setStyleSheet(unactived_button)
        self.search.clicked.connect(self.directory_action)

        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(self.search)

        ### Nom du fichier

        self.name_label = QLabel("File Name : ")
        self.name_label.setStyleSheet(styleH3)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.name = QLineEdit("")
        self.name.setEnabled(True)
        self.name.editingFinished.connect(self.directory_action)

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name)

        ### Pas

        self.step_size_label = QLabel("Vertical Step : p(\u03bcm)")
        self.step_size_label.setStyleSheet(styleH3)
        self.step_size_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        init_value = self.parent.init_acq_step_size
        self.step_size = QLineEdit(str(init_value))
        self.step_size.setEnabled(True)
        self.step_size.editingFinished.connect(self.step_action)

        step_size_layout.addWidget(self.step_size_label)
        step_size_layout.addWidget(self.step_size)

        ### Nombre de pas

        self.step_num_label = QLabel("Number of steps : ")
        self.step_num_label.setStyleSheet(styleH3)
        self.step_num_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        init_value = self.parent.init_acq_step_num
        self.step_num = QLineEdit(str(init_value))
        self.step_num.setEnabled(True)
        self.step_num.editingFinished.connect(self.step_action)

        step_num_layout.addWidget(self.step_num_label)
        step_num_layout.addWidget(self.step_num)

        ### start/stop

        self.start_button = QPushButton("Start")
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet(self.parent.style_but_disabled)
        self.start_button.clicked.connect(self.step_action)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(self.parent.style_but_disabled)

        self.stop_button.clicked.connect(self.step_action)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setObjectName("IOGSProgressBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet(StyleSheet)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title)
        layout.addLayout(directory_layout)
        layout.addWidget(self.directory)
        layout.addLayout(name_layout)
        layout.addLayout(step_size_layout)
        layout.addLayout(step_num_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(40)

        self.setLayout(layout)

    def update_progress_bar(self, progression: float):
        """
        Update the progression bar value.
        :param value: Value to display (float between 0 and 1)
        """
        '''progression est un float entre 0 et 1'''
        bar_progress = int(progression * 100)
        self.progress_bar.setValue(bar_progress)

    def set_start_enabled(self, value: bool):
        """Set the start button enabled."""
        if value:
            self.start_button.setEnabled(True)
            self.start_button.setStyleSheet(self.parent.style_but_enabled)
        else:
            self.start_button.setEnabled(False)
            self.start_button.setStyleSheet(self.parent.style_but_disabled)

    def set_stop_enabled(self, value: bool):
        """Set the stop button enabled."""
        if value:
            self.stop_button.setEnabled(True)
            self.stop_button.setStyleSheet(self.parent.style_but_enabled)
        else:
            self.stop_button.setEnabled(False)
            self.stop_button.setStyleSheet(self.parent.style_but_disabled)

    def directory_action(self):
        sender = self.sender()
        if sender == self.search:
            self.filename_changed.emit("request=")
            #if __name__ == "__main__" : self.folder_search()
        elif sender == self.name:
            self.filename_changed.emit("name=" + self.name.text())
            print(f"the name of the file will be {self.name.text()}")

    def step_action(self):
        sender = self.sender()
        if sender == self.step_size:
            self.acqThread.emit("StepSize=" + self.step_size.text())
            print(f"the step size has been updated")
        elif sender == self.step_num:
            self.acqThread.emit("StepNum=" + self.step_num.text())
            print(f"the number of steps has been updated")
        elif sender == self.start_button:
            self.acqThread.emit("Start=")
            print(f"the acquisition has begun")
        elif sender == self.stop_button:
            self.acqThread.emit("Stop=")
            print(f"the acquisition has been stopped")

    def moderate_interactions(self, activation : bool):
        self.name.setEnabled(activation)
        self.search.setEnabled(activation)
        self.step_size.setEnabled(activation)
        self.step_num.setEnabled(activation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = AcquisitionView()
    fenetre.show()
    sys.exit(app.exec())