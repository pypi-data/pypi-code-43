name = "GoogleActions"
from enum import Enum


from PyVoice.MyDict import MyDict, DictProperty


class MediaType(Enum):
    MEDIA_TYPE_UNSPECIFIED = 'MEDIA_TYPE_UNSPECIFIED'
    AUDIO = 'AUDIO'


from PyVoice.MyDict import MyDict, DictProperty


class InputType(Enum):
    UNSPECIFIED_INPUT_TYPE = 'UNSPECIFIED_INPUT_TYPE'
    TOUCH = 'TOUCH'
    VOICE = 'VOICE'
    KEYBOARD = 'KEYBOARD'
    URL = 'URL'


from PyVoice.MyDict import MyDict, DictProperty


class ImageDisplayOptions(Enum):
    #Fill the gaps between the image and the image container with gray bars.
    DEFAULT = 'DEFAULT'

    # Fill the gaps between the image and the image container with white bars.
    WHITE = 'WHITE'

    # Image is scaled such that the image width and height match or exceed the container dimensions. This may crop the
    # top and bottom of the image if the scaled image height is greater than the container height, or crop the left and
    # right of the image if the scaled image width is greater than the container width. This is similar to "Zoom Mode"
    # on a widescreen TV when playing a 4:3 video.
    CROPPED = 'CROPPED'


from PyVoice.MyDict import MyDict, DictProperty


class PriceType(Enum):
    UNKNOWN = 'UNKNOWN'
    ESTIMATE = 'ESTIMATE'
    ACTUAL = 'ACTUAL'


from PyVoice.MyDict import MyDict, DictProperty


class ReasonType(Enum):
    UNKNOWN = 'UNKNOWN'
    PAYMENT_DECLINED = 'PAYMENT_DECLINED'
    INELIGIBLE = 'INELIGIBLE'
    PROMO_NOT_APPLICABLE = 'PROMO_NOT_APPLICABLE'
    UNAVAILABLE_SLOT = 'UNAVAILABLE_SLOT'


from PyVoice.MyDict import MyDict, DictProperty


class ActionType(Enum):
    UNKNOWN = 'UNKNOWN'
    VIEW_DETAILS = 'VIEW_DETAILS'
    MODIFY = 'MODIFY'
    CANCEL = 'CANCEL'
    RETURN = 'RETURN'
    EXCHANGE = 'EXCHANGE'
    EMAIL = 'EMAIL'
    CALL = 'CALL'
    REORDER = 'REORDER'
    REVIEW = 'REVIEW'
    CUSTOMER_SERVICE = 'CUSTOMER_SERVICE'
    FIX_ISSUE = 'FIX_ISSUE'

from PyVoice.MyDict import MyDict, DictProperty


class UrlTypeHint(Enum):
    URL_TYPE_HINT_UNSPECIFIED = 'URL_TYPE_HINT_UNSPECIFIED'
    AMP_CONTENT = 'AMP_CONTENT'

from PyVoice.MyDict import MyDict, DictProperty


class Permission(Enum):
    UNSPECIFIED_PERMISSION = 'UNSPECIFIED_PERMISSION'
    NAME = 'NAME'
    DEVICE_PRECISE_LOCATION = 'DEVICE_PRECISE_LOCATION'
    DEVICE_COARSE_LOCATION = 'DEVICE_COARSE_LOCATION'
    UPDATE = 'UPDATE'

class HorizontalAlignment(Enum):
    LEADING = 'LEADING'
    CENTER = 'CENTER'
    TRAILING = 'TRAILING'
