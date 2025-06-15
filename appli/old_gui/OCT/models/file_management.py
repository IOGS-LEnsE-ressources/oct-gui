import numpy as np
from PIL import Image

class fileManager:
    def __init__(self, parent = None):
        self.parent = parent
        self.files = []
        self.directory = ""
        self.name = "/"

    def sendTo(self, image, i):
        img = image.fromarray(image)
        img.save(self.directory + self.name + str(i) + ".tiff")

    def changeDirectory(self, directory:str):
        self.dirtectory = directory

    def changeName(self, name:str):
        self.name = "/" + name