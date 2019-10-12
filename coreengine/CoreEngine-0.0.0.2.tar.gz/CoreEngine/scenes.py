import pygame


class Scene(object):
    def __init__(self):
        self.next_scene = self
        self.key_map = {"EXIT": pygame.K_ESCAPE}

    def events(self):
        """
        event loop for game events
        :return: None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT and event.type == pygame.KEYDOWN and event.key == self.key_map["EXIT"]:
                self.terminate()

    def update(self):
        """
        update game here
        :return: None
        """
        raise NotImplementedError("update")

    def render(self):
        """
        render stuff here
        :return: None
        """
        raise NotImplementedError("render")

    def swapToScene(self, scene):
        """
        swaps to scene
        :param scene: Scene instance (such as Game(*args) )
        :return: None
        """
        self.next_scene = scene

    def terminate(self):
        """
        interrupts scene contructs and jumps off main loop
        :return: None
        """
        self.swapToScene(None)
