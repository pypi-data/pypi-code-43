from PyVoice.MyDict import MyDict, DictProperty
from typing import List


class SelectItemInfo(MyDict):
    """
    {
      "key": string,
      "synonyms": [
        string
      ]
    }
    """

    key: str = DictProperty('key', str)
    synonyms: List[str] = DictProperty('synonyms', list)

    def build(self, key: str, *synonyms: str):

        self.key = key
        self.synonyms = []
        self.synonyms.extend(synonyms)
        return self

    def add_synonyms(self, *synonyms: str) -> List[str]:

        self.synonyms.extend(synonyms)
        return self.synonyms
