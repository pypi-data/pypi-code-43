from PyVoice.MyDict import MyDict, DictProperty
from .SimpleResponse import SimpleResponse
from .BasicCard import BasicCard
from .StructuredResponse import StructuredResponse
from .MediaResponse import MediaResponse
from .CarouselBrowse import CarouselBrowse
from .TableCard import TableCard
from .Image import Image
from .Button import Button
from . import ImageDisplayOptions
from .OrderUpdate import  OrderUpdate


class Item(MyDict):
    """
    {

      // Union field item can be only one of the following:
      "simpleResponse": {
        object(SimpleResponse)
      },
      "basicCard": {
        object(BasicCard)
      },
      "structuredResponse": {
        object(StructuredResponse)
      },
      "mediaResponse": {
        object(MediaResponse)
      },
      "carouselBrowse": {
        object(CarouselBrowse)
      },
      "tableCard": {
        object(TableCard)
      }
      // End of list of possible types for union field item.
    }
    """
    
    simple_response: SimpleResponse = DictProperty('simpleResponse', SimpleResponse)
    basic_card: BasicCard = DictProperty('basicCard', BasicCard)
    structured_response: StructuredResponse = DictProperty('structuredResponse', StructuredResponse)
    media_response: MediaResponse = DictProperty('mediaResponse', MediaResponse)
    carousel_browse: CarouselBrowse = DictProperty('carouselBrowse', CarouselBrowse)
    table_card : TableCard = DictProperty('tableCard', TableCard)

    def build(self, member_object=None):
        assert isinstance(member_object, (StructuredResponse, SimpleResponse, BasicCard, MediaResponse))
        if isinstance(member_object, SimpleResponse):
            self.simple_response = member_object
        elif isinstance(member_object, BasicCard):
            self.basic_card = member_object
        elif isinstance(member_object, StructuredResponse):
            self.structured_response = member_object
        elif isinstance(member_object, MediaResponse):
            self.media_response = member_object
        elif isinstance(member_object, CarouselBrowse):
            self.carousel_browse = member_object
        elif isinstance(member_object, TableCard):
            self.table_card = member_object

        return self

    def add(self, member_object):
        if isinstance(member_object, SimpleResponse):
            self.simple_response = member_object
        elif isinstance(member_object, BasicCard):
            self.basic_card = member_object
        elif isinstance(member_object, StructuredResponse):
            self.structured_response = member_object
        elif isinstance(member_object, MediaResponse):
            self.media_response = member_object
        elif isinstance(member_object, CarouselBrowse):
            self.carousel_browse = member_object
        elif isinstance(member_object, TableCard):
            self.table_card = member_object

        return self

    def add_simple_response(self, text_to_speech: str, ssml: str, display_text: str) -> SimpleResponse:
        self.simple_response = SimpleResponse().build(text_to_speech=text_to_speech, ssml=ssml,
                                                      display_text=display_text)

        return self.simple_response

    def add_basic_card(self, title: str=None, formatted_text:str=None, subtitle:str=None, image: Image=None,
                       image_display_options: ImageDisplayOptions=None, *buttons:Button) -> BasicCard:

        self.basic_card = BasicCard().build(title=title, formatted_text=formatted_text,
                                        subtitle=subtitle, image=image,
                                        image_display_options=image_display_options, *buttons)

        return self.basic_card

