from PyVoice.MyDict import MyDict, DictProperty
from typing import List
from .RichResponse import RichResponse
from .Item import Item
from .Suggestion import Suggestion
from .LinkOutSuggestion import LinkOutSuggestion
from . import ImageDisplayOptions, MediaType
from .MediaObject import MediaObject
from .ExpectedIntent import ExpectedIntent
from .Extension import Extension
from .Button import Button


class Google(MyDict):
    """Google data component to be added to DialogFlowOutput
    {
        'expectUserResponse': boolean,
        'userStorage': string
        'richResponse': GoogleRichResponse,
        'systemIntent': GoogleExpectedIntent,
    }

    """

    expect_user_response: bool = DictProperty('expectUserResponse', bool)
    user_storage: str = DictProperty('userStorage', str)
    rich_response: RichResponse = DictProperty('richResponse', RichResponse)
    system_intent: ExpectedIntent = DictProperty('systemIntent', ExpectedIntent)

    def build(self, expect_user_response: bool = True, rich_response: RichResponse = None, user_storage: str=None,
                 system_intent: ExpectedIntent=None):
        if expect_user_response is not None:
            self.expect_user_response = expect_user_response
        if rich_response is not None:
            self.rich_response = rich_response
        if system_intent is not None:
            self.possible_intent = system_intent
        if user_storage is not None:
            self.user_storage = user_storage

        return self

    def add_rich_response(self, items_list: List[Item] = None, suggestions: List[Suggestion] = None, link_name:str=None,
                          link_url:str=None) -> RichResponse:

        self.rich_response = RichResponse().build(item_list=items_list, suggestions=suggestions,
                                                  link_out_suggestion=LinkOutSuggestion().build(url=link_url,
                                                                                        destination_name=link_name))
        return self.rich_response

    def add_system_intent(self, intent: str = None, parameter_name: str = None, input_value:Extension=None)\
            -> ExpectedIntent:

        self.system_intent = ExpectedIntent().build(intent=intent, parameter_name=parameter_name,
                                                    input_value=input_value)
        return self.system_intent

    def add_items(self, *items) -> RichResponse:
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_items(*items)
        return self.rich_response

    def add_simple_response(self, text_to_speech: str, ssml: str, display_text: str) -> RichResponse:
        print('self.rich_response: ', self.rich_response)
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_simple_response(text_to_speech=text_to_speech, ssml=ssml, display_text=display_text)
        print('self.rich_response: ', self.rich_response)
        return self.rich_response

    def add_basic_card(self, title: str, formatted_text: str, subtitle: str, image_url: str,
                       image_text: str, image_height: int, image_width: int,
                       image_display_options: ImageDisplayOptions, *buttons: Button) -> RichResponse:

        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_basic_card(title=title, formatted_text=formatted_text, subtitle=subtitle,
                                          image_url=image_url, image_text=image_text,image_height=image_height,
                                          image_width=image_width, image_display_options=image_display_options,
                                          *buttons)

        return self.rich_response

    def add_structured_response(self, receipt=None, info_extension=None,
                                return_info=None,
                                user_notification=None, rejection_info=None, update_time=None,
                                line_item_updates=None, fulfillment_info=None,
                                total_price=None,
                                in_transit_info=None, action_order_id=None,
                                cancellation_info=None,
                                order_state=None, google_order_id=None,
                                order_management_actions_list=None) -> RichResponse:
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_structured_response(receipt=receipt, info_extension=info_extension,
                                                   return_info=return_info, user_notification=user_notification,
                                                   rejection_info=rejection_info, update_time=update_time,
                                                   line_item_updates=line_item_updates,
                                                   fulfillment_info=fulfillment_info, total_price=total_price,
                                                   in_transit_info=in_transit_info, action_order_id=action_order_id,
                                                   cancellation_info=cancellation_info, order_state=order_state,
                                                   google_order_id=google_order_id,
                                                   order_management_actions_list=order_management_actions_list)
        return self.rich_response

    def add_media_response(self, media_type: MediaType, *media_objects: MediaObject) -> RichResponse:
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.add_media_response(media_type=media_type, *media_objects)
        return self.rich_response

    def add_suggestions(self, *titles) -> RichResponse:
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_suggestions(*titles)
        return self.rich_response

    def add_link_out_suggestion(self, url: str, destination_name: str) -> RichResponse:
        if self.rich_response is None:
            self.rich_response = RichResponse().build()
        self.rich_response.add_link_out_suggestion(url=url, destination_name=destination_name)
        return self.rich_response

