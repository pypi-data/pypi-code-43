from typing import List, Union
from PyVoice.MyDict import MyDict, DictProperty
from .CarouselItem import CarouselItem
from . import ImageDisplayOptions, OptionInfo
from .Image import Image


class CarouselBrowse(MyDict):
    """
    {
      "item_list": [
        {
          object(Item)
        }
      ],
      "imageDisplayOptions": enum(ImageDisplayOptions)
    }
    """

    items: List[CarouselItem] = DictProperty('item_list', list)
    image_display_options: ImageDisplayOptions = DictProperty('imageDisplayOptions', ImageDisplayOptions)

    def build(self, image_display_options: ImageDisplayOptions, *items:CarouselItem):

        self.image_display_options = image_display_options
        self.items = items

        return self

    def add_items(self, *items: CarouselItem) -> List[CarouselItem]:
        for item in items:
            assert isinstance(item, CarouselItem)
            self.items.append(item)

        return self.items

    def add_item(self, title: str = None, description: str=None, image_url: str=None, image_text: str=None,
                 image_height: int=0, image_width: int=0, option_info: OptionInfo=None) \
            -> CarouselItem:
        item = CarouselItem().build(title=title, description=description,
                                    image=Image().build(url=image_url, accessibility_text=image_text,
                                                        height=image_height, width=image_width),option_info=option_info)
        return item
