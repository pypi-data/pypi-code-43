# coding: utf-8

"""
    ocrapi

    The powerful Optical Character Recognition (OCR) APIs let you convert scanned images of pages into recognized text.  # noqa: E501

    OpenAPI spec version: v1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class FormFieldDefinition(object):
    """NOTE: This class is auto generated by the swagger code generator program.

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
        'field_id': 'str',
        'left_anchor': 'str',
        'top_anchor': 'str',
        'anchor_mode': 'str',
        'data_type': 'str',
        'target_digit_count': 'int',
        'minimum_character_count': 'int',
        'allow_numeric_digits': 'bool',
        'vertical_alignment_type': 'str',
        'horizontal_alignment_type': 'str',
        'target_field_width_relative': 'float',
        'target_field_height_relative': 'float',
        'ignore': 'list[str]'
    }

    attribute_map = {
        'field_id': 'FieldID',
        'left_anchor': 'LeftAnchor',
        'top_anchor': 'TopAnchor',
        'anchor_mode': 'AnchorMode',
        'data_type': 'DataType',
        'target_digit_count': 'TargetDigitCount',
        'minimum_character_count': 'MinimumCharacterCount',
        'allow_numeric_digits': 'AllowNumericDigits',
        'vertical_alignment_type': 'VerticalAlignmentType',
        'horizontal_alignment_type': 'HorizontalAlignmentType',
        'target_field_width_relative': 'TargetFieldWidth_Relative',
        'target_field_height_relative': 'TargetFieldHeight_Relative',
        'ignore': 'Ignore'
    }

    def __init__(self, field_id=None, left_anchor=None, top_anchor=None, anchor_mode=None, data_type=None, target_digit_count=None, minimum_character_count=None, allow_numeric_digits=None, vertical_alignment_type=None, horizontal_alignment_type=None, target_field_width_relative=None, target_field_height_relative=None, ignore=None):  # noqa: E501
        """FormFieldDefinition - a model defined in Swagger"""  # noqa: E501

        self._field_id = None
        self._left_anchor = None
        self._top_anchor = None
        self._anchor_mode = None
        self._data_type = None
        self._target_digit_count = None
        self._minimum_character_count = None
        self._allow_numeric_digits = None
        self._vertical_alignment_type = None
        self._horizontal_alignment_type = None
        self._target_field_width_relative = None
        self._target_field_height_relative = None
        self._ignore = None
        self.discriminator = None

        if field_id is not None:
            self.field_id = field_id
        if left_anchor is not None:
            self.left_anchor = left_anchor
        if top_anchor is not None:
            self.top_anchor = top_anchor
        if anchor_mode is not None:
            self.anchor_mode = anchor_mode
        if data_type is not None:
            self.data_type = data_type
        if target_digit_count is not None:
            self.target_digit_count = target_digit_count
        if minimum_character_count is not None:
            self.minimum_character_count = minimum_character_count
        if allow_numeric_digits is not None:
            self.allow_numeric_digits = allow_numeric_digits
        if vertical_alignment_type is not None:
            self.vertical_alignment_type = vertical_alignment_type
        if horizontal_alignment_type is not None:
            self.horizontal_alignment_type = horizontal_alignment_type
        if target_field_width_relative is not None:
            self.target_field_width_relative = target_field_width_relative
        if target_field_height_relative is not None:
            self.target_field_height_relative = target_field_height_relative
        if ignore is not None:
            self.ignore = ignore

    @property
    def field_id(self):
        """Gets the field_id of this FormFieldDefinition.  # noqa: E501

        The identifier of the field; use this to identify which field is being referenced  # noqa: E501

        :return: The field_id of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._field_id

    @field_id.setter
    def field_id(self, field_id):
        """Sets the field_id of this FormFieldDefinition.

        The identifier of the field; use this to identify which field is being referenced  # noqa: E501

        :param field_id: The field_id of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._field_id = field_id

    @property
    def left_anchor(self):
        """Gets the left_anchor of this FormFieldDefinition.  # noqa: E501

        Optional - the left-hand anchor of the field  # noqa: E501

        :return: The left_anchor of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._left_anchor

    @left_anchor.setter
    def left_anchor(self, left_anchor):
        """Sets the left_anchor of this FormFieldDefinition.

        Optional - the left-hand anchor of the field  # noqa: E501

        :param left_anchor: The left_anchor of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._left_anchor = left_anchor

    @property
    def top_anchor(self):
        """Gets the top_anchor of this FormFieldDefinition.  # noqa: E501

        Optional - the top anchor of the field  # noqa: E501

        :return: The top_anchor of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._top_anchor

    @top_anchor.setter
    def top_anchor(self, top_anchor):
        """Sets the top_anchor of this FormFieldDefinition.

        Optional - the top anchor of the field  # noqa: E501

        :param top_anchor: The top_anchor of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._top_anchor = top_anchor

    @property
    def anchor_mode(self):
        """Gets the anchor_mode of this FormFieldDefinition.  # noqa: E501

        Optional - the matching mode for the anchor.  Possible values are Complete (requires the entire anchor to match) and Partial (allows only part of the anchor to match).  Default is Partial.  # noqa: E501

        :return: The anchor_mode of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._anchor_mode

    @anchor_mode.setter
    def anchor_mode(self, anchor_mode):
        """Sets the anchor_mode of this FormFieldDefinition.

        Optional - the matching mode for the anchor.  Possible values are Complete (requires the entire anchor to match) and Partial (allows only part of the anchor to match).  Default is Partial.  # noqa: E501

        :param anchor_mode: The anchor_mode of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._anchor_mode = anchor_mode

    @property
    def data_type(self):
        """Gets the data_type of this FormFieldDefinition.  # noqa: E501

        The data type of the field; possible values are INTEGER (Integer value), STRING (Arbitrary string value, spaces are permitted), DATE (Date in a structured format), DECIMAL (Decimal number), ALPHANUMERIC (Continuous alphanumeric string with no spaces), STRINGNOWHITESPACE (A string that contains no whitespace characters), SERIALNUMBER (A serial-number style string that contains letters and numbers, and certain symbols; must contain at least one number), ALPHAONLY (Alphabet characters only, no numbers or symbols or whitespace)  # noqa: E501

        :return: The data_type of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Sets the data_type of this FormFieldDefinition.

        The data type of the field; possible values are INTEGER (Integer value), STRING (Arbitrary string value, spaces are permitted), DATE (Date in a structured format), DECIMAL (Decimal number), ALPHANUMERIC (Continuous alphanumeric string with no spaces), STRINGNOWHITESPACE (A string that contains no whitespace characters), SERIALNUMBER (A serial-number style string that contains letters and numbers, and certain symbols; must contain at least one number), ALPHAONLY (Alphabet characters only, no numbers or symbols or whitespace)  # noqa: E501

        :param data_type: The data_type of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._data_type = data_type

    @property
    def target_digit_count(self):
        """Gets the target_digit_count of this FormFieldDefinition.  # noqa: E501

        Optional - the target number of digits in the field; useful for fixed-length fields  # noqa: E501

        :return: The target_digit_count of this FormFieldDefinition.  # noqa: E501
        :rtype: int
        """
        return self._target_digit_count

    @target_digit_count.setter
    def target_digit_count(self, target_digit_count):
        """Sets the target_digit_count of this FormFieldDefinition.

        Optional - the target number of digits in the field; useful for fixed-length fields  # noqa: E501

        :param target_digit_count: The target_digit_count of this FormFieldDefinition.  # noqa: E501
        :type: int
        """

        self._target_digit_count = target_digit_count

    @property
    def minimum_character_count(self):
        """Gets the minimum_character_count of this FormFieldDefinition.  # noqa: E501

        Optional - the target number of digits in the field; useful for fixed-length fields  # noqa: E501

        :return: The minimum_character_count of this FormFieldDefinition.  # noqa: E501
        :rtype: int
        """
        return self._minimum_character_count

    @minimum_character_count.setter
    def minimum_character_count(self, minimum_character_count):
        """Sets the minimum_character_count of this FormFieldDefinition.

        Optional - the target number of digits in the field; useful for fixed-length fields  # noqa: E501

        :param minimum_character_count: The minimum_character_count of this FormFieldDefinition.  # noqa: E501
        :type: int
        """

        self._minimum_character_count = minimum_character_count

    @property
    def allow_numeric_digits(self):
        """Gets the allow_numeric_digits of this FormFieldDefinition.  # noqa: E501

        Optional - set to false to block values that contain numeric digits, set to true to allow numeric digits  # noqa: E501

        :return: The allow_numeric_digits of this FormFieldDefinition.  # noqa: E501
        :rtype: bool
        """
        return self._allow_numeric_digits

    @allow_numeric_digits.setter
    def allow_numeric_digits(self, allow_numeric_digits):
        """Sets the allow_numeric_digits of this FormFieldDefinition.

        Optional - set to false to block values that contain numeric digits, set to true to allow numeric digits  # noqa: E501

        :param allow_numeric_digits: The allow_numeric_digits of this FormFieldDefinition.  # noqa: E501
        :type: bool
        """

        self._allow_numeric_digits = allow_numeric_digits

    @property
    def vertical_alignment_type(self):
        """Gets the vertical_alignment_type of this FormFieldDefinition.  # noqa: E501

        Vertical alignment of target value area relative to the field anchor; Possible values are VCenter, Top, Bottom  # noqa: E501

        :return: The vertical_alignment_type of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._vertical_alignment_type

    @vertical_alignment_type.setter
    def vertical_alignment_type(self, vertical_alignment_type):
        """Sets the vertical_alignment_type of this FormFieldDefinition.

        Vertical alignment of target value area relative to the field anchor; Possible values are VCenter, Top, Bottom  # noqa: E501

        :param vertical_alignment_type: The vertical_alignment_type of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._vertical_alignment_type = vertical_alignment_type

    @property
    def horizontal_alignment_type(self):
        """Gets the horizontal_alignment_type of this FormFieldDefinition.  # noqa: E501

        Horizontal alignment of target value area relative to the field anchor; Possible values are Left, Right  # noqa: E501

        :return: The horizontal_alignment_type of this FormFieldDefinition.  # noqa: E501
        :rtype: str
        """
        return self._horizontal_alignment_type

    @horizontal_alignment_type.setter
    def horizontal_alignment_type(self, horizontal_alignment_type):
        """Sets the horizontal_alignment_type of this FormFieldDefinition.

        Horizontal alignment of target value area relative to the field anchor; Possible values are Left, Right  # noqa: E501

        :param horizontal_alignment_type: The horizontal_alignment_type of this FormFieldDefinition.  # noqa: E501
        :type: str
        """

        self._horizontal_alignment_type = horizontal_alignment_type

    @property
    def target_field_width_relative(self):
        """Gets the target_field_width_relative of this FormFieldDefinition.  # noqa: E501

        Optional - scale factor for target field width - relative to width of field title; a value of 1.0 indicates the target value area has the same width as the field value as occurring in the image; a value of 2.0 would indicate that the target value area has 2 times the width of the field value as occurring in the image.  # noqa: E501

        :return: The target_field_width_relative of this FormFieldDefinition.  # noqa: E501
        :rtype: float
        """
        return self._target_field_width_relative

    @target_field_width_relative.setter
    def target_field_width_relative(self, target_field_width_relative):
        """Sets the target_field_width_relative of this FormFieldDefinition.

        Optional - scale factor for target field width - relative to width of field title; a value of 1.0 indicates the target value area has the same width as the field value as occurring in the image; a value of 2.0 would indicate that the target value area has 2 times the width of the field value as occurring in the image.  # noqa: E501

        :param target_field_width_relative: The target_field_width_relative of this FormFieldDefinition.  # noqa: E501
        :type: float
        """

        self._target_field_width_relative = target_field_width_relative

    @property
    def target_field_height_relative(self):
        """Gets the target_field_height_relative of this FormFieldDefinition.  # noqa: E501

        Optional - scale factor for target field height - relative to height of field title  # noqa: E501

        :return: The target_field_height_relative of this FormFieldDefinition.  # noqa: E501
        :rtype: float
        """
        return self._target_field_height_relative

    @target_field_height_relative.setter
    def target_field_height_relative(self, target_field_height_relative):
        """Sets the target_field_height_relative of this FormFieldDefinition.

        Optional - scale factor for target field height - relative to height of field title  # noqa: E501

        :param target_field_height_relative: The target_field_height_relative of this FormFieldDefinition.  # noqa: E501
        :type: float
        """

        self._target_field_height_relative = target_field_height_relative

    @property
    def ignore(self):
        """Gets the ignore of this FormFieldDefinition.  # noqa: E501

        Optional - Ignore any result items that contain a partial or complete match with these text strings  # noqa: E501

        :return: The ignore of this FormFieldDefinition.  # noqa: E501
        :rtype: list[str]
        """
        return self._ignore

    @ignore.setter
    def ignore(self, ignore):
        """Sets the ignore of this FormFieldDefinition.

        Optional - Ignore any result items that contain a partial or complete match with these text strings  # noqa: E501

        :param ignore: The ignore of this FormFieldDefinition.  # noqa: E501
        :type: list[str]
        """

        self._ignore = ignore

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if issubclass(FormFieldDefinition, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FormFieldDefinition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
