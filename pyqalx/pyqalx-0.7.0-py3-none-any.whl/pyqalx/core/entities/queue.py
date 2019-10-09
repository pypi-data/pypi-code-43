import json
import threading
from datetime import datetime, timezone
import uuid

import boto3
import dateutil
import logging
from botocore.exceptions import ClientError

from pyqalx.core.entities import QalxEntity, Group, Item, Set
from pyqalx.core.errors import QalxQueueError


logger = logging.getLogger(__name__)


class QueueResponse:
    """a response from a remote queue"""

    def __init__(self, response):
        """make new response

        v0.1 - doesn't do much yet
        :param response: response from queue
        """
        self._raw_response = response


class QueueMessage:
    """a message frm the queue

    attributes:
        body: message body
        receipt_handle: some information to return to the message broker to confirm receipt
    """

    def __init__(self, message):
        """

        :param message: the full raw message from the queue
        """
        self._raw_message = message
        self.body = json.loads(message['Body'])
        self.receipt_handle = message['ReceiptHandle']
        self._heartbeats = 1
        self._heartbeat = None

    def _stop_heartbeat(self):
        if self._heartbeat is not None:
            self._heartbeat.set()
            # Make sure that if we start the heartbeat again on this message
            # it starts from 1
            self._heartbeats = 1

    def _do_heartbeat(self, visibility, queue):
        """
        A QalxJob might take a long time to process.  Therefore, we
        use a heartbeat on the message to keep it in flight for as long
        as possible.
        :param visibility: The `MSG_BLACKOUTSECONDS` from the bot_config.
        :param queue: An instance of :class:~queue.Queue
        :return:
        """
        if self._heartbeat is None or self._heartbeat.is_set() is False:
            # We only do the heartbeat if it hasn't been started yet and we
            # haven't unset it
            self._heartbeat = threading.Event()

            # Ensure it's an int - it might not be if it's come from the config
            visibility = int(visibility)

            visibility = visibility * self._heartbeats

            # The max timeout for a message is 12 hours in seconds
            MAX_VISIBILITY_TIMEOUT = 43200
            if visibility <= MAX_VISIBILITY_TIMEOUT:
                # Don't change visibility the first time as the message will
                # be in flight anyway
                try:
                    queue.broker_client.change_message_visibility(
                        QueueUrl=queue['info']['queue_url'],
                        ReceiptHandle=self.receipt_handle,
                        VisibilityTimeout=visibility
                    )
                except ClientError as exc:
                    # ClientError: There was an issue changing the visibility.
                    #    This can happen if we delete the message at the same
                    #    time as we are changing the visibility (which is
                    #    possible as the heartbeat is a thread within the
                    #    Worker process).  Just return and let the Worker
                    #    handle the heartbeat again (probably resulting in
                    #    stopping it)
                    logger.debug(f'Got ClientError when extending heartbeat.  '
                                 f'Error was: `{exc}`')
                    # Wait for a single second to help prevent multiple requests
                    # being fired to AWS
                    self._heartbeat.wait(1)
                    return

            # We keep track of the number of heartbeats this message has had
            # and simply increase the visibility timeout exponentially
            self._heartbeats += 1
            # Get roughly 90 percent of the updated visibility time.
            # Sleep until that time expires and then increase the
            # message visibility the next time this method is called
            ninety_percent = visibility - int(visibility / 10)
            self._heartbeat.wait(ninety_percent)


