import os
import sys

import pygame
import ctypes


def get_by_threshold(threshold, objlist):
    for obj in objlist:
        if obj == threshold:
            return obj
    raise ValueError(threshold, " threshold not found")


def load_sound(name, path=""):
    """
    loads sound
    :param name: sound name
    :param path: sound path
    :return: Sound obj
    """
    return pygame.mixer.Sound(os.path.join(path, name))


def toggle_windows_zoom():
    """
    toggle windows zoom
    :return: None
    """
    ctypes.windll.user32.SetProcessDPIAware()


def smooth_exit(exitcode=0):
    """
    smooth exit
    :param exitcode: exit code
    :return: None
    """
    pygame.quit()
    pygame.display.quit()
    pygame.mixer.quit()
    pygame.font.quit()
    sys.exit(exitcode)


def load_image(filename, path="", size=None, doAlpha=False, colorkey=(255, 0, 255), alpha=None):
    """
    loads an image from disk
    :param filename: name of file
    :param path: path file is resting
    :param size: set a pre size
    :param doAlpha: sets convert mode to alpha
    :param colorkey: set colorkey
    :return: pygame.Surface
    """
    image = pygame.image.load(os.path.join(path, filename))
    if size is not None:
        image = pygame.transform.scale(image, size)

    if doAlpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if colorkey is not None:
        image.set_colorkey(colorkey)
        print("colorkey may be a bottleneck when using large images")

    return image
