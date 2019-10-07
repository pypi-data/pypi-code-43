from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .SelectItem import SelectItem
from .OptionInfo import OptionInfo


class SimpleSelect(MyDict):
    """
    {
      'item_list': [
        {
          object(SelectItem)
        }
      ]
    }
    """
    items: List[SelectItem] = DictProperty('item_list', list)

    def build(self, *select_items: SelectItem):
        self.items = []
        for item in select_items:
            assert isinstance(item, SelectItem)
            self.items.append(item)

        return self

    def add_select_items(self, *select_items: SelectItem) -> List[SelectItem]:
        for item in select_items:
            assert isinstance(item, SelectItem)
            self.items.append(item)
        return self.items

    def add_select_item(self, key:str, title:str, *synonyms:str) -> SelectItem:
        select_item = SelectItem(title=title, option_info=OptionInfo(key=key, *synonyms))
        self.items.append(select_item)
        return select_item
