# -*- coding: utf-8 -*-
"""*main_view.py* file.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Julien VILLEMEJANE (PRAG LEnsE) <julien.villemejane@institutoptique.fr>
"""
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt6.QtWidgets import (
    QMessageBox
)
from lensepy import translate
from views.live_mode import *

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QSplitter, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt
from views.images import ImageDisplayGraph
from views.live_mode import liveWidget


class imageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.image_graph = ImageDisplayGraph(self, '#404040')
        self.live_widget = liveWidget()

        self.image1_widget = ImageDisplayGraph(self, '#909090')
        self.image2_widget = ImageDisplayGraph(self, '#909090')
        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_splitter.addWidget(self.image1_widget)
        self.top_splitter.addWidget(self.image2_widget)

        # Zone dynamique pour image ou live
        self.stack = QStackedWidget()
        self.stack.addWidget(self.live_widget)    # index 0
        self.stack.addWidget(self.image_graph)    # index 1
        self.stack.setCurrentIndex(0)

        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.stack)

        self.start = QPushButton("acquisition")
        self.stop = QPushButton("live")
        self.start.clicked.connect(self.button_action)
        self.stop.clicked.connect(self.button_action)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 2)

        # Configuration des lignes
        self.layout.setRowStretch(0, 4)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)

        self.dummy = QPushButton()

        self.layout.addWidget(self.start, 0, 0)
        self.layout.addWidget(self.stop, 1, 0)
        self.layout.addWidget(self.dummy, 2, 0)

        self.layout.addWidget(self.main_splitter, 0, 1, 3, 1)

        self.live = 1

    def button_action(self):
        sender = self.sender()
        if sender == self.start and self.live == 1:
            self.live = 0
            print("acquisition démarrée")
            self.stack.setCurrentIndex(1)
        elif sender == self.stop and self.live == 0:
            self.live = 1
            print("acquisition terminée")
            self.stack.setCurrentIndex(0)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    class MyWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle(translate("window_title_main_menu_widget"))
            self.setGeometry(100, 200, 800, 600)

            self.central_widget = imageWidget(self)
            self.setCentralWidget(self.central_widget)

        def create_gui(self):
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
                event.accept()
            else:
                event.ignore()


    app = QApplication(sys.argv)
    main = MyWindow()
    main.create_gui()
    main.show()
    sys.exit(app.exec())