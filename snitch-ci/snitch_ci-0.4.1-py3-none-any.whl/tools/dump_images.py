#!/usr/bin/python3
"""
Takes one or more test case files created with Snitch, extracts all the
screenshots from them, and saves the images in the current directory.
"""

import sys
import os
import json


from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray, qUncompress


def save_base64_to_png(base64_encoded_image, filename):
    if base64_encoded_image:
        img = QPixmap()
        if img.loadFromData(qUncompress(QByteArray.fromBase64(bytes(base64_encoded_image, 'utf8'))), 'PNG'):
            img.save(filename)

def main():
    APP = QApplication(sys.argv)
    if len(sys.argv) < 2:
        print('You must specify at least one file to read')
        exit(1)

    for snitch_file in sys.argv[1:]:
        if os.path.isfile(snitch_file):
            name = os.path.splitext(os.path.basename(snitch_file))[0]
            for i, cap in enumerate(json.load(open(snitch_file, 'r'))['screenshots']):
                save_base64_to_png(cap['image'], '{}_image{:03d}_original.png'.format(name, i))
                save_base64_to_png(cap['result'], '{}_image{:03d}_result.png'.format(name, i))
        else:
            print('File does not exist: {}'.format(snitch_file))

    APP.quit()

if __name__ == '__main__':
    main()
