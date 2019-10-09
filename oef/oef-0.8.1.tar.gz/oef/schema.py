# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#   Copyright 2018 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------


"""

oef.schema
~~~~~~~~~~

This module defines classes to deal with data models and their instances.

"""


import copy
from abc import ABC, abstractmethod
from typing import Union, Type, Optional, List, Dict

from . import  agent_pb2
from . import dap_interface_pb2
from . import TypeHelpers
from .Logging import has_logger
from .Interfaces import ProtobufSerializable
from .Wrappers import Location

"""
The allowable types that an Attribute can have
"""
ATTRIBUTE_TYPES = Union[float, str, bool, int, Location]


class AttributeSchema(ProtobufSerializable):
    """
    Description of a single element of datum of either a description or a service.

    This defines the schema that a single entry in a schema must take.

    Examples:
        >>> attr_title    = AttributeSchema("title" ,          str,   True,  "The title of the book.")
        >>> attr_author   = AttributeSchema("author" ,         str,   True,  "The author of the book.")
        >>> attr_genre    = AttributeSchema("genre",           str,   True,  "The genre of the book.")
        >>> attr_year     = AttributeSchema("year",            int,   True,  "The year of publication of the book.")
        >>> attr_avg_rat  = AttributeSchema("average_rating",  float, False, "The average rating of the book.")
        >>> attr_isbn     = AttributeSchema("ISBN",            str,   True,  "The ISBN.")
        >>> attr_ebook    = AttributeSchema("ebook_available", bool,  False, "If the book can be sold as an e-book.")

    """

    def __init__(self,
                 attribute_name: str,
                 attribute_type: Type[ATTRIBUTE_TYPES],
                 is_attribute_required: bool,
                 attribute_description: Optional[str] = None) -> None:
        """
        Initialize an attribute schema.

        :param attribute_name: the name of this attribute.
        :param attribute_type: the type of this attribute, must be a type in ATTRIBUTE_TYPES.
        :param is_attribute_required: whether does this attribute have to be included.
        :param attribute_description: optional description of this attribute.
        """
        self.name = attribute_name
        self.type = attribute_type
        self.required = is_attribute_required
        self.description = attribute_description

    def to_pb(self) -> dap_interface_pb2.DataModel.Attribute:
        """
        Convert the attribute into a Protobuf object

        :return: the associated Attribute protobuf object.
        """
        attribute = dap_interface_pb2.DataModel.Attribute()
        attribute.name = self.name
        attribute.typecode = TypeHelpers.TYPECODE_MAP[self.type]
        attribute.required = self.required
        if self.description is not None:
            attribute.description = self.description
        return attribute

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "typecode": TypeHelpers.TYPECODE_MAP[self.type],
            "required": self.required,
            "description": self.description if self.description else ""
        }

    @classmethod
    def from_pb(cls, attribute: dap_interface_pb2.DataModel.Attribute):
        """
        Unpack the attribute Protobuf object.

        :param attribute: the Protobuf object associated with the attribute.
        :return: the attribute.
        """
        return cls(attribute.name,
                   dict(map(reversed, cls._attribute_type_to_pb.items()))[attribute.type],
                   attribute.required,
                   attribute.description if attribute.description else None)

    def __eq__(self, other):
        if type(other) != AttributeSchema:
            return False
        else:
            return self.name == other.name and self.type == other.type and self.required == other.required


class AttributeInconsistencyException(Exception):
    """
    Raised when the attributes in a Description are inconsistent.

    Inconsistency is defined when values do not meet their respective schema, or if the values
    are not of an allowed type.
    """
    pass


