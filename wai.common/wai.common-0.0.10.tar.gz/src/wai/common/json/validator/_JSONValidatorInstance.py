from abc import abstractmethod, ABC
from typing import Callable

from ..schema import JSONSchema
from .._typing import RawJSONElement
from ._JSONValidatorBase import JSONValidatorBase


class JSONValidatorInstance(JSONValidatorBase, ABC):
    """
    Mixin class which adds validation support for JSON at the instance level.
    """
    def with_validation(self, func: Callable[[], RawJSONElement]) -> Callable[[], RawJSONElement]:
        return JSONValidatorBase.with_validation(self, func)

    def validate_raw_json(self, raw_json: RawJSONElement):
        JSONValidatorBase.validate_raw_json(self, raw_json)

    def is_valid_raw_json(self, raw_json: RawJSONElement) -> bool:
        return JSONValidatorBase.is_valid_raw_json(self, raw_json)

    def validate_json_string(self, json_string: str):
        JSONValidatorBase.validate_json_string(self, json_string)

    def is_valid_json_string(self, json_string: str) -> bool:
        return JSONValidatorBase.is_valid_json_string(self, json_string)

    @abstractmethod
    def get_json_validation_schema(self) -> JSONSchema:
        pass

    def clone_json_validation_schema(self) -> JSONSchema:
        return JSONValidatorBase.clone_json_validation_schema(self)

    def perform_special_json_validation(self, raw_json: RawJSONElement):
        pass
