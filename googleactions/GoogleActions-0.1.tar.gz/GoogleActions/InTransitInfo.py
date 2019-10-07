from PyVoice.MyDict import MyDict, DictProperty


class InTransitInfo(MyDict):
    """
    {
      "updatedTime": string,
    }
    """

    updated_time: str = DictProperty('updatedTime', str)

    def build(self, updated_time: str=None):
        if updated_time is not None:
            self.updated_time = updated_time

        return self
