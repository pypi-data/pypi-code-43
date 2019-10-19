from enum import Enum

from flask import request
from flask_restful import abort


class MessageType(Enum):
    """message types processed by error/success handlers in ui5 web frontend"""
    INFORMATION = 'Information'
    NONE = 'None'
    SUCCESS = 'Success'
    WARNING = 'Warning'
    ERROR = 'Error'
    DEBUG = 'Debug'  # not known by UI5 message processor, only showed in frontend console log


def throw_exception(message: str = None,
                    message_type: MessageType = MessageType.ERROR,
                    additional_text: str = None,
                    status_code: int = 409,
                    description: str = None):
    """wraps the flask abort method and hands over a message for ui5 frontend; uses flask request which is not required
    as a parameter"""
    description_text = f'Resource: {parse_resource_from_request(request)}'
    if description:
        description_text = description + '\n' + description_text
    abort(status_code, message={
        'type':           message_type.value,
        'message':        message,
        'additionalText': additional_text,
        'description':    description_text
        })


def get_message(message: str = None,
                message_type: MessageType = MessageType.INFORMATION,
                additional_text: str = None,
                description: str = None):
    """generates a message to be userd in a ui5 frontend; uses flask request which is not required as a paramter"""
    description_text = f'Resource: {parse_resource_from_request(request)}'
    if description and description.strip():
        description_text = description + '\n' + description_text
    return {
        'type':           message_type.value,
        'message':        message,
        'additionalText': additional_text,
        'description':    description_text
        }


def parse_resource_from_request(req: request):
    items = req.url.split('/')
    index_start = items.index('backend') + 1
    resource_name = '/'.join(items[index_start:])
    if '?' in resource_name:
        resource_name = resource_name[:resource_name.find('?')]

    return resource_name
