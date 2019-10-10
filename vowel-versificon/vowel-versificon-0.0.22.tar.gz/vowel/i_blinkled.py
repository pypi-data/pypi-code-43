Ans="""

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)
def blink(n,speed):
    for i in range(0,n):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7,GPIO.OUT)
        GPIO.output(7,True)
        time.sleep(speed)
        GPIO.output(7,False)
        time.sleep(1)
        GPIO.cleanup()
iteration=int(input("No of times to blink"))
speed=int(input("Ener the speed"))
blink(iteration,speed)

#smallneg bigpos 6GND

"""