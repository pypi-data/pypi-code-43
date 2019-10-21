import json
from abc import ABC, abstractmethod
from typing import Callable

import jsonschema

from .._typing import RawJSONElement
from .._error import JSONError
from .._deep_copy import deep_copy
from ..schema import JSONSchema
from ...meta import does_not_raise


class JSONValidatorBase(ABC):
    """
    Provides base functionality for JSON validator interfaces.
    """
    @staticmethod
    def with_validation(self, func: Callable[[], RawJSONElement]) -> Callable[[], RawJSONElement]:
        """
        Decorator which adds validation to a function returning raw JSON.

        :param self:    The validator instance/class.
        :param func:    The function to decorate.
        :return:        The decorated function.
        """
        def validated() -> RawJSONElement:
            # Call the function
            raw_json: RawJSONElement = func()

            # Perform validation
            self.validate_raw_json(raw_json)

            return raw_json

        return validated

    @staticmethod
    def validate_raw_json(self, raw_json: RawJSONElement):
        """
        Validates the raw JSON using this object's validation methods
        (schema, special).

        :param self:        The validator instance/class.
        :param raw_json:    The raw JSON to validate.
        """
        try:
            # Perform schema validation
            jsonschema.validate(raw_json, self.get_json_validation_schema())

            # Perform special validation
            self.perform_special_json_validation(raw_json)
        except Exception as e:
            raise JSONError("Error validating raw JSON element") from e

    @staticmethod
    def is_valid_raw_json(self, raw_json: RawJSONElement) -> bool:
        """
        Checks if the raw JSON is valid.

        :param self:        The validator instance/class.
        :param raw_json:    The raw JSON to check.
        :return:            True if the JSON is valid,
                            False if not.
        """
        return does_not_raise(self.validate_raw_json, raw_json)

    @staticmethod
    def validate_json_string(self, json_string: str):
        """
        Validates the JSON-format string using this object's validation methods
        (schema, special).

        :param self:            The validator instance/class.
        :param json_string:     The JSON-format string to validate.
        """
        try:
            # Convert the string to raw JSON
            raw_json = json.loads(json_string)

            # Validate the raw JSON
            self.validate_raw_json(raw_json)
        except Exception as e:
            raise JSONError(f"Error validating JSON-format string {json_string}") from e

    @staticmethod
    def is_valid_json_string(self, json_string: str) -> bool:
        """
        Checks if the JSON-format string is valid.

        :param self:            The validator instance/class.
        :param json_string:     The JSON-format string to check.
        :return:                True if the JSON is valid,
                                False if not.
        """
        return does_not_raise(self.validate_json_string, json_string)

    @staticmethod
    @abstractmethod
    def get_json_validation_schema(self) -> JSONSchema:
        """
        Gets the schema to validate JSON for objects of this type.
        This may be a cached object, so if it is necessary to modify
        the schema, use clone_json_validation_schema instead.

        :param self:    The validator instance/class.
        :return:        The schema.
        """
        pass

    @staticmethod
    def clone_json_validation_schema(self) -> JSONSchema:
        """
        Gets a copy of the validation schema for this validator.
        Use this if you need to modify the schema.

        :param self:    The validator instance/class.
        :return:        The copy of the schema.
        """
        return deep_copy(self.get_json_validation_schema())

    @staticmethod
    def perform_special_json_validation(self, raw_json: RawJSONElement):
        """
        Optional method to perform custom validation of raw JSON elements
        for objects of this type. Should throw an exception if the raw JSON
        element doesn't meet the special validation criteria. By default
        does nothing.

        :param self:        The validator instance/class.
        :param raw_json:    The raw JSON to validate.
        """
        pass
