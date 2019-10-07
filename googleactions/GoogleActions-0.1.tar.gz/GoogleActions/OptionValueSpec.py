from PyVoice.MyDict import MyDict, DictProperty
from typing import Dict, List, Tuple, Union
from .SimpleSelect import SimpleSelect
from .ListSelect import ListSelect
from .CarouselSelect import CarouselSelect


class OptionValueSpec(MyDict):
    """
    {

      // Union field select can be only one of the following:
      'simpleSelect': {
        object(SimpleSelect)
      },
      'listSelect': {
        object(ListSelect)
      },
      'carouselSelect': {
        object(CarouselSelect)
      }
      // End of list of possible types for union field select.
    }
    """
    simple_select: SimpleSelect = DictProperty('simpleSelect', SimpleSelect)
    list_select: ListSelect = DictProperty('listSelect', ListSelect)
    carousel_select: CarouselSelect = DictProperty('carouselSelect', CarouselSelect)
    
    def build(self, option_object: Union[SimpleSelect, ListSelect, CarouselSelect]):

        if isinstance(option_object, SimpleSelect):
            self.simple_select = option_object
        elif isinstance(option_object, ListSelect):
            self.list_select = option_object
        elif isinstance(option_object, CarouselSelect):
            self.carousel_select = option_object

        return self
