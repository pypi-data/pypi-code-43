from PyVoice.MyDict import MyDict, DictProperty


class LinkOutSuggestion(MyDict):
    """
    {
      "destinationName": string,
      "url": string,
    }
    """
    destination_name: str = DictProperty('destinationName', str)
    url: str = DictProperty('url', str)

    def build(self, url:str=None, destination_name:str=None):
        self.url = url
        self.destination_name = destination_name
        return self
