import re
from lupin import Schema, fields as f, validators as v, Mapper, bind
from lupin.processors import strip
from .constants import *
from .models import *
from .validators import ObjectID, IsRegexp
from .processors import html_sanitize, unicode_normalize
from .fields import RegexpField
from .custom_schemas import MatchIntentConditionSchema, CustomerSatisfactionChoiceSchema

_OBJECT_ID_VALIDATOR = ObjectID()

#
# Conditions
#
PREDICATE_MESSAGE_GETTER = Schema(
    {"type": f.Constant("message", read_only=True)}, name="predicate_message_getter"
)

PREDICATE_SESSION_VALUE_GETTER = Schema(
    {
        "type": f.Constant("session_value", read_only=True),
        "key": f.String(
            validators=(
                v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_KEY_MAX_LENGTH)
                & v.Match(re.compile(r"^[\w\d_]+$"))
            )
        ),
    },
    name="predicate_session_value_getter",
)

PREDICATE_USER_ATTRIBUTE_GETTER = Schema(
    {
        "type": f.Constant("user_attribute", read_only=True),
        "key": f.String(
            validators=(
                v.Length(min=1, max=SET_USER_ATTRIBUTE_ACTION_KEY_MAX_LENGTH)
                & v.Match(re.compile(r"^[\w\d_]+$"))
            )
        ),
    },
    name="predicate_user_attribute_getter",
)

IS_NOT_SET_CONDITION = Schema(
    {"type": f.Constant("is_not_set", read_only=True)}, name="is_not_set_condition"
)

IS_SET_CONDITION = Schema({"type": f.Constant("is_set", read_only=True)}, name="is_set_condition")

CONTAIN_CONDITION = Schema(
    {"type": f.Constant("contains", read_only=True), "values": f.List(f.String())},
    name="contain_condition",
)

EQUALS_CONDITION = Schema(
    {"type": f.Constant("equals", read_only=True), "expected": f.String()}, name="equals_condition"
)

MATCH_REGEXP_CONDITION = Schema(
    {
        "type": f.Constant("match_regexp", read_only=True),
        "pattern": RegexpField(binding="regexp", validators=IsRegexp()),
    },
    name="match_regexp_condition",
)

MATCH_INTENT_CONDITION_INTENT = Schema(
    {
        "type": f.Constant("intent", read_only=True),
        "id": f.String(validators=ObjectID()),
        "name": f.String(read_only=True),
    },
    name="match_intent_condition_intent",
)

MATCH_INTENT_CONDITION = MatchIntentConditionSchema(
    {
        "type": f.Constant("match_intent", read_only=True),
        "intent": f.Object(MATCH_INTENT_CONDITION_INTENT),
    },
    name="match_intent_condition",
)

IS_LESS_THAN_CONDITION = Schema(
    {"maximum": f.Number(), "type": f.Constant("is_less_than", read_only=True)},
    name="is_less_than_condition",
)

IS_LESS_THAN_OR_EQUAL_CONDITION = Schema(
    {"maximum": f.Number(), "type": f.Constant("is_less_than_or_equal", read_only=True)},
    name="is_less_than_or_equal_condition",
)

IS_GREATER_THAN_CONDITION = Schema(
    {"minimum": f.Number(), "type": f.Constant("is_greater_than", read_only=True)},
    name="is_greater_than_condition",
)

IS_GREATER_THAN_OR_EQUAL_CONDITION = Schema(
    {"minimum": f.Number(), "type": f.Constant("is_greater_than_or_equal", read_only=True)},
    name="is_greater_than_or_equal_condition",
)

IS_NUMBER_CONDITION = Schema(
    {"type": f.Constant("is_number", read_only=True)}, name="is_number_condition"
)


#
# Targets
#
STEP_TARGET = Schema(
    {
        "id": f.String(binding="step_id", validators=_OBJECT_ID_VALIDATOR),
        "type": f.Constant(value="step", read_only=True),
        "name": f.String(optional=True, allow_none=True),
    },
    name="step_target",
)

STORY_TARGET = Schema(
    {
        "id": f.String(binding="story_id", validators=_OBJECT_ID_VALIDATOR),
        "type": f.Constant(value="story", read_only=True),
        "name": f.String(optional=True, allow_none=True),
    },
    name="story_target",
)

