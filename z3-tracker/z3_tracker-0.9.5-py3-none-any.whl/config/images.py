'''
Image files
'''

import os.path
import tkinter as tk

__all__ = 'image', 'makebw'


def image(filename: str) -> str:
    '''
    Return full path to image file.

    Args:
        file: basename of image file
    Returns:
        str: full path to image file
    '''

    imagedir = os.path.join(os.path.dirname(__file__), '../images')
    imagepath = os.path.join(imagedir, '{0:s}.png'.format(filename))
    return os.path.normpath(imagepath)


def makebw(img: tk.PhotoImage) -> tk.PhotoImage:
    '''
    Make black&white version of image

    Args:
        img: image to convert
    '''

    for x in range(img.width()):
        for y in range(img.height()):
            bw = sum(img.get(x, y)) // 3
            if bw in (0, 255):
                continue
            img.put('#{0:02x}{0:02x}{0:02x}'.format(bw), (x, y))
    return img
