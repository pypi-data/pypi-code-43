import pprint
import six
import typing

from decimal import Decimal

from properly_model_python import util

T = typing.TypeVar('T')


class Model(object):
    # swaggerTypes: The key is attribute name and the
    # value is attribute type.
    swagger_types = {}

    # attributeMap: The key is attribute name and the
    # value is json key in definition.
    attribute_map = {}

    @classmethod
    def from_dict(cls: typing.Type[T], dikt) -> T:
        """Returns the dict as a model"""
        return util.deserialize_model(dikt, cls)

    def to_dict(self):
        """Returns the model properties as a dict

        :rtype: dict
        """
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            assigned_attr = self.attribute_map[attr]
            value = getattr(self, attr)
            if isinstance(value, list):
                result[assigned_attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[assigned_attr] = value.to_dict()
            elif isinstance(value, dict):
                result[assigned_attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[assigned_attr] = value

        return result

    def to_db_dict(self):
        """
        Returns the model properties as a DynamoDB compatible dict
        :rtype: dict
        """
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            assigned_attr = self.attribute_map[attr]
            value = getattr(self, attr)
            if isinstance(value, list):
                result[assigned_attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[assigned_attr] = value.to_dict()
            elif isinstance(value, dict):
                result[assigned_attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            elif isinstance(value, float):
                result[assigned_attr] = Decimal(str(value))
            else:
                result[assigned_attr] = value

            # DynamoDB does not accept `None` or '' values
            # So delete the properties with `None` or '' values
            if result[assigned_attr] is None or result[assigned_attr] == '':
                del result[assigned_attr]

        return result

    def to_str(self):
        """Returns the string representation of the model

        :rtype: str
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
