Ans="""

import picamera
from time import sleep
cam=picamera.PiCamera()
cam.start_preview()
cam.annotate_text="Hello World"
cam.hflip=True
cam.vflip=True
sleep(1)
cam.capture("image1.jpg")

for i in range(3):
    sleep(1)
    cam.capture("/home/pi/pic%s.jpg"%i)
    
cam.stop_preview()
cam.close()
exit(0)


"""