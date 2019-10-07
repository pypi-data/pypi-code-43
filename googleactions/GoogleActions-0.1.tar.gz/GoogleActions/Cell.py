from typing import List
from PyVoice.MyDict import MyDict, DictProperty


class Cell(MyDict):
    """
    {
      "text": string
    }
    """

    text: str = DictProperty('text', str)

    def build(self, text):
        self.text = text
        return self
