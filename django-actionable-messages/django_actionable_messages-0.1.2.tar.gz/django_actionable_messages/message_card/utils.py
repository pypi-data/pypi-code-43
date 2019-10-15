from enum import Enum


class OSType(str, Enum):
    DEFAULT = "default"
    WINDOWS = "windows"
    IOS = "iOS"
    ANDROID = "android"


class ChoiceStyle(str, Enum):
    NORMAL = "normal"
    EXPANDED = "expanded"
