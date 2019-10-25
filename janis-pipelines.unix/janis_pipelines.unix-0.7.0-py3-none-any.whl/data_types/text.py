from janis_core import File


class TextFile(File):
    def __init__(self, optional=False, extension=".txt"):
        super().__init__(optional, extension=extension)

    @staticmethod
    def name():
        return "TextFile"

    def doc(self):
        return "A textfile, ending with .txt"
