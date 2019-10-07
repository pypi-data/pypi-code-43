from typing import List
from PyVoice.VoicePlatformABC import VoicePlatformABC
from .Context import Context
from .Message import Message
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
from .EventInput import EventInput
from PyVoice.GoogleActions.Google import Google
from .CarouselItem import CarouselItem
from .ListItem import ListItem
from .Suggestion import Suggestion
from .Button import Button


class DialogFlow(VoicePlatformABC):
    """

    Main class to handle interface with google actions
    Dialogflow Request:
    {
  "responseId": "c4b863dd-aafe-41ad-a115-91736b665cb9",
  "queryResult": {
    "queryText": "GOOGLE_ASSISTANT_WELCOME",
    "action": "input.welcome",
    "parameters": {},
    "allRequiredParamsPresent": true,
    "fulfillmentText": "",
    "fulfillmentMessages": [],
    "outputContexts": [
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/google_assistant_welcome"
      },
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/actions_capability_screen_output"
      },
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/google_assistant_input_type_voice"
      },
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/actions_capability_audio_output"
      },
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/actions_capability_web_browser"
      },
      {
        "name": "projects/${PROJECTID}/agent/sessions/${SESSIONID}/contexts/actions_capability_media_response_audio"
      }
    ],
    "intent": {
      "name": "projects/${PROJECTID}/agent/intents/8b006880-0af7-4ec9-a4c3-1cc503ea8260",
      "displayName": "Default Welcome Intent"
    },
    "intentDetectionConfidence": 1,
    "diagnosticInfo": {},
    "languageCode": "en-us"
  },
  "originalDetectIntentRequest": {
    "source": "google",
    "version": "2",
    "payload": {
      "isInSandbox": true,
      "surface": {
        "capabilities": [
          {
            "name": "actions.capability.SCREEN_OUTPUT"
          },
          {
            "name": "actions.capability.AUDIO_OUTPUT"
          },
          {
            "name": "actions.capability.WEB_BROWSER"
          },
          {
            "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
          }
        ]
      },
      "inputs": [
        {
          "rawInputs": [
            {
              "query": "query from the user",
              "inputType": "KEYBOARD"
            }
          ],
          "arguments": [
            {
              "rawText": "query from the user",
              "textValue": "query from the user",
              "name": "text"
            }
          ],
          "intent": "actions.intent.TEXT"
        }
      ],
      "user": {
        "lastSeen": "2018-03-16T22:08:48Z",
        "permissions": [
          "UPDATE"
        ],
        "locale": "en-US",
        "userId": "ABwppHEvwoXs18xBNzumk18p5h02bhRDp_riW0kTZKYdxB6-LfP3BJRjgPjHf1xqy1lxqS2uL8Z36gT6JLXSrSCZ"
      },
      "conversation": {
        "conversationId": "${SESSIONID}",
        "type": "NEW"
      },
      "availableSurfaces": [
        {
          "capabilities": [
            {
              "name": "actions.capability.SCREEN_OUTPUT"
            },
            {
              "name": "actions.capability.AUDIO_OUTPUT"
            }
          ]
        }
      ]
    }
  },
  "session": "projects/${PROJECTID}/agent/sessions/${SESSIONID}"
}

    Dialogflow response:
    {
      "fulfillmentText": string,
      "fulfillmentMessages": [
        {
          object(Message)
        }
      ],
      "source": string,
      "payload": {
        object
      },
      "outputContexts": [
        {
          object(Context)
        }
      ],
      "followupEventInput": {
        object(EventInput)
      }
    }
    """

    def __init__(self, request_data_json: dict, version: str='v1'):
        print('initializing Dialogflow with: ', request_data_json)
        assert isinstance(request_data_json, dict)
        super(DialogFlow, self).__init__(request_data_json)

        self._session_id = request_data_json.get('session')
        print('session_id : ', self._session_id)

        self._result = request_data_json.get('queryResult') or request_data_json.get('result')
        print('result: ', self._result)

        self._parameters = self._result.get('parameters')
        print('parameters: ', self._parameters)

        self._action = self._result.get('action')
        if self._action == 'input.welcome':
            self._action = 'welcome'
        print('action: ', self._action)

        self._context: List[Context] = []
        contexts = self._result.get('outputContexts') or self._result.get('contexts')
        for context in contexts:
            context_object = Context()._from(context)
            if context_object.lifespan_count is not None:
                self._context.append(context_object)
        print('context: ', self._context)

        self._max_msg_length = 550
        self._fullfillment_messages: List[Message] = []
        self._source: str = None
        self._payload_type = None
        self._payload = None
        self._followup_event_input: EventInput = None

    @property
    def payload(self):
        return self._payload

    @property
    def contexts(self) -> List[Context]:
        return self._context

    @property
    def source(self) -> str:
        return self._source

    def add_fullfillment_messages(self, *messages: Message) -> List[Message]:
        for item in messages:
            self._fullfillment_messages.append(item)
        return self._fullfillment_messages

    def delete_messages(self):
        self._fullfillment_messages = []
        return self

    def add_text_message(self, text) -> Text:
        self._message = text
        text = Text().build(self.decorated_message)
        self._fullfillment_messages.append(Message().build(text))
        return text

    def add_image(self, uri: str = None, accessibility_text: str = None) -> Image:
        image = Image().build(uri=uri, accessibility_text=accessibility_text)
        self._fullfillment_messages.append(Message().build(image))
        return image

    def add_quick_reply(self, title, *quick_replies: str) -> QuickReplies:
        quick_reply: QuickReplies = QuickReplies().build(title=title)
        quick_reply.add_quick_replies(*quick_replies)
        self._fullfillment_messages.append(Message().build(quick_reply))
        return quick_reply

    def add_card(self, title: str, subtitle: str, image_uri: str, *buttons: Button) -> Card:
        card: Card = Card().build(title=title, subtitle=subtitle, image_uri=image_uri, *buttons)
        self._fullfillment_messages.append(Message().build(card))
        return card

    def add_payload(self, payload_type: str, payload):
        self._payload_type = payload_type
        self._payload = payload
        return self._payload

    def add_simple_response(self, text_to_speech: str = None, ssml: str = None, display_text: str = None) \
            -> SimpleResponse:
        simple_response: SimpleResponse = SimpleResponse().build(text_to_speech=text_to_speech, ssml=ssml,
                                                                 display_text=display_text)
        self._fullfillment_messages.append(Message().build(simple_response))
        return simple_response

    def add_basic_card(self, title: str = None, formatted_text: str = None, subtitle: str = None, image_uri: str=None,
                       image_text: str=None, *buttons: Button) -> BasicCard:
        basic_card: BasicCard = BasicCard().build(title=title, formatted_text=formatted_text, subtitle=subtitle,
                                                  image=Image().build(uri=image_uri, accessibility_text=image_text),
                                                  *buttons)
        self._fullfillment_messages.append(Message().build(basic_card))
        return basic_card

    def add_suggestions(self, *titles: str) -> Suggestions:
        suggestions_list: List[Suggestion] = [Suggestion().build(title=item) for item in titles]
        suggestions: Suggestions = Suggestions().build(*suggestions_list)
        self._fullfillment_messages.append(Message().build(suggestions))
        return suggestions

    def add_link_out_suggestion(self, uri: str, destination_name: str) -> LinkOutSuggestion:
        link_out_suggestion: LinkOutSuggestion = LinkOutSuggestion().build(uri=uri, destination_name=destination_name)
        self._fullfillment_messages.append(Message().build(link_out_suggestion))
        return link_out_suggestion

    def add_list_select(self, title: str, *list_items:ListItem) -> ListSelect:
        list_select: ListSelect = ListSelect().build(title=title, *list_items)
        self._fullfillment_messages.append(Message().build(list_select))
        return list_select

    def add_carousel_select(self, *carousel_items: CarouselItem) -> CarouselSelect:
        carousel_select: CarouselSelect = CarouselSelect().build(*carousel_items)
        self._fullfillment_messages.append(Message().build(carousel_select))
        return carousel_select

    def add_source(self, source: str):
        assert isinstance(source, str)
        self._source = source
        return self

    def add_context(self, context_name: str, lifespan: int = 0, **parameters) -> List[Context]:
        assert isinstance(context_name, str)
        assert isinstance(lifespan, int)

        for context in self._context:
            if context.name == context_name:
                context.update_parameters(**parameters)
                context.lifespan = lifespan
                return self._context

        self._context.append(Context().build(name=context_name, lifespan_count=lifespan, **parameters))
        print('context: ', self._context)
        return self._context

    def update_context(self, context_name: str, lifespan:int=0, **parameters) -> List[Context]:
        assert isinstance(context_name, str)
        assert isinstance(lifespan, int)

        for context in self._context:
            if context.name == context_name:
                context.lifespan_count = lifespan
                context.update_parameters(**parameters)

        return self._context

    def delete_context(self, *context_names) -> bool:

        if len(context_names) == 0:
            self._context = list()

        else:
            for context_name in context_names:
                assert isinstance(context_name, str)

                for context in self._context:
                    if context.name == context_name:
                        self._context.remove(context)

        return True

    @property
    def output(self) -> dict:

        return {
            "fulfillmentText": self.decorated_message,
            "fulfillmentMessages": self._fullfillment_messages,
            "source": self._source,
            "payload": self._payload,
            "outputContexts": [item for item in self._context],
            "followupEventInput": self._followup_event_input
        }
