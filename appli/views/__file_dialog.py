import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListView, QLabel
)
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtCore import QDir
from PyQt6.QtGui import QFileSystemModel

class FileSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.homePath())  # Point de départ

        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(QDir.homePath()))
        self.view.clicked.connect(self.on_file_selected)

        layout.addWidget(self.view)

    def on_file_selected(self, index):
        filepath = self.model.filePath(index)
        print("Fichier sélectionné :", filepath)

app = QApplication(sys.argv)
widget = FileSelectorWidget()
widget.show()
sys.exit(app.exec())