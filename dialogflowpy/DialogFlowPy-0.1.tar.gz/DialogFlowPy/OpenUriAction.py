from PyVoice.MyDict import MyDict, DictProperty


class OpenUriAction(MyDict):
    """"
        {
      "uri": string
    }
    """

    uri: str = DictProperty('uri', str)

    def build(self, uri: str):
        self.uri = uri
        return self
