from CoreEngine.utility import smooth_exit


class SceneController(object):
    def __init__(self, start_scene):
        self.scene = start_scene

    def run(self):
        """
        just a simple mainloop
        :return: None
        """
        while self.scene is not None:
            self.scene.events()
            self.scene.update()
            self.scene.render()
            self.scene = self.scene.next_scene

        smooth_exit()
