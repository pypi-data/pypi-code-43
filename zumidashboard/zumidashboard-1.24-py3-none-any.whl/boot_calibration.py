import time
from zumi.zumi import Zumi
from zumi.util.screen import Screen
import zumidashboard.scripts as scripts
import os
import subprocess
from socket import gethostname
import zumidashboard.sounds as sound


def run():
    zumi = Zumi()
    screen = Screen()

    if os.path.isfile('/home/pi/recalibrate'):
        subprocess.Popen(['sudo', 'rm', '-rf', '/home/pi/recalibrate'])

        screen.draw_text_center("Place me on\na flat surface.",font_size=18)
        sound.happy_sound(zumi)
        time.sleep(5)

        screen.calibrating()
        sound.try_calibrate_sound(zumi)
        zumi.mpu.calibrate_MPU()

        screen.draw_image_by_name("calibrated")
        sound.calibrated_sound(zumi)

    time.sleep(1)
    screen.draw_text_center("Find \"" + gethostname() + "\" in your WiFi list")
    sound.happy_sound(zumi)

    while not scripts.is_device_connected():
        time.sleep(.2)
    screen.draw_image_by_name("foundme")
    sound.celebrate_sound(zumi)
    time.sleep(2)
    screen.draw_text_center("Go to \"zumidashboard.ai\" in your browser")
    time.sleep(1)


if __name__ == '__main__':
    run()
