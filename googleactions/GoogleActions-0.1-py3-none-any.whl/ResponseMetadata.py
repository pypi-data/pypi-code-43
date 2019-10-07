from PyVoice.MyDict import MyDict, DictProperty


class ResponseMetadata(MyDict):

    status: str = DictProperty('status', str)

    def build(self, status: str):
        self.status = status
        return self
