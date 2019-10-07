from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .FinalResponse import FinalResponse
from .ExpectedInput import ExpectedInput
from .CustomPushMessage import CustomPushMessage
from .RichResponse import RichResponse
from .InputPrompt import InputPrompt
from .ExpectedIntent import ExpectedIntent
from .LinkOutSuggestion import LinkOutSuggestion
from .OrderUpdate import OrderUpdate
from .UserNotification import UserNotification
from .Target import Target


class AppResponse(MyDict):
    """
    {
      "conversationToken": string,
      "userStorage": string,
      "resetUserStorage": boolean,
      "expectUserResponse": boolean,
      "expectedInputs": [
        {
          object(ExpectedInput)
        }
      ],
      "finalResponse": {
        object(FinalResponse)
      },
      "customPushMessage": {
        object(CustomPushMessage)
      },
      "isInSandbox": boolean,
    }
    """

    conversation_token: str = DictProperty('conversationToken', str)
    user_storage: str = DictProperty('userStorage', str)
    reset_user_storage: bool = DictProperty('resetUserStorage', bool)
    expect_user_response: bool = DictProperty('expectUserResponse', bool)
    expected_inputs: List[ExpectedInput] = DictProperty('expectedInputs', list)
    final_response: FinalResponse = DictProperty('finalResponse', FinalResponse)
    custom_push_message: CustomPushMessage = DictProperty('customPushMessage', CustomPushMessage)
    is_in_sandbox: bool = DictProperty('isInSandbox', bool)

    def build(self, conversation_token=None, user_storage: str = None, reset_user_storage: bool = False,
              expect_user_response: bool = True, final_response: FinalResponse = None, is_in_sandbox: bool = False,
              custom_push_message: CustomPushMessage = None, *expected_inputs: ExpectedInput):

        for item in expected_inputs:
            assert isinstance(item, ExpectedInput)
            self.expected_inputs = expected_inputs

        if final_response is not None:
            self.final_response = final_response

        if user_storage is not None:
            self.user_storage = user_storage

        self.reset_user_storage = reset_user_storage
        self.is_in_sandbox = is_in_sandbox
        self.expect_user_response = expect_user_response

        if conversation_token is not None:
            self.conversation_token = conversation_token

        if custom_push_message is not None:
            self.custom_push_message = custom_push_message

        return self

    def add_expected_inputs(self, *expected_inputs) -> List[ExpectedInput]:
        for item in expected_inputs:
            assert isinstance(item, ExpectedInput)
            self.expected_inputs.append(item)

        return self.expected_inputs

    def add_expected_input(self, speech_biasing_hints_list: List[str] = None, input_prompt: InputPrompt = None,
                           possible_intents_list: List[ExpectedIntent] = None) -> ExpectedInput:
        expected_input = ExpectedInput().build(speech_biasing_hints_list=speech_biasing_hints_list,
                                               input_prompt=input_prompt, possible_intents_list=possible_intents_list)
        return expected_input

    def add_final_response(self, items_list: list = None, suggestions: list = None,
                           link_out_suggestion: LinkOutSuggestion = None) -> FinalResponse:
        self.final_response = FinalResponse().build(rich_response=RichResponse().build(item_list=items_list,
                                                                                       suggestions=suggestions,
                                                                                       link_out_suggestion=
                                                                                       link_out_suggestion))
        return self.final_response

    def add_custom_push_message(self, order_update:OrderUpdate=None, user_notification:UserNotification=None,
                                target:Target=None) -> CustomPushMessage:
        self.custom_push_message = CustomPushMessage().build(order_update=order_update,
                                                             user_notification=user_notification,
                                                             target=target)
        return self.custom_push_message
