from typing import List
from PyVoice.MyDict import MyDict, DictProperty


class Text(MyDict):
    """
    {
      "text": [
        string
      ]
    }
    """

    text: List[str] = DictProperty('text', list)

    def build(self, *texts: str):
        self.text = []
        for text in texts:
            self.text.append(text)

        return self
