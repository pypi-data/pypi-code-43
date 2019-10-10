Ans="""

import picamera
from time import sleep
cam=picamera.PiCamera()
cam.resolution=(640,480)
print("video recording start ho jaa!!")
cam.start_recording('/home/pi/demo.h264')
cam.wait_recording(8)
cam.stop_recording()
cam.close()
print("video recording rukk jaa!!")
exit(0)


"""