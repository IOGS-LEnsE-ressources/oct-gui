from PyQt6.QtWidgets import QMainWindow, QPushButton, QFileDialog, QApplication, QVBoxLayout, QWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test folder dialog")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        btn = QPushButton("Choisir dossier")
        btn.clicked.connect(self.folder_search)
        layout.addWidget(btn)

    def folder_search(self):
        folder = QFileDialog.getExistingDirectory(None, "Choisir un dossier")
        if folder:
            print("Dossier sélectionné :", folder)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())