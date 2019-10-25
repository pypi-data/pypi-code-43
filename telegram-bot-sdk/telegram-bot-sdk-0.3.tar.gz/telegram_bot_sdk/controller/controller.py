from telegram_bot_sdk.exceptions.message_exception import MessageError
from telegram_bot_sdk.exceptions.web_exception import WebError
from telegram_bot_sdk.helper import travseral
import json


def control_requests(request):

    return request


def control_response_level_network(response):
    if response.status_code != 200:
        raise WebError(response.status_code, response.text)

    json_decoded = json.loads(response.text)
    json_decoded = travseral.replace_keys_from_dict("from", "from_user", json_decoded)
    json_decoded = travseral.replace_keys_from_dict("id", "id_unique", json_decoded)
    json_decoded = travseral.replace_keys_from_dict("type", "type_result", json_decoded)
    json_decoded = travseral.replace_keys_from_dict("hash", "hash_data", json_decoded)

    return control_response_level_message(json_decoded)


def control_response_level_message(response):
    if not response["ok"]:
        raise MessageError
    else:
        return response["result"]

