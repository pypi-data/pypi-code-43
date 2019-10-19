from zumi.zumi import Zumi
from zumi.util.screen import Screen
import time

import os, subprocess, time, signal
from threading import Thread
from PIL import Image, ImageDraw
import numpy as np


def __progress(screen, img, start, end):
    while start != end:
        draw = ImageDraw.Draw(img)
        draw.point([(start + 13, 35), (start + 13, 36), (start + 13, 37)])
        screen.draw_image(img.convert('1'))
        start += 1


def __finished_updating(_screen, text):
    _zumi = Zumi()
    img = _screen.path_to_image('/usr/local/lib/python3.5/dist-packages/zumi/util/images/happy1.ppm')
    time.sleep(.5)
    _screen.draw_text(text, x=10, y=5, image=img.convert('1'), font_size=12, clear=False)

    tempo = 60
    time.sleep(0.5)
    _zumi.play_note(41, tempo)
    _zumi.play_note(43, tempo)
    _zumi.play_note(45, tempo)


def __kill_updater(proc, timeout):
    print("timeout!")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    timeout["value"] = True


def update_version(_screen):
    p = subprocess.Popen('sudo pip3 install zumidashboard --upgrade',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))

    _screen.draw_text("Updating Firmware", x=9, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    updater_thread = Thread(target=__progress, args=(_screen,img, 0, 51))
    updater_thread.start()

    try:
        while p.poll() is None:
            line = p.stdout.readline().decode()
            print(line)

            if 'Error' in line:
                _screen.draw_text_center("Error!\nPlease Try Again")
                return

            if 'Collecting' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 51, 88))
                updater_thread.start()

            elif 'Installing collected packages' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 88, 96))
                updater_thread.start()

            elif 'Successfully installed zumidashboard' in line:
                updater_thread.join()
                updater_thread = Thread(target=__progress, args=(_screen, img, 96, 101))
                updater_thread.start()
                version_info = line.split('-')[1]

        print(version_info)
        updater_thread.join()

        time.sleep(1)
        __finished_updating(_screen, "Firmware updated!")
        _screen.draw_text_center("Firmware updated to v" + str(version_info), font_size=15)

    except Exception as e:
        updater_thread.join()
        _screen.draw_text_center("Zumi firmware is already latest")
        print(e)


def update_content(_screen):
    past_folder = 'mv /home/pi/Zumi_Content /home/pi/log_Zumi_Content'+str(time.time())
    print(past_folder)
    subprocess.Popen(past_folder,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(1)
    past_folder = "sudo chown -R pi /home/pi/" + past_folder
    subprocess.Popen(past_folder,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    print("change name ")

    p = subprocess.Popen(
        'git clone https://github.com/RobolinkInc/Zumi_Content /home/pi/Zumi_Content',
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, preexec_fn=os.setsid)

    img_arr = np.asarray(Image.open('/usr/local/lib/python3.5/dist-packages/zumi/util/images/blankbar.ppm'))
    img = Image.fromarray(img_arr.astype('uint8'))
    print("start clone")
    _screen.draw_text("Updating Content", x=12, y=8, image=img.convert('1'), font_size=12, clear=False)
    img = _screen.screen_image.convert('RGB')

    time.sleep(1)

    while p.poll() is None:
        line = p.stdout.readline().decode()
        print(line)

        if 'Cloning into ' in line:
            updater_thread = Thread(target=__progress, args=(_screen, img, 0, 101))
            updater_thread.start()

        elif 'Already up-to-date' in line:
            _screen.draw_text_center('Zumi content is already latest')
            break
    try:
        updater_thread.join()
    except Exception as e:
        print(e)
        print("error")
        return False
    time.sleep(1)
    subprocess.Popen("sudo chown -R pi /home/pi/Zumi_Content",
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    __finished_updating(_screen, "Content updated!")
    return True


def restart_threads(_screen):
    Thread(target=restart_app, args=()).start()
    Thread(target=go_to_zumi_dashboard_msg, args=(_screen,)).start()


def restart_app():
    subprocess.run(["sudo python3 /home/pi/Dashboard/dashboard.py"], shell=True)


def go_to_zumi_dashboard_msg(_screen):
    _screen.draw_text_center("Dashboard restarting...")
    for x in range(20):
        time.sleep(1)
    _screen.draw_text_center("Go to \"zumidashboard.ai\" in your browser")


def run():
    screen = Screen(clear=False)
    update_version(screen)
    time.sleep(2)
    update_content(screen)
    restart_threads(screen)


if __name__ == '__main__':
    run()

