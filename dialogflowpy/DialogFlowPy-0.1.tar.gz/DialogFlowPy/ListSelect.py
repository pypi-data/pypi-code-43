from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .ListItem import ListItem
from .Image import Image
from .SelectItemInfo import SelectItemInfo

class ListSelect(MyDict):
    """
    {
      'title': string,
      'item_list': [
        {
          object(ListItem)
        }
      ]
    }
    """
    
    title: str = DictProperty('title', str)
    items: List[ListItem] = DictProperty('item_list', list)

    def build(self, title: str, *list_items:ListItem):
        for item in list_items:
            assert isinstance(item, ListItem)
            self.items.append(item)

        self.title = title

        return self

    def add_items(self, *list_items: ListItem) -> List[ListItem]:
        for item in list_items:
            assert isinstance(item, ListItem)
            self.items.append(item)
        return self.items

    def add_item(self, key: str, title: str, description:str=None, image_uri:str=None, image_text:str=None,
                 *synonyms: str) -> ListItem:

        list_item: ListItem = ListItem().build(title=title, description=description, image=Image().build(uri=image_uri,
                                                                                           accessibility_text=image_text
                                                                                                     ),
                                         info=SelectItemInfo().build(key=key, *synonyms))
        self.items.append(list_item)
        return list_item
