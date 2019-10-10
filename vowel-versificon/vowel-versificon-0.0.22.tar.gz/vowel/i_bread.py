Ans="""

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7,GPIO.OUT,initial=GPIO.LOW)
N=0
while(N<5):
    GPIO.output(7,True)
    time.sleep(1)
    print("Connected")
    GPIO.output(7,False)
    time.sleep(1)
    N=N+1
    
GPIO.cleanup()
#Posbig NegSmall
#pos end of wire on row 5 neg end on row 7
#one end of resistor on row 7 other on right side of board(2col side) on 11th row
#GPIO 7 on besides the row 5 right side big section
#Ground in top right on 2col side
"""