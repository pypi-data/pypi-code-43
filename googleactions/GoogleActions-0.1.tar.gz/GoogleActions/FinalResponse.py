from typing import List
from .RichResponse import RichResponse
from .LinkOutSuggestion import LinkOutSuggestion
from .Suggestion import Suggestion
from .Item import Item
from . import ImageDisplayOptions, MediaType
from .MediaObject import MediaObject
from PyVoice.MyDict import MyDict, DictProperty


class FinalResponse(MyDict):
    """
    {
      "richResponse": {
        object(RichResponse)
      },
    }
    """

    rich_response: RichResponse = DictProperty('richResponse', RichResponse)

    def build(self, rich_response: RichResponse=None):
        self.rich_response = rich_response
        return RichResponse

    def add_rich_response(self, items_list: List[Item] = None, suggestions_list: List[Suggestion] = None,
                          link_out_suggestion: LinkOutSuggestion = None) -> RichResponse:

        self.rich_response = RichResponse(items_list=items_list, suggestions_list=suggestions_list,
                                           link_out_suggestion=link_out_suggestion)

        return self.rich_response
