name = "DialogFlowPy"
from enum import Enum


class Platform(Enum):
    PLATFORM_UNSPECIFIED = 'PLATFORM_UNSPECIFIED'
    FACEBOOK = 'FACEBOOK'
    SLACK = 'SLACK'
    TELEGRAM = 'TELEGRAM'
    KIK = 'KIK'
    SKYPE = 'SKYPE'
    LINE = 'LINE'
    VIBER = 'VIBER'
    ACTIONS_ON_GOOGLE = 'ACTIONS_ON_GOOGLE'