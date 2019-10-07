from PyVoice.MyDict import MyDict, DictProperty


class OrderState(MyDict):
    """
    {
      "state": string,
      "label": string,
    }
    """
    state: str = DictProperty('state', str)
    label: str = DictProperty('label', str)

    def build(self, state: str=None, label: str=None):
        if state is not None:
            self.state = state
        if label is not None:
            self.label = label

        return self
