import collections
import os
import uuid

import proton

import aorta.const
from aorta.lib.datastructures import DTO


class Message(proton.Message):
    """Augment :class:`proton.Message` with additional methods and
    properties.
    """
    message_class = None

    @property
    def dto(self):
        return DTO(**self.body)

    def is_aorta(self):
        """Return a boolean if the message represents a known Aorta
        type.
        """
        return self.message_class is not None

    def is_valid(self):
        """Return a boolean indicating if the :class:`Message` instance is
        valid according to the Aorta Infrastructure Protocol (AIP).
        """
        return True

    def get_message_id(self):
        """Returns a string representation of the message
        identifier.
        """
        message_id = None
        if self.id is None:
            message_id = 'null'
        elif isinstance(self.id, bytes):
            message_id = bytes.hex(self.id)
        elif isinstance(self.id, (uuid.UUID, str)):
            message_id = str(self.id)
        else:
            message_id = repr(self.id)
        return message_id

    def isconsumable(self):
        """Return a boolean indicating if the message is a consumable."""
        return False


class AortaMessage(Message):
    """The base class for all Aorta message types."""
    message_class = None

    @property
    def canonical(self):
        """Returns the canonical name of this message."""
        return self.properties[aorta.const.P_OBJECT_TYPE]

    def __init__(self, *args, **kwargs):
        Message.__init__(self, *args, **kwargs)
        if not isinstance(self.properties, dict):
            self.properties = {
                aorta.const.P_AORTA_ID: os.urandom(16),
                aorta.const.P_ENCRYPTED: False,
                aorta.const.P_SIGNED: False
            }
        assert self.message_class is not None,\
            "%s.message_class is None" % type(self).__name__
        self.properties[aorta.const.P_MESSAGE_CLASS] = self.message_class

    def set_object_type(self, name):
        """Sets the object type in the application properties."""
        self.properties[aorta.const.P_OBJECT_TYPE] = name


class EventMessage(AortaMessage):
    message_class = 'event'


class CommandMessage(AortaMessage):
    message_class = 'command'

    def isconsumable(self):
        """Return a boolean indicating if the message is a consumable."""
        return True


_types = collections.defaultdict(Message, {
    EventMessage.message_class: EventMessage,
    CommandMessage.message_class: CommandMessage
})


def factory(incoming):
    """Instantiate an Aorta message type from an incoming message
    through the Proton library.
    """
    props = incoming.properties or {}
    message = _types[props.get(aorta.const.P_MESSAGE_CLASS)]()
    message.decode(incoming.encode())
    return message
