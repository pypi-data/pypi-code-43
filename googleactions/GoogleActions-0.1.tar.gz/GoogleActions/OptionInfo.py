from typing import List
from PyVoice.MyDict import MyDict, DictProperty


class OptionInfo(MyDict):
    """
     {
          'key': string,
          'synonyms': [
            string
          ]
        }
    """
    key: str = DictProperty('key', str)
    synonyms: List[str] = DictProperty('synonyms', list)
    
    def build(self, key: str = None, *synonyms: str):

        if key is not None:
            self.key = key

        for item in synonyms:
            self.synonyms.append(item)

        return self

    def add_synonyms(self, *synonyms: str) -> List[str]:
        for item in synonyms:
            self.synonyms.append(item)
        return self.synonyms
