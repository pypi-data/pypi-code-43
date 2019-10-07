from PyVoice.MyDict import MyDict, DictProperty


class Suggestion(MyDict):
    """
    {
      "title": string,
    }
    """
    
    title: str = DictProperty('title', str)

    def build(self, title: str):
        self.title = title
        return self
