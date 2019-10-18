from typing import *

CSSColor = Text

WebSocketDataType = Union["message", "reload_browser", "refresh_chat_menu", "error", "refresh", "uploaded_file", "delivered", "readed"]


class ChatData:
    def __init__(self, kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

    channel: Text
    date: Text
    guid: Optional[Text]
    host: Text
    message: Optional[Text]
    message_state_delivered_id: int
    message_state_delivered_name: Text
    message_state_new_id: int
    message_state_new_name: Text
    message_state_readed_id: int
    message_state_readed_name: Text
    path: Text
    port: int
    props: int
    theme_ids: List[int]
    type: WebSocketDataType
    user__color: Text
    user__full_name: Text
    user__short_name: Text
    user_id: int


class ChatResponseData(Dict):
    channel: Text
    date: Text
    guid: Text
    host: Text
    message: Text
    port: Text
    state__name: Optional[Text]
    to_whom_id: Optional[int]
    type: WebSocketDataType
    user__color: CSSColor
    user__short_name: Text
    user_id: int


FREQUENCY_OF_POLLING_UNREAD_MESSAGES = 1000 * 60 * 3
