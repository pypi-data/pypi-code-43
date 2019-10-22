#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import sys
import traceback
from marshmallow import Schema, fields
from marshmallow import ValidationError as MarshmallowValidationError


class Error(Exception):
    """Error"""
    MSGID = "Err-00000"
    CODE = 1

    def __init__(self, message=None, extra=None, msgid=None,
                 stack=None, name=None, code=None, **kwargs):
        self.message = message if message else self.__doc__
        Exception.__init__(self, code, self.message)
        self.code = code or self.CODE
        self.extra = extra or kwargs
        self.stack = stack
        self.msgid = msgid or self.MSGID
        self.name = name or self.__class__.__name__

        if self.stack is None:
            exc_t, exc_v, exc_tb = sys.exc_info()
            if exc_t and exc_v and exc_tb:
                self.stack = "\n".join([
                    x.rstrip() for x in traceback.format_exception(
                        exc_t, exc_v, exc_tb
                    )
                ])

    def to_json(self):
        return ErrorSchema().dumps(self)

    def to_dict(self):
        return ErrorSchema().dump(self)

    @classmethod
    def from_json(cls, data):
        return ErrorSchema().load(data)

    def __repr__(self):
        return "{}<code={}, msgid={}, message={}>".format(
            self.__class__.__name__, self.code, self.msgid, self.message
        )

    def __str__(self):
        return "{}: {}".format(self.msgid, self.message)


class ErrorSchema(Schema):
    code = fields.Integer(required=True)
    name = fields.String(required=True)
    message = fields.String(required=True)
    msgid = fields.String()
    extra = fields.Dict()
    stack = fields.String()

    def class_name(self, data):
        return data.__class__.__name__


def from_exc(exc, extra=None):
    """ Try to convert exception into an JSOn serializable

    :param Exception exc: exception
    :param dict extra: extra data
    :return: an Error
    :rtype: Error
    """
    if isinstance(exc, Error):
        return exc

    if isinstance(exc, MarshmallowValidationError):
        return ValidationError(
            "Invalid field(s) value: {}".format(
                ", ".join(exc.normalized_messages().keys())
            ), extra=exc.normalized_messages()
        )

    return InternalError(message=str(exc), extra=extra)


class ConfigurationError(Error):
    """Configuration error"""
    MSGID = "ERR-19036"
    CODE = 500


# noinspection PyShadowingBuiltins
class IOError(Error):
    """I/O Error"""
    MSGID = "ERR-27582"
    CODE = 500


# noinspection PyShadowingBuiltins
class NotImplemented(Error):
    """Not Implemented"""
    MSGID = "ERR-04766"
    CODE = 501


class ValidationError(Error):
    """Validation error"""
    MSGID = "ERR-04413"
    CODE = 400


class NotFound(Error):
    """Not Found"""
    MSGID = "ERR-08414"
    CODE = 404


class InternalError(Error):
    """Internal Error"""
    MSGID = "ERR-29885"
    CODE = 500
