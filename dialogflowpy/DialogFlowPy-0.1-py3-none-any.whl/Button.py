from PyVoice.MyDict import MyDict, DictProperty
from .OpenUriAction import OpenUriAction


class Button(MyDict):
    """
    {
      "title": string,
      "openUriAction": {
        object(OpenUriAction)
      }
    }
    """

    text: str = DictProperty('text', str)
    open_uri_action: OpenUriAction = DictProperty('openUriAction', OpenUriAction)

    def build(self, title: str=None, open_uri_action: OpenUriAction=None):
        if title is not None:
            self.title = title
        if open_uri_action is not None:
            self.open_uri_action = open_uri_action

        return self

    def add_open_uri_action(self, uri: str = None):
        self.open_uri_action = OpenUriAction().build(uri=uri)
        return self.open_uri_action
