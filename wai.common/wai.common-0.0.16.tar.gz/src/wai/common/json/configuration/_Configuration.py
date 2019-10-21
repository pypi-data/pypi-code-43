from abc import ABC
from typing import Dict, TypeVar, List, Any, Union, Tuple, Type

from wai.common.json.configuration.property import RawProperty
from .property._MapProxy import MapProxy
from ._Absent import Absent
from ..schema import JSONSchema, standard_object, IS_JSON_SCHEMA, IS_JSON_DEFINITION
from ..schema.constants import DEFINITIONS_KEYWORD
from .property import Property
from .._typing import RawJSONObject
from ..serialise import JSONValidatedBiserialisable

T = TypeVar("T", bound="Configuration")


class Configuration(JSONValidatedBiserialisable[T], ABC):
    """
    Base class for Python representations of JSON-format configuration files.
    All configurations are validated against a schema for format correctness.
    The attributes of a configuration should be either JSON types or nested
    configurations.
    """
    # Cache of sub-class schema
    __schema_cache: Dict[Type["Configuration"], JSONSchema] = {}

    def __init__(self, **initial_values):
        # Get the properties
        properties = self.get_all_properties()

        # Make sure no properties are set twice
        for attribute_name, property in properties.items():
            if attribute_name in initial_values and \
                    property.name() in initial_values and \
                    property.name() not in properties:
                raise ValueError(f"Value for property {property.name()} (attribute "
                                 f"name '{attribute_name}') specified twice")

        # Set the properties with initial values, favouring attribute names
        for attribute_name, property in properties.items():
            # Get the initial value for the property (absent if not specified)
            initial_value = initial_values.pop(attribute_name
                                               if attribute_name in initial_values
                                               else property.name(),
                                               Absent)

            # Attempt to set the value
            try:
                # Set explicitly first
                property.__set__(self, initial_value)
            except Exception as e:
                try:
                    # If that fails, set by JSON
                    property.set_from_raw_json(self, initial_value)
                except Exception as e2:
                    # If that fails as well, let the exception escape
                    raise e2 from e

        # Treat remaining initial values as additional properties
        self._additional_properties = self.init_additional_properties(**initial_values)

    @classmethod
    def init_additional_properties(cls, **initial_values):
        """
        Initialises the additional-properties storage for this configuration.

        :param initial_values:  The initial values that weren't explicit properties.
        """
        # Create the closure of the sub-property
        sub_property: Property = cls._additional_properties_sub_property[0]

        # Create a map closure class to act as the storage
        class AdditionalPropertiesProxy(MapProxy):
            @classmethod
            def sub_property(cls) -> Property:
                return sub_property

        # Create the storage
        return AdditionalPropertiesProxy(**initial_values)

    def __getattr__(self, item: str):
        # Return the value of the additional property if present
        if item in self._additional_properties:
            return self._additional_properties[item]

        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{item}'")

    def __setattr__(self, key: str, value):
        # Set any unknown attribute in the additional values
        if key != "_additional_properties":
            if not hasattr(self, key) or key in self._additional_properties:
                self._additional_properties[key] = value

        super().__setattr__(key, value)

    def _serialise_to_raw_json(self) -> RawJSONObject:
        # Get a list of all properties
        properties = list(self.get_all_properties().values())

        # Convert the properties to JSON (includes Absent values)
        json_with_absents = {
            property.name(): property.get_as_raw_json(self)
            for property in properties
        }

        # Strip the absent values
        json = {
            key: value
            for key, value in json_with_absents.items()
            if value is not Absent
        }

        # Add any additional properties
        json.update(self._additional_properties)

        return json

    @classmethod
    def _deserialise_from_raw_json(cls, raw_json: RawJSONObject) -> T:
        return cls(**raw_json)

    @classmethod
    def get_json_validation_schema(cls) -> JSONSchema:
        # Get the cached version if possible
        if cls in Configuration.__schema_cache:
            return Configuration.__schema_cache[cls]

        # Get the properties of this configuration type
        properties: Dict[str, Property] = cls.get_all_properties(True)

        # Extract the required property schemas
        required_properties_schema: Dict[str, JSONSchema] = {
            name: property.get_json_validation_schema()
            for name, property in properties.items()
            if not property.is_optional()
        }

        # Extract the optional property schemas
        optional_properties_schema: Dict[str, JSONSchema] = {
            name: property.get_json_validation_schema()
            for name, property in properties.items()
            if property.is_optional()
        }

        # Extract the additional properties schema
        additional_properties_schema: JSONSchema = cls._additional_properties_sub_property[0]\
            .get_json_validation_schema()

        # Create the schema
        schema: JSONSchema = standard_object(required_properties_schema,
                                             optional_properties_schema,
                                             additional_properties=additional_properties_schema)

        # Cache the schema
        Configuration.__schema_cache[cls] = schema

        return schema

    @classmethod
    def get_all_properties(cls, with_property_names: bool = False) -> Dict[str, Property]:
        """
        Gets all properties of this configuration.

        :param with_property_names:     Whether the keys should be the property names (by default
                                        they are the attribute names).
        :return:                        A dictionary of the properties of this configuration.
        """
        # Get the attribute names
        attribute_names: List[str] = dir(cls)

        # Get the mapping from attribute name to attribute
        attributes: Dict[str, Any] = {name: getattr(cls, name)
                                      for name in attribute_names
                                      if not name.startswith("_")}

        # Get the properties
        properties = {
            name: attribute
            for name, attribute in attributes.items()
            if isinstance(attribute, Property)
        }

        # Convert the names to the property names if requested
        if with_property_names:
            properties = {property.name(): property for property in properties.values()}

        return properties

    @classmethod
    def additional_properties_validation(cls) -> Union[JSONSchema, Property]:
        """
        Gets the schema/property to validate any additional properties set
        on this configuration. By default all additional properties are allowed.
        Override to modify this behaviour.
        """
        schema: JSONSchema = {DEFINITIONS_KEYWORD: IS_JSON_DEFINITION}
        schema.update(IS_JSON_SCHEMA)
        return schema

    def __init_subclass__(cls, **kwargs):
        # Perform any super initialisation
        super().__init_subclass__(**kwargs)

        # Make sure the property names are unique
        property_names = [property.name() for property in cls.get_all_properties().values()]
        if len(property_names) != len(set(property_names)):
            raise TypeError(f"Duplicate property names in {cls.__name__}: {', '.join(property_names)}")

        # Initialise the additional properties validation property
        property = cls.additional_properties_validation()
        if not isinstance(property, Property):
            property = RawProperty("", property)
        cls._additional_properties_sub_property: Tuple[Property] = (property,)  # Wrapped in a tuple to avoid discovery
