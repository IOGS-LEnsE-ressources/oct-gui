import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QThread
from models.images_acquisition import ImageLive
from views.images import ImageDisplayGraph

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oct_lab_app import MainWindow

class ImageController(QMainWindow):
    def __init__(self, main_app: "MainWindow"):
        super().__init__()
        self.setWindowTitle("MVC Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Vue
        self.viewer = ImageDisplayGraph(self)
        self.setCentralWidget(self.viewer)

        # Modèle
        self.thread = QThread()
        self.worker = ImageLive()
        self.worker.moveToThread(self.thread)

        # Connexions
        self.thread.started.connect(self.worker.run)
        self.worker.image_ready.connect(self.viewer.set_image_from_array)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()

    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()


import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageController()
    window.show()
    sys.exit(app.exec())