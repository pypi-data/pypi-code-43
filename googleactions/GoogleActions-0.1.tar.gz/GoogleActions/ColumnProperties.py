from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from . import HorizontalAlignment


class ColumnProperties(MyDict):
    """
    {
      "header": string,
      "horizontalAlignment": enum(HorizontalAlignment)
    }
    """
    header: str = DictProperty('header', str)
    horizontal_alignment: HorizontalAlignment = DictProperty('horizontalAlignment', HorizontalAlignment)

    def build(self, header: str, horizontal_alignment: HorizontalAlignment):
        self.header = header
        self.horizontal_alignment = horizontal_alignment
        return self
