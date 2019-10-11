from .config_loader import *
from .errors import *
from .extensions import *
from .inspect_tools import *
from .logging import *
from .re_dict import *
from .subrequest_classes import *
from .types import *

@property
def re_type():
    from warnings import warn
    warn("re_type is going to be deprecated. Use RegExpType instead", DeprecationWarning, 2)
    return RegExpType

__all__ = \
[
    'revrange',
    'server_request_to_client_request',
    'setup_logging',
    'logging_method',
    'is_list_type',
    'unfold_list_type',
    'unfold_json_dataclass_list_type',
    
    'JsonSerializable',
    're_type',
    'RegExpType',
    'ConfigLoader',
    'ExtendedLogger',
    'RequestLogger',
    'StyleAdapter',
    'HttpSubrequest',
    'HttpSubrequestResponse',
    'ServerError',
    'SubrequestFailedErrorCodes',
    'SubrequestFailedError',
    'ReDict',
]
