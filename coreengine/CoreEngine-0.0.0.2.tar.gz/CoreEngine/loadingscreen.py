import pygame
import time


class LoadingScreen(object):
    def __init__(self, screen, image):
        self.screen = screen
        self.image = image
        self._max = 100
        self._current = 0

        self.screen_size = self.screen.get_size()
        self._half_w = self.screen_size[0] // 2
        self._half_h = self.screen_size[1] // 2

    def update(self):
        """
        blits image
        :return: None
        """
        pygame.event.pump()
        self.screen.blit(self.image, (0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), (
            self._half_h - self._half_h // 2,
            self._half_h,
            self._half_w,
            self._half_h
        ), 5)
        pygame.draw.rect(self.screen, (50, 50, 50), (
            self._half_w - self._half_w // 2 - 1,
            self._half_h - 1,
            self._half_w - 2,
            self._half_h - 2
        ))
        pygame.display.flip()

    @property
    def current(self):
        """
        get current
        :return: current
        """
        return self._current

    @current.setter
    def current(self, value):
        """
        set current
        :param value: new current
        :return: None
        """
        self._current = value
        if self._current > 100:
            self._current = 100
            print("[WARNING] Loading Bar current value too high")
