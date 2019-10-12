import pygame
from pygame import freetype

freetype.init()


class FontObject(pygame.sprite.DirtySprite):
    def __init__(self):
        pygame.sprite.DirtySprite.__init__(self)
        self.dirty = 2
        self._layer = 1
        self.visible = True

    def update(self, *args):
        pass


class Button(FontObject):
    def __init__(self, pos, size, color, text="", threshold=""):
        FontObject.__init__(self)

        self.threshold = threshold
        self.size = size
        self.pos = pos
        self.text = text

        self.image = pygame.Surface([*self.size])
        self.image.fill(color)
        self.origin = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.font = freetype.SysFont("arial", 20)
        self.render_text(self.text)

        self.pointer = None
        self.value = None

    def render_text(self, text):
        """
        renders test to own surface -> updates itself
        :param text: new text
        :return: None
        """
        self.image = self.origin.copy()
        size = self.font.get_rect(text).size
        self.font.render_to(self.image, (self.size[0] // 2 - size[0] // 2, self.size[1] // 2 - size[1] // 2), text)

    def render(self, surface):
        """
        render to image
        :param surface: pygame.Surface
        :return: None
        """
        surface.blit(self.image, self.rect)

    def on_click(self, cursor):
        """
        check if clicked
        :param cursor: mousepos
        :return: None
        """
        if self.rect.x < cursor[0] < self.rect.right and self.rect.y < cursor[1] < self.rect.bottom:
            return True
        return False


class Label(FontObject):
    def __init__(self, pos, size, color, text):
        FontObject.__init__(self)

        self.size = size
        self.pos = pos
        self.text = text

        self.image = pygame.Surface([*self.size])
        self.image.fill(color)
        self.origin = self.image.copy()
        self.rect = self.image.get_rect(topleft=self.pos)

        self.font = freetype.SysFont("arial", 20)
        self.render_text(self.text)

        self.pointer = None
        self.value = None

    def render(self, surface):
        """
        render to image
        :param surface: pygame.Surface
        :return: None
        """
        surface.blit(self.image, self.rect)

    def render_text(self, text):
        """
        render text to img
        :param text: text
        :return: None
        """
        self.image = self.origin.copy()
        size = self.font.get_rect(text).size
        self.font.render_to(self.image, (self.size[0] // 2 - size[0] // 2, self.size[1] // 2 - size[1] // 2), text)


class TextInputBox(FontObject):
    def __init__(self, pos, size, color, threshold=""):
        FontObject.__init__(self)

        self.threshold = threshold

        self.text = ""
        self.pos = pos
        self.size = size

        self.image = pygame.Surface([*size])
        self.image.fill(color)
        self.origin = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)

        self.font = freetype.SysFont("arial", 20)

        self.active = False

    def handle_input(self, event):
        """
        handle key events
        :param event: keydown event
        :return: None
        """
        if event.unicode == '\r':
            self.active = False
        elif event.unicode == '\x08':
            self.text = self.text[:-1]
            self._render()
        else:
            self.text += event.unicode
            self._render()

    def _render(self):
        """
        render text
        :return: None
        """
        self.image = self.origin.copy()
        size = self.font.get_rect(self.text).size
        self.font.render_to(self.image, (5, self.size[1] // 2 - size[1] // 2), self.text)

    def render(self, surface):
        """
        render to image
        :param surface: pygame.Surface
        :return: None
        """
        surface.blit(self.image, self.rect)

    def on_click(self, cursor):
        """
        checks collision
        :param cursor: mouse pos
        :return: bool ifhit
        """
        if self.rect.x < cursor[0] < self.rect.right and self.rect.y < self.rect.bottom:
            return True
        return False
