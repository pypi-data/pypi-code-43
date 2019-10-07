from PyVoice.MyDict import MyDict, DictProperty


class UserNotification(MyDict):
    """
    {
      "title": string,
      "text": string,
    }
    """
    title: str = DictProperty('title', str)
    text: str = DictProperty('text', str)

    def build(self, text: str=None, title: str=None):
        self.text = text
        self.title = title
