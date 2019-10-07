from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .ListItem import ListItem
from .Image import Image
from .OptionInfo import OptionInfo


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

    def add_list_items(self, *list_items: ListItem) -> List[ListItem]:
        for item in list_items:
            assert isinstance(item, ListItem)
            self.items.append(item)
        return self.items

    def add_list_item(self, key: str, title: str, description:str=None, image_url:str=None, image_text:str=None,
                      image_height:int=0, image_width:int=0, *synonyms: str) -> bool:


        self.items.append(ListItem().build(title=title, description=description, image=Image().build(url=image_url,
                                                                                           accessibility_text=image_text,
                                                                                           height=image_height,
                                                                                           width=image_width),
                                         option_info=OptionInfo().build(key=key, *synonyms)))
        return True
