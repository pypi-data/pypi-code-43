from math import floor
from time import time


class Tile(object):
    """
    container class
    """

    def __init__(self, pos, image):
        self.image = image
        self.size = self.image.get_rect(topleft=pos)


class AnimatedTile(object):
    """
    Animated tile container class
    """

    def __init__(self, pos, frames, ticks_peed):
        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.tick_speed = ticks_peed
        self.is_dirty = True
        self.last_frame = self.frames.index(self.image)

    def update(self, *args):
        """
        updates image
        :param delta: delta time
        :return:None
        """
        self.image = self.frames[floor((time() % self.tick_speed) * len(self.frames) / self.tick_speed)]
        if self.last_frame != self.frames.index(self.image):
            self.is_dirty = True

    def render(self, surface):
        """
        renders image
        :param surface: pygame.Surface
        :return: None
        """
        surface.blit(self.image, self.rect)
        self.is_dirty = False
