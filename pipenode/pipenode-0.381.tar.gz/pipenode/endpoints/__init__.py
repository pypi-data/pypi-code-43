

def isInputEndpoint(obj):
    return isinstance(obj, (AbstractInputEndpoint, AbstractCoroutineInputEndpoint))


def isOutputEndpoint(obj):
    return isinstance(obj, (AbstractOutputEndpoint, AbstractCoroutineOutputEndpoint))


def isCoroutineInputEndpoint(obj):
    return isinstance(obj, AbstractCoroutineInputEndpoint)


def isCoroutineOutputEndpoint(obj):
    return isinstance(obj, AbstractCoroutineOutputEndpoint)


class AbstractInputEndpoint:
    """Abstract input endpoint"""

    def get(self):
        """Get a message from queue and parse message into a Task object

        Return a Task object, or raise its exception
        """
        raise NotImplementedError


class AbstractOutputEndpoint:
    """Abstract output endpoint"""

    def put(self, task):
        """Parse Task object into message and put into queue
        """
        raise NotImplementedError


class AbstractCoroutineInputEndpoint:
    """Abstract coroutine input endpoint"""

    async def get(self):
        """Get a message from queue and parse message into a Task object

        Return a Task object, or raise its exception
        """
        raise NotImplementedError


class AbstractCoroutineOutputEndpoint:
    """Abstract coroutine output endpoint"""

    async def put(self, task):
        """Parse Task object into message and put into queue
        """
        raise NotImplementedError