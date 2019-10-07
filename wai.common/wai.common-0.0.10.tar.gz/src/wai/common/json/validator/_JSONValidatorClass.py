from abc import abstractmethod, ABC
from typing import Callable

from ..schema import JSONSchema
from .._typing import RawJSONElement
from ._JSONValidatorBase import JSONValidatorBase
from ._JSONValidatorInstance import JSONValidatorInstance


class JSONValidatorClass(JSONValidatorInstance, ABC):
    """
    Mixin class which adds validation support for JSON at the class level. Derives
    from JSONValidatorInstance as instances can still access the class-level validation.
    """
    @classmethod
    def with_validation(cls, func: Callable[[], RawJSONElement]) -> Callable[[], RawJSONElement]:
        return JSONValidatorBase.with_validation(cls, func)

    @classmethod
    def validate_raw_json(cls, raw_json: RawJSONElement):
        JSONValidatorBase.validate_raw_json(cls, raw_json)

    @classmethod
    def is_valid_raw_json(cls, raw_json: RawJSONElement) -> bool:
        return JSONValidatorBase.is_valid_raw_json(cls, raw_json)

    @classmethod
    def validate_json_string(cls, json_string: str):
        JSONValidatorBase.validate_json_string(cls, json_string)

    @classmethod
    def is_valid_json_string(cls, json_string: str) -> bool:
        return JSONValidatorBase.is_valid_json_string(cls, json_string)

    @classmethod
    @abstractmethod
    def get_json_validation_schema(cls) -> JSONSchema:
        pass

    @classmethod
    def clone_json_validation_schema(cls) -> JSONSchema:
        return JSONValidatorBase.clone_json_validation_schema(cls)

    @classmethod
    def perform_special_json_validation(cls, raw_json: RawJSONElement):
        pass