class DataModel(ProtobufSerializable):
    """
    This class represents a data model (a.k.a. schema) of the OEFCore.

    Examples:
        >>> book_model = DataModel("book", [
        ..  AttributeSchema("title" ,          str,   True,  "The title of the book."),
        ..  AttributeSchema("author" ,         str,   True,  "The author of the book."),
        ..  AttributeSchema("genre",           str,   True,  "The genre of the book."),
        ..  AttributeSchema("year",            int,   True,  "The year of publication of the book."),
        ..  AttributeSchema("average_rating",  float, False, "The average rating of the book."),
        ..  AttributeSchema("ISBN",            str,   True,  "The ISBN."),
        ..  AttributeSchema("ebook_available", bool,  False, "If the book can be sold as an e-book."),
        .. ], "A data model to describe books.")
    """

    def __init__(self,
                 name: str,
                 attribute_schemas: List[AttributeSchema],
                 description: Optional[str] = None) -> None:
        """
        Initialize a Data Model object.

        :param name: the name of the data model.
        :param attribute_schemas: the list of attributes that constitutes the data model.
        :param description: a short description for the data model.
        """
        self.name = name
        self.attribute_schemas = sorted(copy.deepcopy(attribute_schemas), key=lambda x: x.name)
        self.description = description
        self.attributes_by_name = {a.name: a for a in self.attribute_schemas}
        self._check_validity()

    @classmethod
    def from_pb(cls, model: dap_interface_pb2.DataModel):
        """
        Unpack the data model Protobuf object.

        :param model: the Protobuf object associated with the data model.
        :return: the data model.
        """

        name = model.name
        attributes = [AttributeSchema.from_pb(attr_pb) for attr_pb in model.attributes]
        description = model.description
        return cls(name, attributes, description)

    def to_pb(self):
        """
        Convert the data model into a Protobuf object

        :return: the associated DataModel Protobuf object.
        """
        model = dap_interface_pb2.DataModel()
        model.name = self.name
        model.attributes.extend([attr.to_pb() for attr in self.attribute_schemas])
        if self.description is not None:
            model.description = self.description
        return model

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description if self.description else "",
            "attributes": [attr.to_dict() for attr in self.attribute_schemas]
        }

    def _check_validity(self):
        # check if there are duplicated attribute names
        attribute_names = [attribute.name for attribute in self.attribute_schemas]
        if len(attribute_names) != len(set(attribute_names)):
            raise ValueError("Invalid input value for type '{}': duplicated attribute name."
                             .format(type(self).__name__))

    def __eq__(self, other):
        if type(other) != DataModel:
            return False
        else:
            return self.name == other.name and self.attribute_schemas == other.attribute_schemas


def generate_schema(model_name: str, attribute_values: Dict[str, ATTRIBUTE_TYPES]) -> DataModel:
    """
    Generate a schema that matches the values stored in this description.
    That is, for each attribute (name, value), generate an AttributeSchema.
    It is assumed that each attribute is required.

    :param model_name: the name of the model.
    :param attribute_values: the values of each attribute
    :return: the schema compliant with the values specified.
    """

    return DataModel(model_name, [AttributeSchema(k, type(v), True) for k, v in attribute_values.items()])