ACTIONS_BLOCK_TARGET = Schema(
    {
        "id": f.String(binding="actions_block_id", validators=_OBJECT_ID_VALIDATOR),
        "type": f.Constant(value="actions_block", read_only=True),
        "name": f.String(optional=True, allow_none=True),
    },
    name="actions_block_target",
)


#
# Flow connections
#

FLOW_CONNECTION_PREDICATE = Schema(
    {
        "type": f.Constant("connection_predicate", read_only=True),
        "condition": f.PolymorphicObject(
            on="type",
            schemas={
                "is_not_set": IS_NOT_SET_CONDITION,
                "is_set": IS_SET_CONDITION,
                "contains": CONTAIN_CONDITION,
                "equals": EQUALS_CONDITION,
                "match_regexp": MATCH_REGEXP_CONDITION,
                "match_intent": MATCH_INTENT_CONDITION,
                "is_less_than": IS_LESS_THAN_CONDITION,
                "is_less_than_or_equal": IS_LESS_THAN_OR_EQUAL_CONDITION,
                "is_greater_than": IS_GREATER_THAN_CONDITION,
                "is_greater_than_or_equal": IS_GREATER_THAN_OR_EQUAL_CONDITION,
                "is_number": IS_NUMBER_CONDITION,
            },
        ),
        "valueGetter": f.PolymorphicObject(
            on="type",
            binding="value_getter",
            schemas={
                "message": PREDICATE_MESSAGE_GETTER,
                "session_value": PREDICATE_SESSION_VALUE_GETTER,
                "user_attribute": PREDICATE_USER_ATTRIBUTE_GETTER,
            },
        ),
    },
    name="flow_connection_predicate",
)

FLOW_CONNECTION = Schema(
    {
        "type": f.Constant("flow_connection", read_only=True),
        "target": f.PolymorphicObject(
            on="type", schemas={"story": STORY_TARGET, "step": STEP_TARGET}
        ),
        "predicates": f.List(
            f.Object(FLOW_CONNECTION_PREDICATE),
            validators=v.Length(min=1, max=FLOW_CONNECTION_MAX_PREDICATES_COUNT),
        ),
    },
    name="flow_connection",
)


#
# Button actions
#
GO_TO_ACTION = Schema(
    {
        "type": f.Constant(value="go_to_action", read_only=True),
        "target": f.PolymorphicObject(
            on="type", schemas={"step": STEP_TARGET, "story": STORY_TARGET}
        ),
        "sessionValues": f.Dict(binding="session_values", optional=True, allow_none=True),
    },
    name="go_to_action",
)

CUSTOMER_SATISFACTION_CALLBACK_ACTION = Schema(
    {
        "type": f.Constant(value="customer_satisfaction_callback_action", read_only=True),
        "target": f.PolymorphicObject(
            on="type", schemas={"step": STEP_TARGET, "story": STORY_TARGET}
        ),
        "kind": f.String(validators=v.In(CUSTOMER_SATISFACTION_CHOICE_KINDS)),
    },
    name="customer_satisfaction_callback_action",
)

LEGACY_REPLY_TO_MESSAGE_ACTION = Schema(
    {
        "type": f.Constant(value="legacy_reply_to_message_action", read_only=True),
        "message": f.String(
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[html_sanitize],
        ),
    },
    name="legacy_reply_to_message_action",
)

OPEN_URL_ACTION = Schema(
    {
        "type": f.Constant(value="open_url_action", read_only=True),
        "url": f.String(
            pre_load=[strip, html_sanitize],
            validators=v.Length(min=1, max=EXTERNAL_URL_MAX_LENGTH) & v.URL(),
        ),
    },
    name="open_url_action",
)

SHARE_ACTION = Schema(
    {"type": f.Constant(value="share_action", read_only=True)}, name="share_action"
)

BUTTON_ACTIONS_SCHEMAS = {
    "go_to_action": GO_TO_ACTION,
    "legacy_reply_to_message_action": LEGACY_REPLY_TO_MESSAGE_ACTION,
    "open_url_action": OPEN_URL_ACTION,
    "share_action": SHARE_ACTION,
    "customer_satisfaction_callback_action": CUSTOMER_SATISFACTION_CALLBACK_ACTION,
}

