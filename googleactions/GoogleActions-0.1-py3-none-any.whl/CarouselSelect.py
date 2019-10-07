from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .CarouselItem import CarouselItem
from .Image import Image
from .OptionInfo import OptionInfo
from . import ImageDisplayOptions


class CarouselSelect(MyDict):
    """
    {
      'imageDisplayOptions': enum(ImageDisplayOptions),
      'item_list': [
        {
          object(carouselItem)
        }
      ]
    }
    """
    image_display_options: ImageDisplayOptions = DictProperty('imageDisplayOptions', ImageDisplayOptions)
    items_carousel: List[CarouselItem] = DictProperty('item_list', list)

    def build(self, image_display_options: ImageDisplayOptions, *carousel_items:CarouselItem):

        self.items_carousel = []
        for item in carousel_items:
            assert isinstance(item, CarouselItem)
            self.items_carousel.append(item)

        if image_display_options is not None:
            self.image_display_options = image_display_options
        
        return self

    def add_carousel_items(self, *carousel_items: CarouselItem) -> List[CarouselItem]:
        for item in carousel_items:
            assert isinstance(item, CarouselItem)
            self.items_carousel.append(item)
        return self.items_carousel

    def add_carousel_item(self, key: str, title: str, description:str=None, image_url:str=None, image_text:str=None,
                      image_height:int=0, image_width:int=0, *synonyms: str) -> CarouselItem:

        carousel_item = CarouselItem().build(title=title, description=description, image=Image().build(url=image_url,
                                                                                           accessibility_text=image_text,
                                                                                           height=image_height,
                                                                                           width=image_width),
                                         option_info=OptionInfo(key=key, *synonyms))
        self.items_carousel.append(carousel_item)
        return carousel_item
