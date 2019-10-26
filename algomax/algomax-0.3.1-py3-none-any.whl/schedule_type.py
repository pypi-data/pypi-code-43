from enum import Enum


class ScheduleType(Enum):
    """
    an enum that contains all acceptable scheduling types
    """
    ONCE = 'once'
    INTERVAL = 'interval'
