from PyVoice.MyDict import MyDict, DictProperty
from .OptionInfo import OptionInfo


class SelectItem(MyDict):
    """
    {
      'optionInfo': object(optioninfo),
      'title': string
    }
    """
    
    option_info: OptionInfo = DictProperty('optionInfo', OptionInfo)
    title: str = DictProperty('title', str)

    def build(self, title: str = None, option_info: OptionInfo=None):

        self.option_info = option_info
        self.title = title
        return self

    def add_option_info(self, key:str, *synonyms:str) -> OptionInfo:
        self.option_info = OptionInfo().build(key=key, *synonyms)
        return self.option_info
