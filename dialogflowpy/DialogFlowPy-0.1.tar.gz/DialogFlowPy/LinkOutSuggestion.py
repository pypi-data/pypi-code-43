from PyVoice.MyDict import MyDict, DictProperty


class LinkOutSuggestion(MyDict):
    """
    {
      "destinationName": string,
      "uri": string,
    }
    """
    destination_name: str = DictProperty('destinationName', str)
    uri: str = DictProperty('uri', str)

    def build(self, uri: str=None, destination_name: str=None):
        self.uri = uri
        self.destination_name = destination_name
        return self
