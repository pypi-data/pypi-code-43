import pygame
import os


class SpriteSheetCreator(object):
    def __init__(self, filename, path="", colorkey=(255, 0, 255)):
        self.sheet = pygame.image.load(os.path.join(path, filename)).convert()
        self.sheet.set_colorkey(colorkey)

    def get_image_clip(self, clip):
        """
        get clip of image
        :param clip: pygame.Rect
        :return: pygame.Surface
        """
        return self.sheet.subsurface(clip)
