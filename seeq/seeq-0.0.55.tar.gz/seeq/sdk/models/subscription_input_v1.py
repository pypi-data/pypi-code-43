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


class SubscriptionInputV1(object):
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
        'channel_id': 'str',
        'subscriber_parameters': 'list[str]'
    }

    attribute_map = {
        'channel_id': 'channelId',
        'subscriber_parameters': 'subscriberParameters'
    }

    def __init__(self, channel_id=None, subscriber_parameters=None):
        """
        SubscriptionInputV1 - a model defined in Swagger
        """

        self._channel_id = None
        self._subscriber_parameters = None

        if channel_id is not None:
          self.channel_id = channel_id
        if subscriber_parameters is not None:
          self.subscriber_parameters = subscriber_parameters

    @property
    def channel_id(self):
        """
        Gets the channel_id of this SubscriptionInputV1.
        URI that uniquely identifies the channel

        :return: The channel_id of this SubscriptionInputV1.
        :rtype: str
        """
        return self._channel_id

    @channel_id.setter
    def channel_id(self, channel_id):
        """
        Sets the channel_id of this SubscriptionInputV1.
        URI that uniquely identifies the channel

        :param channel_id: The channel_id of this SubscriptionInputV1.
        :type: str
        """
        if channel_id is None:
            raise ValueError("Invalid value for `channel_id`, must not be `None`")

        self._channel_id = channel_id

    @property
    def subscriber_parameters(self):
        """
        Gets the subscriber_parameters of this SubscriptionInputV1.
        Parameters associated with the subscriber

        :return: The subscriber_parameters of this SubscriptionInputV1.
        :rtype: list[str]
        """
        return self._subscriber_parameters

    @subscriber_parameters.setter
    def subscriber_parameters(self, subscriber_parameters):
        """
        Sets the subscriber_parameters of this SubscriptionInputV1.
        Parameters associated with the subscriber

        :param subscriber_parameters: The subscriber_parameters of this SubscriptionInputV1.
        :type: list[str]
        """

        self._subscriber_parameters = subscriber_parameters

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
        if not isinstance(other, SubscriptionInputV1):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
