import re


class TemplateText:

    def __init__(self, body=""):
        self.__body = body

    def set_body_from_file(self, path):
        with open(path, 'r') as file:
            self.__body = file.read()

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, body):
        self.__body = body

    def sub(self, before, after):
        before = before.replace("(","\(").replace(")","\)")
        after = after.replace("(", "\(").replace(")", "\)")
        result = re.search(rf'{before}(.+?){after}', self.__body)
        return result.group(1)
