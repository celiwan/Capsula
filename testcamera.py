from picamera import PiCamera
from time import sleep
camera=PiCamera()
camera.start_preview(fullscreen=True)
sleep(10)

