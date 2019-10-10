Ans="""

import re
import time
import argparse
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
def demo():
    #create matrix device
    serial=spi(port=0, device=0, gpio=noop())
    device=max7219(serial)
    print("Created device")
    # start demo
    msg = "MAX7219 LED Matrix Grid Demo"
    print(msg)
    
    show_message(device, msg, fill="white", font=proportional(CP437_FONT), scroll_delay=0.05)
    time.sleep(0.5)
    msg = input('Enter your text:')
    print(msg)
    show_message(device, msg, fill="white", font=proportional(LCD_FONT), scroll_delay=0.1)
    print('Brightness')
    show_message(device, msg, fill="white", scroll_delay=0.1)
    time.sleep(0.5)
    print('Alternative font!')
    show_message(device, msg, fill="white", font=SINCLAIR_FONT, scroll_delay=0.1)
    time.sleep(0.5)
    print('Proportional font - characters are squeezed together!')
    show_message(device, msg, fill="white", font=proportional(SINCLAIR_FONT), scroll_delay=0.1)
if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        pass


#sudo usermod -a -F spi,gpio.pi
#sudo apt install build-essential python3-dev python3-pip libfreetype6-dev libjpeg-dev
#sudo pip install --upgrade pip setup tools
#sudo -H pip install --upgrade luma.led_matrix
#board pins from VCC to CLK to 2,6,19,24,23
"""