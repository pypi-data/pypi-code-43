from PyVoice.MyDict import MyDict, DictProperty


class CancellationInfo(MyDict):
    """
    {
      "reason": string,
    }
    """
    reason: str = DictProperty('reason', str)
    
    def build(self, reason:str =None):
        if reason is not None:
            self.reason = reason

        return self
