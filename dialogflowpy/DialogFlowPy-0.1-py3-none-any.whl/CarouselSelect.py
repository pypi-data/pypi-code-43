from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .CarouselItem import CarouselItem
from .Image import Image
from .SelectItemInfo import SelectItemInfo


class CarouselSelect(MyDict):
    """
    {
      'item_list': [
        {
          object(carouselItem)
        }
      ]
    }
    """
    items_carousel: List[CarouselItem] = DictProperty('item_list', list)

    def build(self, *carousel_items:CarouselItem):

        self.items_carousel = []
        for item in carousel_items:
            assert isinstance(item, CarouselItem)
            self.items_carousel.append(item)
        
        return self

    def add_carousel_items(self, *carousel_items: CarouselItem) -> List[CarouselItem]:
        for item in carousel_items:
            assert isinstance(item, CarouselItem)
            self.items_carousel.append(item)
        return self.items_carousel

    def add_carousel_item(self, key: str, title: str, description:str=None, image_url:str=None, image_text:str=None,
                       *synonyms: str) -> CarouselItem:

        carousel_item = CarouselItem().build(title=title, description=description, image=Image().build(url=image_url,
                                                                                           accessibility_text=image_text
                                                                                                       ),
                                         info=SelectItemInfo(key=key, *synonyms))
        self.items_carousel.append(carousel_item)
        return carousel_item
