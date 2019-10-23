from aorta.lib.datastructures import ImmutableDTO


class Context:

    @classmethod
    def fromincoming(cls, incoming):
        return cls(incoming)

    def __init__(self, message):
        self.message = message

    def handle(self, func):
        """Invokes callable `func` with the message parameters as
        its first positional argument. The message is considered to
        be cleaned and validated at this point, so we may assume
        that the message body is of the appropriate type (e.g. a
        Python dictionary).
        """
        return func(ImmutableDTO.fromdict(self.message.body))
