from . import ReasonType
from PyVoice.MyDict import MyDict, DictProperty


class RejectionInfo(MyDict):
    """
    {
      "type": enum(ReasonType),
      "reason": string,
    }
    """

    type: str = DictProperty('type', ReasonType)
    reason: str = DictProperty('reason', str)

    def build(self, type: ReasonType, reason: str):

        self.type = type
        self.reason = reason
        
        return self
