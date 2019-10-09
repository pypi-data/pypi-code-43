from pyqalx.core.adapters.adapter import QalxNamedEntityAdapter
from pyqalx.core.entities import Queue
from pyqalx.core.errors import QalxEntityNotFound


class QalxQueue(QalxNamedEntityAdapter):
    _entity_class = Queue
    _bot_only_methods = ['get_messages']

    @property
    def _queue_params(self):
        """
        The configurable parameters for a `Queue`
        :return:
        """
        return {
            'VisibilityTimeout': int(self.session.config['MSG_BLACKOUTSECONDS'])
        }

    def add(self, name, meta=None, **kwargs):
        """
        Queues are created with a name.  This name is stored in the metadata
        of the `Queue` instance

        :param name: The name we want to assign the Queue
        :type name: str
        :param meta: A dictionary of metadata to store
        :type meta: dict
        :param kwargs: Any other kwargs we are setting on the Queue
        :return: A newly created `Queue` instance
        """
        return super(QalxQueue, self).add(parameters=self._queue_params,
                                          name=name,
                                          meta=meta,
                                          **kwargs)

    def get_messages(self, queue):
        """
        Gets the messages on the `Queue` instance

        :return: A list of `QueueMessage` instances
        """
        config = self.session.config
        max_msgs = int(config["Q_MSGBATCHSIZE"])
        visibility = int(config["MSG_BLACKOUTSECONDS"])
        waittime = int(config["MSG_WAITTIMESECONDS"])

        message = queue.get_messages(max_msgs, visibility, waittime)
        return message

    def get_by_name(self, name):
        """a single queue by name

        :param name: name of queue
        :type name: str
        :return: pyqalx.core.entities.Queue
        :raises: pyqalx.errors.QalxReturnedMultipleError,
                 pyqalx.errors.QalxEntityNotFound
        """
        return self.find(many=False, name=name)

    def get_or_create(self, name, meta=None, **kwargs):
        """
        Gets a Queue by the given name or creates it if it doesn't exist

        :param name:
        :type name: str
        :param meta: metadata about the queue
        :return: pyqalx.core.entities.Queue
        """
        try:
            return self.get_by_name(name=name)
        except QalxEntityNotFound:
            return self.add(name, meta=meta)

