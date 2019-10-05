# coding: utf-8

"""
    Seeq REST API

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: 0.44.00-BETA
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class SampleInputV1(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'key': 'object',
        'value': 'object'
    }

    attribute_map = {
        'key': 'key',
        'value': 'value'
    }

    def __init__(self, key=None, value=None):
        """
        SampleInputV1 - a model defined in Swagger
        """

        self._key = None
        self._value = None

        if key is not None:
          self.key = key
        if value is not None:
          self.value = value

    @property
    def key(self):
        """
        Gets the key of this SampleInputV1.
        The key of the sample. For a time series, this is an ISO 8601 date string(YYYY-MM-DDThh:mm:ss.sssssssss±hh:mm) or an integer number of nanoseconds since January 1, 1970 in UTC time. Otherwise it is a double-precision number.

        :return: The key of this SampleInputV1.
        :rtype: object
        """
        return self._key

    @key.setter
    def key(self, key):
        """
        Sets the key of this SampleInputV1.
        The key of the sample. For a time series, this is an ISO 8601 date string(YYYY-MM-DDThh:mm:ss.sssssssss±hh:mm) or an integer number of nanoseconds since January 1, 1970 in UTC time. Otherwise it is a double-precision number.

        :param key: The key of this SampleInputV1.
        :type: object
        """
        if key is None:
            raise ValueError("Invalid value for `key`, must not be `None`")

        self._key = key

    @property
    def value(self):
        """
        Gets the value of this SampleInputV1.
        The value of the sample, which can be an integer, double-precision number, a string, a boolean, or null to indicate an invalid sample value.

        :return: The value of this SampleInputV1.
        :rtype: object
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the value of this SampleInputV1.
        The value of the sample, which can be an integer, double-precision number, a string, a boolean, or null to indicate an invalid sample value.

        :param value: The value of this SampleInputV1.
        :type: object
        """

        self._value = value

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, SampleInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
