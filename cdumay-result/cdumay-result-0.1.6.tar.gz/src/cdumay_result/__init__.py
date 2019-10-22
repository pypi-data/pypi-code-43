#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from uuid import uuid4
from marshmallow import Schema, fields
from cdumay_error import from_exc
import jsonpath_rw_ext


def random_uuid():
    """description of random_uuid"""
    return str(uuid4())


class ResultSchema(Schema):
    uuid = fields.String()
    retcode = fields.Integer(default=0)
    stdout = fields.String(default="")
    stderr = fields.String(default="")
    retval = fields.Dict()


class Result(object):
    def __init__(self, retcode=0, stdout="", stderr="", retval=None, uuid=None):
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr
        self.retval = retval or dict()
        self.uuid = uuid if uuid else random_uuid()

    def print(self, data):
        """Store text in result's stdout

        :param Any data: Any printable data
        """
        self.stdout += "{}\n".format(data)

    def print_err(self, data):
        """Store text in result's stderr

        :param Any data: Any printable data
        """
        self.stderr += "{}\n".format(data)

    @staticmethod
    def from_exception(exc, uuid=None):
        """ Serialize an exception into a result

        :param Exception exc: Exception raised
        :param str uuid: Current Kafka :class:`kser.transport.Message` uuid
        :rtype: :class:`kser.result.Result`
        """
        return Result.from_error(
            from_exc(exc, extra=dict(uuid=uuid or random_uuid()))
        )

    @staticmethod
    def from_error(error):
        """ Serialize an Error into a result

        :param Error error: error raised
        :rtype: :class:`kser.result.Result`
        """
        return Result(
            uuid=error.extra.get("uuid", random_uuid()),
            retcode=error.code, stderr=error.message,
            retval=dict(error=error.to_dict())
        )

    def search_value(self, xpath, default=None, single_value=True):
        """ Try to find a value in the result.
        see https://github.com/kennknowles/python-jsonpath-rw#jsonpath-syntax

        :param str xpath: a xpath filter
        :param any default: default value if not found
        :param bool single_value: is the result is multivalued
        :return: the value found or None
        """
        matches = [
            match.value for match in
            jsonpath_rw_ext.parse(xpath).find(self.retval)
        ]
        if len(matches) == 0:
            return default
        return matches[0] if single_value is True else matches

    def __add__(self, o):
        """description of __add__"""
        self.retcode = self.retcode if self.retcode > o.retcode else o.retcode
        self.retval.update(o.retval)
        if o.stdout and (len(o.stdout) > 0):
            self.stdout = o.stdout
        if o.stderr and len(o.stderr) > 0:
            self.stderr = o.stderr
        return self

    def __str__(self):
        return self.stdout if self.retcode == 0 else self.stderr

    def __repr__(self):
        """"""
        return "Result<retcode='{}'>".format(self.retcode)