class Queue(QalxEntity):
    """QalxEntity with entity_type Queue

    attributes:
        broker_client: an authenticated client to communicate with the remote message broker
    """
    entity_type = 'queue'

    def _stringify(self, message: dict) -> str:
        return json.dumps(message)

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(*args, **kwargs)
        self.__super_setbroker_client__()

    def __super_setbroker_client__(self, broker_client=None):
        # Use __super_setattr__ to ensure that the `_broker_client` is
        # set as an attribute - not an ObjectDict
        self.__super_setattr__('_broker_client', broker_client)

    @property
    def broker_client(self):
        """
        Windows can't pickle the client if it gets set on __init__ therefore,
        we set it to an internal attribute and cache it for the duration of
        the Queue to avoid getting the client multiple times
        """
        if self._broker_client is None \
                and self.get('info')\
                and ('credentials' in self['info']):

                _broker_client = \
                    boto3.client('sqs',
                                 region_name="eu-west-2",  # TODO: #2756 make this configurable
                                 aws_access_key_id=self['info']['credentials']['ACCESS_KEY_ID'],
                                 aws_secret_access_key=self['info']['credentials']['SECRET_ACCESS_KEY'],
                                 aws_session_token=self['info']['credentials']['SESSION_TOKEN'])
                # Use __super_setattr__ to ensure that the `_broker_client` is
                # set as an attribute - not an ObjectDict
                self.__super_setbroker_client__(_broker_client)
        return self._broker_client

    def _credentials_expiring_soon(self):
        """
        Returns True if the credentials are expiring soon.  The expiration
        datetime will be a UTC timestamp in isoformat
        """
        expiration = dateutil.parser.parse(self['info']['credentials']['EXPIRATION'])
        # Refresh when 1 hour or less left on the expiration token
        REFRESH_LIMIT_HOURS = 3600
        return (expiration - datetime.now(timezone.utc)).seconds <= REFRESH_LIMIT_HOURS

    def submit_sets_from_group(self, group):
        """

        :param group: a group
        :type group: `~pyqalx.core.Group`
        :returns: `pyqalx.core.queue.QueueResponse`
        """

        responses = []

        for chunk in self._chunks(list(group['sets'].values()), chunk_size=10):
            chunked_objects = filter(None, chunk)
            entries = []
            for n, set_guid in enumerate(chunked_objects):
                entries.append(
                    {
                        "Id": str(uuid.uuid4()),
                        'MessageBody': json.dumps({
                            "entity_type": "set",
                            "entity_guid": set_guid,
                            "parent_group_guid": group['guid']
                        }),
                        # Unique MessageGroupId to prevent processing
                        # duplicates
                        "MessageGroupId": str(uuid.uuid4()),
                        # Unique MessageDeduplicationId to allow the user
                        # to put the same entity on the queue multiple times
                        "MessageDeduplicationId": str(uuid.uuid4()),
                    })

            if entries:
                responses.append(self.broker_client.send_message_batch(
                    QueueUrl=self['info']['queue_url'],
                    Entries=entries
                ))

        return QueueResponse(responses)

    def get_messages(self, max_num_msg, visibility, waittime):
        """get messages from the queue

        :param max_num_msg: maximum number to retrieve
        :param visibility: time in seconds until the message becomes visible again on the queue
        :param waittime: time to wait for a message
        :return: list of `pyqalx.core.entities.queue.QueueMessage`
        """

        responses = self.broker_client.receive_message(
            QueueUrl=self['info']['queue_url'],
            MaxNumberOfMessages=max_num_msg,
            VisibilityTimeout=visibility,
            WaitTimeSeconds=waittime,
        )
        if not responses.get("Messages"):
            return []
        else:
            return [QueueMessage(response) for response in responses['Messages']]

    def delete_message(self, message):
        """remove message from the queue

        :param message: message to delete
        :type message: `QalxMessage`
        :return: None
        """
        if message is not None:
            # message could be None if the job it's been
            # on has been told to wait - therefore, don't attempt delete
            self.broker_client.delete_message(
                QueueUrl=self['info']['queue_url'],
                ReceiptHandle=message.receipt_handle
            )

    def submit_entity(self, entity):
        """put a qalx entity on the queue

        :param entity: entity to add to the queue
        :type entity: `pyqalx.core.entity.QalxEntity`
        :return: `pyqalx.core.queue.QueueResponse`
        """
        if not type(entity) in [Item, Set, Group]:
            raise QalxQueueError("Only Item, Set and Group entities can be submitted to the queue.")
        response = self.broker_client.send_message(QueueUrl=self['info']['queue_url'],
                                                   # Unique MessageGroupId to prevent processing duplicates
                                                   MessageGroupId=str(uuid.uuid4()),
                                                   # Unique MessageDeduplicationId to allow the user
                                                   # to put the same entity on the queue multiple times
                                                   MessageDeduplicationId=str(uuid.uuid4()),
                                                   MessageBody=self._stringify(
                                                       {"entity_type": entity.entity_type,
                                                        "entity_guid": entity['guid']
                                                        }))
        return QueueResponse(response)
