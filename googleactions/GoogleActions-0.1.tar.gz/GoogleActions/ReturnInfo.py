from PyVoice.MyDict import MyDict, DictProperty


class ReturnInfo(MyDict):
    """
    {
      "reason": string,
    }
    """
    
    reason: str = DictProperty('reason', str)

    def build(self, reason):
        self.reason = reason
        return self
