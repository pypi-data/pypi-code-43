# -*- coding: utf-8 -*-
import json
from .errors import Errors

class FollowUp:
    """Class for post-event actions to run."""

    def __init__(self, action, value=None):
        self.action = action
        self.value = value


class StatusCode:
    """Codes for <Response> objects."""
    STATUS_OK = 'OK'
    STATUS_WARNING = 'WARNING'
    STATUS_ERROR = 'ERROR'


class MessageType:
    """Categories for <Request> and <Response> objects."""
    TYPE_REQUEST = 'REQUEST'
    TYPE_RESPONSE = 'RESPONSE'
    TYPE_INFO = 'INFO'


class SerializableMessage:
    """Class for serializable messages."""

    def __init__(self):
        self.type = None
        self.data = None

    def set_data(self, data):
        """ set data """
        if isinstance(data, dict) and self._is_serializable(data):
            self.data = data
        else:
            raise TypeError(Errors.E0100)

    def _is_serializable(self, data):
        """ check if data is json-serializable """
        try:
            json.dumps(data)
            return True
        except:
            return False

    def obj_to_dict(self):
        """ converts to dict """

        data_dict = {}
        data_dict['type'] = self.type
        data_dict['data'] = self.data

        return data_dict

    def encode(self, MSG_LEN):
        """ converts to fixed-length byte data """

        data_dict = self.obj_to_dict()
        byte_data = json.dumps(data_dict).encode('utf-8')
        # zero padding
        byte_data += b'0' * (MSG_LEN - len(byte_data))
        return byte_data

    @staticmethod
    def encoded_to_dict(data):
        try:
            # convert to string
            padded_data = data.decode('utf-8')
            # remove zero padding
            sep = padded_data.find('}0')+1
            data_dict = json.loads(padded_data[:sep])
        except:
            raise ValueError(Errors.E0101)

        return data_dict


class Request(SerializableMessage):
    """Class for client requests."""

    def __init__(self):
        super().__init__()
        self.type = MessageType.TYPE_REQUEST
        self.classname = None
        self.classpath = None

    def set_classname(self, classname):
        """Sets name of class to call."""

        if isinstance(classname, str):
            self.classname = classname
        else:
            raise TypeError(Errors.E0102)

    def set_classpath(self, classpath):
        """Sets filepath for class."""

        if isinstance(classpath, str):
            self.classpath = classpath
        else:
            raise TypeError(Errors.E0103)

    def obj_to_dict(self):
        """Serializes itself to a dict."""

        data_dict = super().obj_to_dict()
        data_dict['classname'] = self.classname
        data_dict['classpath'] = self.classpath

        return data_dict

    @staticmethod
    def decode(encoded):

        data_dict = SerializableMessage.encoded_to_dict(encoded)

        request = Request()
        request.classname = data_dict.get('classname')
        request.classpath = data_dict.get('classpath')
        request.data = data_dict.get('data')

        return request


class Response(SerializableMessage):
    """Class for task response. """

    def __init__(self):
        super().__init__()
        self.type = MessageType.TYPE_RESPONSE
        self.status = None

    def set_status(self, status):
        """Sets status code """
        if status not in (StatusCode.STATUS_OK, StatusCode.STATUS_WARNING, StatusCode.STATUS_ERROR):
            raise ValueError(Errors.E0104)
        self.status = status

    def obj_to_dict(self):
        """Serializes itself to dict """

        data_dict = super().obj_to_dict()
        data_dict['status'] = self.status

        return data_dict

    @staticmethod
    def decode(encoded):

        data_dict = SerializableMessage.encoded_to_dict(encoded)

        response = Response()
        response.status = data_dict.get('status')
        response.data = data_dict.get('data')

        return response
