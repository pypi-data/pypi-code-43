from dataclasses import dataclass
from typing import *
from .constants import *
from zuper_nodes.structures import TimingInfo

X = TypeVar('X')


@dataclass
class MsgReceived(Generic[X]):
    topic: str
    data: X
    timing: TimingInfo


@dataclass
class RawTopicMessage:
    topic: str
    data: Optional[dict]
    timing: Optional[dict]

@dataclass
class ControlMessage:
    code: str
    msg: Optional[str]


WireMessage = NewType('WireMessage', dict)

class Malformed(Exception):
    pass

def interpret_control_message(m: WireMessage) -> ControlMessage:
    if not isinstance(m, dict):
        msg = f'Expected dictionary, not {type(m)}.'
        raise Malformed(msg)
    if not FIELD_CONTROL in m:
        msg = f'Expected field {FIELD_CONTROL}, obtained {list(m)}.'
        raise Malformed(msg)
    code = m[FIELD_CONTROL]
    msg = m.get(FIELD_DATA, None)
    return ControlMessage(code, msg)
