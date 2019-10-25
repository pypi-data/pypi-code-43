from janis_core import File


class ZipFile(File):
    @staticmethod
    def name():
        return "Zip"

    def doc(self):
        return "A zip archive, ending with .zip"
