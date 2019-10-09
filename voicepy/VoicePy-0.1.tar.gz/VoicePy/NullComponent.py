from PyVoice.ComponentsABC import ComponentsABC


class NullComponent(ComponentsABC):

    def __init__(self) -> None:
        pass

    @property
    def output(self):
        return None
