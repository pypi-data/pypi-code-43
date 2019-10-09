from abc import ABC
from typing import TypeVar

from ..schema import JSONSchema, TRIVIALLY_FAIL_SCHEMA
from ._Configuration import Configuration

T = TypeVar("T", bound="StrictConfiguration")


class StrictConfiguration(Configuration[T], ABC):
    """
    Base class for configurations which don't support additional
    properties by default.
    """
    @classmethod
    def additional_properties_validation(cls) -> JSONSchema:
        return TRIVIALLY_FAIL_SCHEMA
