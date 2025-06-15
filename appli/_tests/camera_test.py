from lensecam.basler.camera_basler import CameraBasler
import matplotlib.pyplot as plt

def find_camera():
    cam = CameraBasler()
    cam_connected = cam.find_first_camera()
    print(cam_connected)
    return cam