class Description(ProtobufSerializable):
    """
    Description of either a service or an agent so it can be understood by the OEF and other agents.
    Contains values of the description, and an optional schema for checking format of values.
    Whenever the description is changed (including when it is create), the attribute values will
    checked to make sure they do not violate the attribute schema.
    Examples:
        >>> It = Description({
        ..     "title" :           "It",
        ..     "author":           "Stephen King",
        ..     "genre":            "horror",
        ..     "year":             1986,
        ..     "average_rating":   4.5,
        ..     "ISBN":             "0-670-81302-8",
        ..     "ebook_available":  True
        .. })
        >>> _1984 = Description({
        ..     "title" :           "1984",
        ..     "author":           "George Orwell",
        ..     "genre":            "novel",
        ..     "year":             1949,
        ..     "ISBN":             "978-0451524935",
        ..     "ebook_available":  False
        .. })
    """
    @has_logger
    def __init__(self,
                 attribute_values: Dict[str, ATTRIBUTE_TYPES],
                 data_model: DataModel = None,
                 data_model_name: str = "") -> None:
        """
        Initialize a description.
        :param attribute_values: the values of each attribute in the description. This is a dictionary from
               | attribute name to attribute value, each attribute value must have a type in ATTRIBUTE_TYPES.
        :param data_model: optional schema of this description. If none is provided then the attribute values
               | will not be checked against a schema. Schemas are extremely useful for preventing
               | problems hard to debug, and are highly recommended.
        :param data_model_name: the name of the default data model. If a data model is provided,
               | this parameter is ignored.
        """
        self.values = copy.deepcopy(attribute_values)
        if data_model is not None:
            self.data_model = data_model
        else:
            self.data_model = generate_schema(data_model_name, attribute_values)

        self._check_consistency()

    @classmethod
    def from_pb(cls, query_instance: dap_interface_pb2.Actions):
        """
        Unpack the data model Protobuf object.
        :param query_instance: the Protobuf object associated with the data model.
        :return: the data model.
        """
        values = {}
        model  = None
        for kv in query_instance.actions:
            if kv.target_field_name == "data_model":
                model = DataModel.from_pb(kv.query_field_value)
                continue
            values[kv.target_field_name] = TypeHelpers.decodeConstraintValue(kv.query_field_value)
        return cls(values, model)

    def to_pb(self) -> dap_interface_pb2.Actions:
        """
        Return the description object as a Protobuf query instance.
        :return: the Protobuf query instance object associated to the description.
        """
        instance = dap_interface_pb2.Actions()
        dm = instance.actions.add()
        dm.target_field_name = "data_model"
        dm.query_field_value.typecode = "data_model"
        dm.query_field_value.dm.CopyFrom(self.data_model.to_pb())
        for key, value in self.values.items():
            kv = instance.actions.add()
            kv.target_field_name = key
            kv.query_field_value.CopyFrom(TypeHelpers.encodeConstraintValue(value, TypeHelpers.TYPECODE_MAP[type(value)],
                                                                            self.log))
        return instance

    def to_dict(self) -> dict:
        actions = [
            {
                "target_field_name": "data_model",
                "query_field_value": {
                    "typecode": "data_model",
                    "dm": self.data_model.to_dict()
                }
            }
        ]
        actions.extend([
            {
                "target_field_name": key,
                "query_field_value": TypeHelpers.encodeConstraintValueToDict(value,
                                                                             TypeHelpers.TYPECODE_MAP[type(value)],
                                                                             self.log)
            }
            for key, value in self.values.items()
        ])
        return  {"actions": actions}

    def to_agent_description_pb(self) -> agent_pb2.AgentDescription:
        """
        Convert the description into the Protobuf object associated to the AgentDescription message.
        :return: the associated AgentDescription Protobuf object.
        """
        description = agent_pb2.AgentDescription()
        description.description.CopyFrom(self.to_pb())
        return description

    def _check_consistency(self):
        """
        Checks the consistency of the values of this description.
        If an attribute_schemas has been provided, values are checked against that. If no attribute
        schema has been provided then minimal checking is performed based on the values in the
        provided attribute_value dictionary.
        :raises AttributeInconsistencyException: if values do not meet the schema, or if no schema is present
                                               | if they have disallowed types.
        """

        # check that all required attributes in the schema are contained in the description
        required_attributes = [s.name for s in self.data_model.attribute_schemas if s.required]
        if not all(a in self.values for a in required_attributes):
            raise AttributeInconsistencyException("Missing required attribute.")

        # check that all values are defined in the schema
        all_schema_attributes = [s.name for s in self.data_model.attribute_schemas]
        if not all(k in all_schema_attributes for k in self.values):
            raise AttributeInconsistencyException("Have extra attribute not in schema")

        # check that each of the values are consistent with that specified in the schema
        for schema in self.data_model.attribute_schemas:
            if schema.name in self.values:
                if type(self.values[schema.name]) != schema.type:
                    # values does not match type in schema
                    raise AttributeInconsistencyException(
                        "Attribute {} has incorrect type: {}".format(schema.name, schema.type))
                elif not isinstance(self.values[schema.name], ATTRIBUTE_TYPES.__args__):
                    # value type matches schema, but it is not an allowed type
                    raise AttributeInconsistencyException("Attribute {} has unallowed type".format(schema.name))
