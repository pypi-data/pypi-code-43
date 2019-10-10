Ans="""

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
control_pins = [7,11,13,15]
for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)
halfstep_seq = [
  [1,0,0,0],
  [1,1,0,0],
  [0,1,0,0],
  [0,1,1,0],
  [0,0,1,0],
  [0,0,1,1],
  [0,0,0,1],
  [1,0,0,1]
]
for i in range(512):
  for halfstep in range(8):
    for pin in range(4):
      GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
    time.sleep(0.001)

print('fan wrking')
GPIO.cleanup()
#7,11,13,15 to IN1,2,3,4
#POs of circ to pin 2
#NEg of circ to pin 6


"""