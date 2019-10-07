from abc import abstractmethod
from typing import Tuple, Optional, List
from weakref import WeakKeyDictionary

from ...schema import JSONSchema
from ..._typing import RawJSONElement
from .._OptionallyPresent import OptionallyPresent
from .._Absent import Absent
from ._Property import Property
from ._DummyInstance import DummyInstance


class OfProperty(Property):
    """
    Base class for OneOfProperty and AnyOfProperty.
    """
    def __init__(self,
                 name: str,
                 *sub_properties: Property,
                 schema_function,  # one_of/any_of
                 optional: bool = False):
        super().__init__(
            name,
            optional=optional
        )

        self._sub_properties: Tuple[Property] = sub_properties
        self._instance_keys = WeakKeyDictionary()
        self.__schema_function = schema_function

    def get_json_validation_schema(self) -> JSONSchema:
        return self.__schema_function(
            *(
                property.get_json_validation_schema()
                for property in self._sub_properties
            )
        )

    def set_search_with_revert(self, instance, value, set_method):
        """
        Attempts to set this property, and reverts to the current
        value if setting fails.

        :param instance:    The instance to set the value for.
        :param value:       The value to set.
        :param set_method:  A function which returns the set-method
                            to use on an object.
        """
        # Make sure instance is not None
        self._require_instance(instance)

        # Attempt to get the current value
        try:
            current_value = self.__get__(instance, None)
        except AttributeError as e:
            # No current value
            current_value = e

        # Try to set the value
        try:
            self.set_search(instance, value, set_method)
        except Exception as e:
            if not isinstance(current_value, AttributeError):
                self.__set__(instance, current_value)

            raise e

    def set_search(self, instance, value, set_method):
        """
        Performs the logic of setting the value for this property.

        :param instance:    The instance to set the value for.
        :param value:       The value to set.
        :param set_method:  A function which returns the set-method
                            to use on an object.
        """
        # If the value is absent, set it directly
        if value is Absent:
            # Remove the current instance key if there is one
            if instance in self._instance_keys:
                self._instance_keys.pop(instance)

            super().__set__(instance, Absent)

            return

        # Find the properties this value is valid for
        keys = []
        for property in self._sub_properties:
            try:
                # Create a new key for this value
                keys.append(DummyInstance())

                set_method(property)(keys[-1], value)
            except Exception:
                keys[-1] = None

        # Select the canonical index
        key_index = self.choose_current_property(keys)

        # Save it
        super().__set__(instance, key_index)
        self._instance_keys[instance] = keys[key_index]

    @abstractmethod
    def choose_current_property(self, keys: List[Optional[DummyInstance]]) -> int:
        """
        Allows the sub-classes to choose which sub-property should
        store the value based on the success or failure of all sub-
        properties being set. Should raise an attribute error if it
        can't decide.

        :param keys:    The list of keys for the properties that were set,
                        and Nones for the properties that weren't.
        :return:        The index of the property to regard as storing the
                        value.
        """
        pass

    def __get__(self, instance, owner):
        # Get the current value
        value = super().__get__(instance, owner)

        # If it's an index, return the value of the sub-property
        # at that index
        if isinstance(value, int):
            return self._sub_properties[value].__get__(self._instance_keys[instance], owner)

        # Otherwise it's absent or self
        return value

    def __set__(self, instance, value):
        self.set_search_with_revert(instance,
                                    value,
                                    lambda property: property.__set__)

    def get_as_raw_json(self, instance) -> OptionallyPresent[RawJSONElement]:
        # Make sure instance is not None
        self._require_instance(instance)

        # Get the current value
        value = super().__get__(instance, None)

        # If it's an index, return the JSON of the sub-property
        # at that index
        if isinstance(value, int):
            return self._sub_properties[value].get_as_raw_json(self._instance_keys[instance])

        # Otherwise it's absent or self
        return value

    def set_from_raw_json(self, instance, value: OptionallyPresent[RawJSONElement]):
        self.set_search_with_revert(instance,
                                    value,
                                    lambda property: property.set_from_raw_json)

    def validate_value(self, value):
        super().validate_value(value)

        # No need to continue validation if value is absent
        if value is Absent:
            return

        # Our values are indices into the sub-properties
        if not isinstance(value, int) or not (0 <= value < len(self._sub_properties)):
            raise AttributeError(f"Error in internal index for Of property. "
                                 f"Index should be integer in [0:{len(self._sub_properties)}), "
                                 f"got {value}")