#
# Bot actions
#
ASK_LOCATION_ACTION = Schema(
    {
        "type": f.Constant(value="ask_location_action", read_only=True),
        "message": f.String(
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[html_sanitize],
        ),
        "action": f.Object(schema=GO_TO_ACTION, binding="callback_action"),
    },
    name="ask_location_action",
)

SEND_IMAGE_ACTION = Schema(
    {
        "type": f.Constant(value="send_image_action", read_only=True),
        "imageURL": f.String(
            binding="image_url",
            pre_load=[strip, html_sanitize],
            validators=(v.Length(max=EXTERNAL_URL_MAX_LENGTH) & v.URL(schemes={"https", "http"})),
        ),
    },
    name="send_image_action",
)

SEND_TEXT_ACTION = Schema(
    {
        "type": f.Constant(value="send_text_action", read_only=True),
        "alternatives": f.List(
            f.String(
                validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
                pre_load=[html_sanitize, unicode_normalize],
            ),
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MAX_MESSAGES_COUNT),
        ),
        "text": f.String(
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
            read_only=True,
            ignore_if_null=True,
            optional=True,
        ),
    },
    name="send_text_action",
)


SEND_JS_EVENT_ACTION = Schema(
    {
        "type": f.Constant(value="send_js_event_action", read_only=True),
        "event": f.String(
            validators=v.Length(min=1, max=SEND_JS_EVENT_ACTION_EVENT_MAX_LENGTH), pre_load=[strip]
        ),
    },
    name="send_js_event_action",
)


