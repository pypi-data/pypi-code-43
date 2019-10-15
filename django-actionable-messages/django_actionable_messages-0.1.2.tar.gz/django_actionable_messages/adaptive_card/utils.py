from enum import Enum

VERSIONS = ("1.0", "1.1", "1.2")
SCHEMA = "http://adaptivecards.io/schemas/adaptive-card.json"


class FallbackOption(str, Enum):
    DROP = "drop"


class Style(str, Enum):
    DEFAULT = "default"
    EMPHASIS = "emphasis"
    GOOD = "good"
    ATTENTION = "attention"
    WARNING = "warning"
    ACCENT = "accent"


class HorizontalAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalAlignment(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class Color(str, Enum):
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    ACCENT = "accent"
    GOOD = "good"
    WARNING = "warning"
    ATTENTION = "attention"


class FontType(str, Enum):
    DEFAULT = "default"
    MONOSPACE = "monospace"


class FontSize(str, Enum):
    DEFAULT = "default"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extraLarge"


class FontWeight(str, Enum):
    DEFAULT = "default"
    LIGHTER = "lighter"
    BOLDER = "bolder"


class BlockElementHeight(str, Enum):
    AUTO = "auto"
    STRETCH = "stretch"


class SpacingStyle(str, Enum):
    DEFAULT = "default"
    NONE = "none"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extraLarge"
    PADDING = "padding"


class ImageSize(str, Enum):
    AUTO = "auto"
    STRETCH = "stretch"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ImageStyle(str, Enum):
    DEFAULT = "default"
    PERSON = "person"


class ActionStyle(str, Enum):
    DEFAULT = "default"
    POSITIVE = "positive"
    DESTRUCTIVE = "destructive"


class ChoiceInputStyle(str, Enum):
    COMPACT = "compact"
    EXPANDED = "expanded"


class TextInputStyle(str, Enum):
    TEXT = "text"
    TEL = "tel"
    URL = "url"
    EMAIL = "email"


class Width(str, Enum):
    AUTO = "auto"
    STRETCH = "stretch"


class FillMode(str, Enum):
    COVER = "cover"
    REPEAT_HORIZONTALLY = "repeatHorizontally"
    REPEAT_VERTICALLY = "repeatVertically"
    REPEAT = "repeat"
