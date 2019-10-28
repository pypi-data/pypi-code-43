from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class EventStatus(ExtendedEnum):
    UNRESPONDED = "unresponded"
    FAR = "far"
    NEAR = "near"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELED = "cancelled"


class ReportStatus(ExtendedEnum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELED = "cancelled"


class OptType(ExtendedEnum):
    OPT_IN = "optIn"
    OPT_OUT = "optOut"
    NONE = "none"
