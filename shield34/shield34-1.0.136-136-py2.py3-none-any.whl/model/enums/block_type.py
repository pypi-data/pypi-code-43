from enum import Enum


class BlockType(Enum):
    UNKNOWN = "unknown"
    BEFORE_METHOD = "before_method"
    AFTER_METHOD = "after_method"
    BEFORE_CLASS = "before_class"
    AFTER_CLASS = "after_class"
    BEFORE_SUITE = "before_suite"
    AFTER_SUITE = "after_suite"
    TEST = "test"
