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

    # CP <-> BR
    Register = 1
    AssignmentRequest = 2
    Assignment = 3
    Terminate = 4
    SlowQueueAlert = 5
    NewInputSource = 6

    # BR <-> BR
    Packet = 20
    PacketRequest = 21
    ConsumerRegistration = 22


Message = namedtuple("Message", ("type", "content"))

# pylint: disable=invalid-name
RegisterMessage = partial(Message, MessageType.Register)
AssignmentMessage = partial(Message, MessageType.Assignment)
AssignmentRequest = partial(Message, MessageType.AssignmentRequest)
TerminateMessage = partial(Message, MessageType.Terminate)
TERMINATE = TerminateMessage(None)

SlowQueueAlert = partial(Message, MessageType.SlowQueueAlert)
InputSourceMessage = partial(Message, MessageType.NewInputSource)

PacketMessage = partial(Message, MessageType.Packet)
PacketRequest = partial(Message, MessageType.PacketRequest)
ConsumerRegistration = partial(Message, MessageType.ConsumerRegistration)


AssignmentContent = namedtuple(
    "AssignmentContent", "brick_description input_sources output_targets"
)
BrickDescription = namedtuple(
    "BrickDescription", "flowname name parameters uid path_to_module is_inlet"
)
OutputTarget = namedtuple("OutputTarget", "name port autoscale_queue_level")
InputSource = namedtuple("InputSource", "name port address")
