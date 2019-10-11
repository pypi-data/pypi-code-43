#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""Messages within titanfe"""

from collections import namedtuple
from functools import partial
from enum import IntEnum


class MessageType(IntEnum):
    """Types of Messages used within titanfe"""

    Register = 1
    AssignmentRequest = 2
    Assignment = 3
    Terminate = 4
    Packet = 20
    PacketRequest = 21


Message = namedtuple("Message", ("type", "content"))

# pylint: disable=invalid-name
AssignmentMessage = partial(Message, MessageType.Assignment)
AssignmentRequest = partial(Message, MessageType.AssignmentRequest)
PacketMessage = partial(Message, MessageType.Packet)
PacketRequest = partial(Message, MessageType.PacketRequest)
RegisterMessage = partial(Message, MessageType.Register)
TerminateMessage = partial(Message, MessageType.Terminate)

TERMINATE = TerminateMessage(None)

AssignmentContent = namedtuple("AssignmentContent", "brick_description output_targets")
BrickDescription = namedtuple(
    "BrickDescription",
    "flowname name parameters uid path_to_module is_inlet"
)