SEND_EMAIL_ACTION = Schema(
    {
        "type": f.Constant(value="send_email_action", read_only=True),
        "fromEmail": f.String(
            binding="from_email",
            pre_load=[strip, html_sanitize],
            optional=True,
            allow_none=True,
            validators=[
                v.Length(max=SEND_EMAIL_ACTION_FROM_EMAIL_MAX_LENGTH),
                v.Match(re.compile(r"^((?!@clustaar\.).)*$", re.IGNORECASE)),
            ],
        ),
        "fromName": f.String(
            binding="from_name",
            pre_load=[strip, html_sanitize, unicode_normalize],
            optional=True,
            allow_none=True,
            validators=v.Length(max=SEND_EMAIL_ACTION_FROM_NAME_MAX_LENGTH),
        ),
        "recipient": f.String(
            pre_load=[strip, html_sanitize, unicode_normalize],
            validators=v.Length(max=SEND_EMAIL_ACTION_RECIPIENT_MAX_LENGTH),
        ),
        "subject": f.String(
            validators=v.Length(max=SEND_EMAIL_ACTION_SUBJECT_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "content": f.String(
            validators=v.Length(max=SEND_EMAIL_ACTION_CONTENT_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
    },
    name="send_email_action",
)

WAIT_ACTION = Schema(
    {
        "type": f.Constant(value="wait_action", read_only=True),
        "duration": f.Number(
            validators=v.Between(min=WAIT_ACTION_MIN_DURATION, max=WAIT_ACTION_MAX_DURATION),
            default=WAIT_ACTION_DEFAULT_DURATION,
        ),
    },
    name="wait_action",
)

PAUSE_BOT_ACTION = Schema(
    {"type": f.Constant(value="pause_bot_action", read_only=True)}, name="pause_bot_action"
)

CLOSE_INTERCOM_CONVERSATION_ACTION = Schema(
    {"type": f.Constant(value="close_intercom_conversation_action", read_only=True)},
    name="close_intercom_conversation_action",
)

ASSIGN_INTERCOM_CONVERSATION_ACTION = Schema(
    {
        "type": f.Constant(value="assign_intercom_conversation_action", read_only=True),
        "assigneeID": f.String(
            optional=True,
            allow_none=True,
            binding="assignee_id",
            pre_load=[strip],
            validators=[
                v.Length(max=ASSIGN_INTERCOM_CONVERSATION_ACTION_ASSIGNEE_ID_MAX_LENGTH),
                v.Match(re.compile(r"^\d*$")),
            ],
        ),
    },
    name="assign_intercom_conversation_action",
)

QUICK_REPLY = Schema(
    {
        "title": f.String(
            validators=v.Length(min=1, max=QUICK_REPLY_TITLE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "action": f.PolymorphicObject(
            on="type",
            schemas={
                "go_to_action": GO_TO_ACTION,
                "customer_satisfaction_callback_action": CUSTOMER_SATISFACTION_CALLBACK_ACTION,
            },
        ),
        "type": f.Constant(value="quick_reply", read_only=True, optional=True),
    },
    name="quick_reply",
)

SEND_QUICK_REPLIES_ACTION = Schema(
    {
        "type": f.Constant(value="send_quick_replies_action", read_only=True),
        "message": f.String(
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "buttons": f.List(
            f.Object(QUICK_REPLY),
            validators=v.Length(min=1, max=SEND_QUICK_REPLIES_ACTION_MAX_BUTTONS_COUNT),
        ),
    },
    name="send_quick_replies_action",
)

BUTTON = Schema(
    {
        "type": f.Constant(value="button", read_only=True),
        "title": f.String(
            validators=v.Length(min=1, max=BUTTON_TITLE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "action": f.PolymorphicObject(on="type", schemas=BUTTON_ACTIONS_SCHEMAS),
    },
    name="button",
)

CARD = Schema(
    {
        "type": f.Constant(value="card", read_only=True),
        "title": f.String(
            validators=v.Length(min=1, max=CARD_TITLE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "subtitle": f.String(
            optional=True,
            validators=v.Length(max=CARD_SUBTITLE_MAX_LENGTH),
            allow_none=True,
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "imageURL": f.String(
            optional=True,
            allow_none=True,
            binding="image_url",
            pre_load=[strip],
            validators=(
                v.Length(max=EXTERNAL_URL_MAX_LENGTH) & v.URL(schemes={"http", "https"})
                | v.Equal("")
            ),
        ),
        "url": f.String(
            optional=True,
            pre_load=[strip],
            allow_none=True,
            validators=v.Length(max=EXTERNAL_URL_MAX_LENGTH) | v.Equal(""),
        ),
        "buttons": f.List(
            f.Object(BUTTON),
            allow_none=True,
            default=(),
            optional=True,
            validators=v.Length(max=CARD_MAX_BUTTONS_COUNT),
        ),
    },
    name="card",
)

SEND_CARDS_ACTIONS = Schema(
    {
        "type": f.Constant(value="send_cards_action", read_only=True),
        "cards": f.List(
            f.Object(CARD), validators=v.Length(min=1, max=SEND_CARDS_ACTION_MAX_CARDS_COUNT)
        ),
    },
    name="send_cards_action",
)

STORE_SESSION_VALUE_ACTION = Schema(
    {
        "type": f.Constant(value="store_session_value_action", read_only=True),
        "key": f.String(
            validators=(
                v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_KEY_MAX_LENGTH)
                & v.Match(re.compile(r"^[\w\d_]+$"))
            )
        ),
        "value": f.String(
            validators=v.Length(min=1, max=STORE_SESSION_VALUE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
    },
    name="store_session_value_action",
)

SET_USER_ATTRIBUTE_ACTION = Schema(
    {
        "type": f.Constant(value="set_user_attribute_action", read_only=True),
        "key": f.String(
            validators=(
                v.Length(min=1, max=SET_USER_ATTRIBUTE_ACTION_KEY_MAX_LENGTH)
                & v.Match(re.compile(r"(?i)^(?!(id)$)[\w\d_]+$"))
            )
        ),
        "value": f.String(
            validators=v.Length(min=1, max=SET_USER_ATTRIBUTE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
    },
    name="set_user_attribute_action",
)

GOOGLE_CUSTOM_SEARCH_ACTION = Schema(
    {
        "type": f.Constant(value="google_custom_search_action", read_only=True),
        "query": f.String(
            validators=v.Length(min=1, max=GOOGLE_CUSTOM_SEARCH_ACTION_QUERY_MAX_LENGTH)
        ),
        "customEngineID": f.String(
            binding="custom_engine_id", pre_load=[strip], validators=v.Length(min=1)
        ),
        "limit": f.Int(validators=v.Between(min=1, max=GOOGLE_CUSTOM_SEARCH_ACTION_MAX_LIMIT)),
    },
    name="google_custom_search_action",
)

WEBHOOK_REQUEST_FIELD = Schema(
    {
        "type": f.Constant(value="webhook_request_field", read_only=True),
        "key": f.String(
            validators=(
                v.Length(
                    min=WEBHOOK_REQUEST_FIELD_KEY_MIN_LENGTH,
                    max=WEBHOOK_REQUEST_FIELD_KEY_MAX_LENGTH,
                )
                & v.Match(re.compile(r"^[\w\d_]+$"))
            )
        ),
        "value": f.String(
            validators=v.Length(
                min=WEBHOOK_REQUEST_FIELD_VALUE_MIN_LENGTH,
                max=WEBHOOK_REQUEST_FIELD_VALUE_MAX_LENGTH,
            )
        ),
    },
    name="webhook_request_field",
)

SEND_WEBHOOK_REQUEST_ACTION = Schema(
    {
        "type": f.Constant(value="send_webhook_request_action", read_only=True),
        "url": f.String(validators=v.Length(min=1, max=EXTERNAL_URL_MAX_LENGTH), pre_load=[strip]),
        "description": f.String(
            validators=v.Length(min=0, max=SEND_WEBHOOK_REQUEST_ACTION_DESCRIPTION_MAX_LENGTH)
        ),
        "service": f.String(validators=v.In(SEND_WEBHOOK_REQUEST_ACTION_TYPES)),
        "fields": f.List(
            f.Object(WEBHOOK_REQUEST_FIELD),
            validators=v.Length(max=SEND_WEBHOOK_REQUEST_ACTION_MAX_FIELD_COUNT),
        ),
    },
    name="send_webhook_request_action",
)

ZENDESK_USER = Schema(
    {
        "email": f.String(
            optional=True,
            pre_load=[strip, html_sanitize],
            validators=v.Length(max=ZENDESK_USER_EMAIL_MAX_LENGTH),
        ),
        "name": f.String(
            optional=True,
            pre_load=[strip, html_sanitize, unicode_normalize],
            validators=v.Length(max=ZENDESK_USER_NAME_MAX_LENGTH),
        ),
        "phoneNumber": f.String(optional=True, binding="phone_number"),
    },
    name="zendesk_user",
)

CREATE_ZENDESK_TICKET_ACTION = Schema(
    {
        "user": f.Object(ZENDESK_USER),
        "type": f.Constant(value="create_zendesk_ticket_action", read_only=True),
        "ticketType": f.String(
            optional=True,
            binding="ticket_type",
            validators=(v.In(ZENDESK_TICKET_TYPES) | v.Equal("")),
        ),
        "ticketPriority": f.String(
            optional=True,
            binding="ticket_priority",
            validators=(v.In(ZENDESK_TICKET_PRIORITIES) | v.Equal("")),
        ),
        "subject": f.String(
            optional=True,
            validators=v.Length(max=ZENDESK_TICKET_SUBJECT_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "description": f.String(
            validators=v.Length(min=1, max=ZENDESK_TICKET_DESCRIPTION_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "tags": f.List(
            f.String(validators=v.Length(max=ZENDESK_TICKET_TAG_MAX_LENGTH)),
            optional=True,
            validators=v.Length(max=ZENDESK_TICKET_TAGS_MAX_COUNT),
        ),
        "groupID": f.String(
            optional=True,
            binding="group_id",
            validators=[
                v.Length(max=ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH),
                v.Match(re.compile(r"^\d*$")),
            ],
        ),
        "assigneeID": f.String(
            optional=True,
            binding="assignee_id",
            pre_load=[strip],
            validators=[
                v.Length(max=ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH),
                v.Match(re.compile(r"^\d*$")),
            ],
        ),
    },
    name="create_zendesk_ticket_action",
)

JUMP_TO_ACTION = Schema(
    {
        "type": f.Constant(value="jump_to_action", read_only=True),
        "connections": f.List(
            f.Object(FLOW_CONNECTION),
            validators=v.Length(min=0, max=JUMP_TO_ACTION_MAX_CONNECTIONS_COUNT),
        ),
        "defaultTarget": f.PolymorphicObject(
            on="type",
            binding="default_target",
            allow_none=True,
            schemas={"story": STORY_TARGET, "step": STEP_TARGET},
        ),
    },
    name="jump_to_action",
)

CUSTOMER_SATISFACTION_CHOICE = CustomerSatisfactionChoiceSchema(
    {
        "type": f.Constant("customer_satisfaction_choice", read_only=True),
        "target": f.PolymorphicObject(
            on="type", allow_none=True, schemas={"story": STORY_TARGET, "step": STEP_TARGET}
        ),
        "kind": f.String(validators=v.In(CUSTOMER_SATISFACTION_CHOICE_KINDS)),
        "label": f.String(
            validators=v.Length(min=1, max=QUICK_REPLY_TITLE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "matchingIntent": f.Object(
            MATCH_INTENT_CONDITION_INTENT,
            binding="matching_intent",
            allow_none=True,
            read_only=True,
        ),
        "matching_intent_id": f.String(write_only=True, optional=True),
    },
    name="customer_satisfaction_choice",
)

CUSTOMER_SATISFACTION_ACTION = Schema(
    {
        "type": f.Constant("customer_satisfaction_action", read_only=True),
        "message": f.String(
            validators=v.Length(min=1, max=SEND_TEXT_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "choices": f.List(
            f.Object(CUSTOMER_SATISFACTION_CHOICE),
            validators=v.Length(
                min=CUSTOMER_SATISFACTION_ACTION_BUTTONS_COUNT,
                max=CUSTOMER_SATISFACTION_ACTION_BUTTONS_COUNT,
            ),
        ),
    },
    name="customer_satisfaction_action",
)

CREATE_USER_REQUEST_ACTION = Schema(
    {
        "type": f.Constant("create_user_request_action", read_only=True),
        "message": f.String(
            validators=v.Length(min=1, max=CREATE_USER_REQUEST_ACTION_MESSAGE_MAX_LENGTH),
            pre_load=[strip, html_sanitize, unicode_normalize],
        ),
        "assigneeID": f.String(
            optional=True, allow_none=True, binding="assignee_id", pre_load=[strip]
        ),
    },
    name="create_user_request_action",
)

ACTION_SCHEMAS = {
    "pause_bot_action": PAUSE_BOT_ACTION,
    "wait_action": WAIT_ACTION,
    "send_email_action": SEND_EMAIL_ACTION,
    "send_text_action": SEND_TEXT_ACTION,
    "send_js_event_action": SEND_JS_EVENT_ACTION,
    "send_image_action": SEND_IMAGE_ACTION,
    "close_intercom_conversation_action": CLOSE_INTERCOM_CONVERSATION_ACTION,
    "assign_intercom_conversation_action": ASSIGN_INTERCOM_CONVERSATION_ACTION,
    "send_cards_action": SEND_CARDS_ACTIONS,
    "send_quick_replies_action": SEND_QUICK_REPLIES_ACTION,
    "store_session_value_action": STORE_SESSION_VALUE_ACTION,
    "set_user_attribute_action": SET_USER_ATTRIBUTE_ACTION,
    "ask_location_action": ASK_LOCATION_ACTION,
    "google_custom_search_action": GOOGLE_CUSTOM_SEARCH_ACTION,
    "create_zendesk_ticket_action": CREATE_ZENDESK_TICKET_ACTION,
    "jump_to_action": JUMP_TO_ACTION,
    "customer_satisfaction_action": CUSTOMER_SATISFACTION_ACTION,
    "send_webhook_request_action": SEND_WEBHOOK_REQUEST_ACTION,
    "create_user_request_action": CREATE_USER_REQUEST_ACTION,
}

COORDINATES = Schema({"lat": f.Number(), "long": f.Number()}, name="coordinates")

#
# Webhook
#
URL_LOADED_EVENT = Schema(
    {"url": f.String(pre_load=[strip]), "type": f.Constant("url_loaded_event", read_only=True)},
    name="url_loaded_event",
)

CUSTOM_EVENT = Schema(
    {"type": f.Constant("custom_event", read_only=True), "name": f.String()}, name="custom_event"
)

FILE = Schema({"type": f.Constant("file", read_only=True), "url": f.String()}, name="file")

VIDEO = Schema({"type": f.Constant("video", read_only=True), "url": f.String()}, name="video")

IMAGE = Schema({"type": f.Constant("image", read_only=True), "url": f.String()}, name="image")

AUDIO = Schema({"type": f.Constant("audio", read_only=True), "url": f.String()}, name="audio")

ATTACHMENTS_SCHEMAS = {"file": FILE, "audio": AUDIO, "video": VIDEO, "image": IMAGE}

INCOMING_MESSAGE = Schema(
    {
        "type": f.Constant("message", read_only=True),
        "text": f.String(pre_load=[html_sanitize, unicode_normalize]),
        "attachments": f.PolymorphicList(on="type", schemas=ATTACHMENTS_SCHEMAS),
    },
    name="incoming_message",
)


REPLY_TO_ACTION_TO_MESSAGE = Schema(
    {
        "type": f.Constant("message"),
        "attachments": f.Constant([]),
        "text": f.String(binding="message", pre_load=[html_sanitize, unicode_normalize]),
    },
    name="reply_to_action_to_message",
)

INPUT_SCHEMAS = {
    "message": INCOMING_MESSAGE,
    "legacy_reply_to_message_action": REPLY_TO_ACTION_TO_MESSAGE,
    "url_loaded_event": URL_LOADED_EVENT,
    "go_to_action": GO_TO_ACTION,
    "custom_event": CUSTOM_EVENT,
}

WEBHOOK_INTERLOCUTOR = Schema(
    {
        "id": f.String(),
        "location": f.Object(COORDINATES, allow_none=True),
        "email": f.String(
            allow_none=True,
            validators=v.Length(max=SET_USER_ATTRIBUTE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize],
        ),
        "firstName": f.String(
            binding="first_name",
            allow_none=True,
            validators=v.Length(max=SET_USER_ATTRIBUTE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "lastName": f.String(
            binding="last_name",
            allow_none=True,
            validators=v.Length(max=SET_USER_ATTRIBUTE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "phoneNumber": f.String(
            binding="phone_number",
            allow_none=True,
            validators=v.Length(max=SET_USER_ATTRIBUTE_ACTION_VALUE_MAX_LENGTH),
            pre_load=[html_sanitize, unicode_normalize],
        ),
        "customAttributes": f.Dict(
            binding="custom_attributes",
            validators=v.TypedDict(str, str) & v.DictKeysFormat(re.compile(r"^[\w\d]+$")),
        ),
    },
    name="webhook_interlocutor",
)

WEBHOOK_CONVERSATION_SESSION = Schema({"values": f.Dict()}, name="webhook_conversation_session")

WEBHOOK_STEP = Schema(
    {
        "id": f.String(),
        "name": f.String(),
        "userData": f.String(binding="user_data"),
        "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS),
    },
    name="webhook_step",
)

WEBHOOK_STEP_REACHED = Schema(
    {
        "type": f.Constant("step_reached_event", read_only=True),
        "channel": f.String(),
        "interlocutor": f.Object(schema=WEBHOOK_INTERLOCUTOR),
        "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION),
        "step": f.Object(schema=WEBHOOK_STEP),
        "input": f.PolymorphicObject(on="type", schemas=INPUT_SCHEMAS),
    },
    name="webhook_step_reached",
)

WEBHOOK_STEP_REACHED_RESPONSE = Schema(
    {
        "actions": f.PolymorphicList(on="type", schemas=ACTION_SCHEMAS),
        "session": f.Object(schema=WEBHOOK_CONVERSATION_SESSION, optional=True, allow_none=True),
        "interlocutor": f.Object(schema=WEBHOOK_INTERLOCUTOR, optional=True, allow_none=True),
    },
    name="webhook_step_reached_response",
)

WEBHOOK_REQUEST = Schema(
    {
        "topic": f.String(),
        "botID": f.String(binding="bot_id"),
        "timestamp": f.Int(),
        "type": f.Constant("notification_event", read_only=True),
        "data": f.PolymorphicObject(
            binding="event", on="type", schemas={"step_reached_event": WEBHOOK_STEP_REACHED}
        ),
    },
    name="webhook_request",
)


def get_mapper(factory=bind):
    """Load mapper v1

    Returns:
        Mapper
    """
    mapper = Mapper()
    mappings = {
        AskLocationAction: ASK_LOCATION_ACTION,
        StepTarget: STEP_TARGET,
        StoryTarget: STORY_TARGET,
        GoToAction: GO_TO_ACTION,
        LegacyReplyToMessageAction: LEGACY_REPLY_TO_MESSAGE_ACTION,
        OpenURLAction: OPEN_URL_ACTION,
        ShareAction: SHARE_ACTION,
        SendImageAction: SEND_IMAGE_ACTION,
        SendTextAction: SEND_TEXT_ACTION,
        SendJSEventAction: SEND_JS_EVENT_ACTION,
        SendEmailAction: SEND_EMAIL_ACTION,
        WaitAction: WAIT_ACTION,
        PauseBotAction: PAUSE_BOT_ACTION,
        CloseIntercomConversationAction: CLOSE_INTERCOM_CONVERSATION_ACTION,
        AssignIntercomConversationAction: ASSIGN_INTERCOM_CONVERSATION_ACTION,
        QuickReply: QUICK_REPLY,
        SendQuickRepliesAction: SEND_QUICK_REPLIES_ACTION,
        Button: BUTTON,
        Card: CARD,
        SendCardsAction: SEND_CARDS_ACTIONS,
        StoreSessionValueAction: STORE_SESSION_VALUE_ACTION,
        SetUserAttributeAction: SET_USER_ATTRIBUTE_ACTION,
        Step: WEBHOOK_STEP,
        Interlocutor: WEBHOOK_INTERLOCUTOR,
        ConversationSession: WEBHOOK_CONVERSATION_SESSION,
        StepReached: WEBHOOK_STEP_REACHED,
        WebhookRequest: WEBHOOK_REQUEST,
        Coordinates: COORDINATES,
        StepReachedResponse: WEBHOOK_STEP_REACHED_RESPONSE,
        GoogleCustomSearchAction: GOOGLE_CUSTOM_SEARCH_ACTION,
        CreateZendeskTicketAction: CREATE_ZENDESK_TICKET_ACTION,
        ZendeskUser: ZENDESK_USER,
        JumpToAction: JUMP_TO_ACTION,
        MessageGetter: PREDICATE_MESSAGE_GETTER,
        SessionValueGetter: PREDICATE_SESSION_VALUE_GETTER,
        UserAttributeGetter: PREDICATE_USER_ATTRIBUTE_GETTER,
        IsNotSetCondition: IS_NOT_SET_CONDITION,
        IsSetCondition: IS_SET_CONDITION,
        ContainCondition: CONTAIN_CONDITION,
        EqualsCondition: EQUALS_CONDITION,
        MatchRegexpCondition: MATCH_REGEXP_CONDITION,
        MatchIntentConditionIntent: MATCH_INTENT_CONDITION_INTENT,
        MatchIntentCondition: MATCH_INTENT_CONDITION,
        IsLessThanCondition: IS_LESS_THAN_CONDITION,
        IsLessThanOrEqualCondition: IS_LESS_THAN_OR_EQUAL_CONDITION,
        IsGreaterThanCondition: IS_GREATER_THAN_CONDITION,
        IsGreaterThanOrEqualCondition: IS_GREATER_THAN_OR_EQUAL_CONDITION,
        IsNumberCondition: IS_NUMBER_CONDITION,
        FlowConnection: FLOW_CONNECTION,
        ConnectionPredicate: FLOW_CONNECTION_PREDICATE,
        URLLoadedEvent: URL_LOADED_EVENT,
        CustomEvent: CUSTOM_EVENT,
        Message: (INCOMING_MESSAGE, REPLY_TO_ACTION_TO_MESSAGE),
        File: FILE,
        Audio: AUDIO,
        Video: VIDEO,
        Image: IMAGE,
        CustomerSatisfactionCallbackAction: CUSTOMER_SATISFACTION_CALLBACK_ACTION,
        CustomerSatisfactionChoice: CUSTOMER_SATISFACTION_CHOICE,
        CustomerSatisfactionAction: CUSTOMER_SATISFACTION_ACTION,
        SendWebhookRequestAction: SEND_WEBHOOK_REQUEST_ACTION,
        WebhookRequestField: WEBHOOK_REQUEST_FIELD,
        CreateUserRequestAction: CREATE_USER_REQUEST_ACTION,
    }

    for cls, schemas in mappings.items():
        if not isinstance(schemas, tuple):
            schemas = (schemas,)

        for schema in schemas:
            mapper.register(cls, schema, factory=factory)

    return mapper
