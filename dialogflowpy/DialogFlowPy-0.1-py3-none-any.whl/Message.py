from typing import List, Union
from PyVoice.MyDict import MyDict, DictProperty
from .Text import Text
from .Image import Image
from .QuickReplies import QuickReplies
from .Card import Card
from .SimpleResponse import SimpleResponse
from .BasicCard import BasicCard
from .Suggestions import Suggestions
from .LinkOutSuggestion import LinkOutSuggestion
from .ListSelect import ListSelect
from .CarouselSelect import CarouselSelect
from PyVoice.GoogleActions.Google import Google


class Message(MyDict):
    """
    {
      "platform": enum(Platform),

      // Union field message can be only one of the following:
      "text": {
        object(Text)
      },
      "image": {
        object(Image)
      },
      "quickReplies": {
        object(QuickReplies)
      },
      "card": {
        object(Card)
      },
      "payload": {
        object
      },
      "simpleResponses": {
        object(SimpleResponses)
      },
      "basicCard": {
        object(BasicCard)
      },
      "suggestions": {
        object(Suggestions)
      },
      "linkOutSuggestion": {
        object(LinkOutSuggestion)
      },
      "listSelect": {
        object(ListSelect)
      },
      "carouselSelect": {
        object(CarouselSelect)
      }
      // End of list of possible types for union field message.
    }
    """

    text: Text = DictProperty('text', Text)
    image: Image = DictProperty('image', Image)
    quick_replies: QuickReplies = DictProperty('quickReplies', QuickReplies)
    card: Card = DictProperty('card', Card)
    payload: Google = DictProperty('payload', Google)
    simple_responses: SimpleResponse = DictProperty('simpleResponses', SimpleResponse)
    basic_card: BasicCard = DictProperty('basicCard', BasicCard)
    suggestions: Suggestions = DictProperty('suggestions', Suggestions)
    link_out_suggestion: LinkOutSuggestion = DictProperty('linkOutSuggestion', LinkOutSuggestion)
    list_select: ListSelect = DictProperty('listSelect', ListSelect)
    carousel_select: CarouselSelect = DictProperty('carouselSelect', CarouselSelect)

    def build(self, object: Union[Text, Image, QuickReplies, Card, Google, SimpleResponse, BasicCard, Suggestions,
                                  LinkOutSuggestion, ListSelect, CarouselSelect]):
        if isinstance(object, Text):
            self.text = object
        elif isinstance(object, Image):
            self.image = object
        elif isinstance(object, QuickReplies):
            self.quick_replies = object
        elif isinstance(object, Card):
            self.card = object
        elif isinstance(object, Google):
            self.payload = object
        elif isinstance(object, SimpleResponse):
            self.simple_responses = object
        elif isinstance(object, BasicCard):
            self.basic_card = object
        elif isinstance(object, Suggestions):
            self.suggestions = object
        elif isinstance(object, LinkOutSuggestion):
            self.link_out_suggestion = object
        elif isinstance(object, ListSelect):
            self.list_select = object
        elif isinstance(object, CarouselSelect):
            self.carousel_select = object

        return self
