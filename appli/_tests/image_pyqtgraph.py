import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

app = QtWidgets.QApplication([])

# Créer un widget de type GraphicsLayoutWidget
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Affichage d\'une image avec PyQtGraph')

# Ajouter une vue graphique
view = win.addViewBox()
view.setAspectLocked(True)  # Garde les proportions de l'image

# Générer une image aléatoire
image = np.random.normal(size=(100, 100))

# Créer un objet ImageItem et l'afficher
img_item = pg.ImageItem(image)
view.addItem(img_item)

# Afficher la fenêtre
win.show()
sys.exit(app.exec())