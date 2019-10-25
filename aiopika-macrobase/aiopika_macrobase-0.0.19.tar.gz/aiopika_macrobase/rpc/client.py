import datetime
from typing import Union, Dict
import uuid
import asyncio
from asyncio import AbstractEventLoop, Future, TimeoutError

from .request import RPCMessageType, RPCRequest, RPCResponse, response_from_raw
from ..router import Router, HeaderMethodRouter
from ..serializers import serialize, deserialize, PayloadTypeNotSupportedException, SerializeFailedException,\
    DeserializeFailedException, ContentTypeNotSupportedException
from ..exceptions import AiopikaException
from .exceptions import PublishMessageException, DeliveryException, MessageTimeoutException, ExternalException,\
    ReceiveMessageException, ReplyNotSupportBroadcastException

from aio_pika import connect_robust, Connection, Channel, IncomingMessage, Message, Exchange, Queue, ExchangeType
from aio_pika.message import DeliveredMessage

from logging import getLogger
log = getLogger('AiopikaClient')


DateType = Union[int, datetime.datetime, float, datetime.timedelta, None]


class AsyncResult(object):

    #: Timeout for wait publish new message in broker
    rpc_wait_timeout = 60

    def __init__(self, client, exchange: str, queue: str, identifier: str, correlation_id: str, reply: bool = True):
        self._client = client
        self._exchange = exchange
        self._queue = queue
        self._identifier = identifier
        self._correlation_id = correlation_id
        self._reply = reply

    @property
    def exchange(self) -> str:
        return self._exchange

    @property
    def queue(self) -> str:
        return self._queue

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def correlation_id(self) -> str:
        return self._correlation_id

    @property
    def reply(self) -> bool:
        return self._reply

    async def wait(self, timeout: int = None):
        if not self.reply:
            raise ReplyNotSupportBroadcastException

        if timeout is None:
            timeout = self.rpc_wait_timeout

        return await self._client.wait_result(self, timeout=timeout)


class AiopikaClient(object):

    #: Timeout for wait declaring queue or exchange
    declaring_timeout = 30

    #: Timeout for wait publish new task in broker
    publish_timeout = 30

    #: Timeout for wait publish new task in broker
    rpc_wait_timeout = 60

    #: Limit for count retries task
    max_retries = 100

    def __init__(self, name: str = 'client', host: str = 'localhost',
                 port: int = 5672, virtual_host: str = '/',
                 exchange: str = '', user: str = None,
                 password: str = None, loop: AbstractEventLoop = None):
        self._name = name
        self._host = host
        self._virtual_host = virtual_host
        self._exchange_name = exchange
        self._port = port
        self._user = user
        self._password = password
        self._loop = loop

        self._callback_queue: Queue = None
        self._callback_queue_name = None
        self._callback_queue_consumer_tag = None

        self._connection: Connection = None
        self._channel: Channel = None
        self._exchange: Exchange = None
        self._futures: Dict[str, Future] = {}

        self.router_cls: Router = HeaderMethodRouter

    @property
    def name(self) -> str:
        return self._name

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    def replace_loop(self, loop: AbstractEventLoop):
        self._loop = loop

    @property
    def connection(self) -> Connection:
        return self._connection

    @property
    def channel(self) -> Channel:
        return self._channel

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def is_closed(self) -> bool:
        return self._connection.is_closed if self._connection is not None else True

    def get_nodename(self):
        return self._name

    async def connect(self, exchange_name: str = 'rpc', loop: AbstractEventLoop = None):
        self._loop = loop or self._loop

        await self._reset_callback_queue()

        log.info(f'Connect to {self._host}:{self._port}/{self._virtual_host} ({self._user}:******)')
        self._connection = await connect_robust(
            host=self._host,
            port=self._port,
            login=self._user,
            password=self._password,
            virtualhost=self._virtual_host,
            loop=self.loop
        )
        self._connection.loop
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            name=exchange_name,
            type=ExchangeType.TOPIC,
            durable=True,
            auto_delete=False
        )

        if self._callback_queue is None:
            await self._reset_callback_queue()
            await self._setup_callback_queue()

    async def close(self):
        # if self._callback_queue is not None:
        #     await self._callback_queue.delete()

        if self._channel is not None:
            await self._channel.close()
            self._channel = None

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def _reset_callback_queue(self):
        if self._callback_queue is not None:
            await self._callback_queue.cancel(self._callback_queue_consumer_tag, timeout=self.declaring_timeout)

        self._callback_queue_name = f'{self._name}.clients.{str(uuid.uuid4())}'

    async def _setup_callback_queue(self):
        self._callback_queue = await self.channel.declare_queue(
            name=self._callback_queue_name,
            # exclusive=True,
            auto_delete=True,
            # durable=True,
            timeout=self.declaring_timeout,
        )

        self._callback_queue_consumer_tag = await self._callback_queue.consume(self._on_response)

    async def _on_response(self, message: IncomingMessage):
        async with message.process(ignore_processed=True):
            if message.correlation_id not in self._futures:
                await message.reject(requeue=False)
                return

            future = self._futures.pop(message.correlation_id)

            try:
                response = response_from_raw(message.body, message.content_type, message.type)

                if response.type == RPCMessageType.result:
                    future.set_result(response.payload)
                elif response.type == RPCMessageType.error:
                    future.set_exception(response.payload)
            except (DeserializeFailedException, ContentTypeNotSupportedException) as e:
                future.set_exception(ReceiveMessageException(message.correlation_id, message.routing_key, message.type))

            await message.ack()

    async def _get_message(self, body, content_type: str, type: str, correlation_id: str, identifier: str,
                     reply_to: str = None, expiration: DateType = None) -> Message:
        return Message(
            body=body,
            content_type=content_type,
            type=type,

            correlation_id=correlation_id,
            reply_to=reply_to,

            expiration=expiration,

            headers={
                'lang': 'py',
                'method': identifier,
                # 'id': correlation_id,
                # 'shadow': shadow,
                # 'countdown': countdown,
                # 'eta': eta,
                # 'group': group_id,
                # 'retries': retries,
                # 'timelimit': [time_limit, soft_time_limit],
                # 'root_id': root_id,
                # 'parent_id': parent_id,
                'origin': self.get_nodename()
            }
        )

    async def _publish_message(self, message: Message, identifier: str, correlation_id: str,
                               routing_key: str) -> DeliveredMessage:
        try:
            result: DeliveredMessage = await self._exchange.publish(
                message=message,
                routing_key=routing_key,
                timeout=self.publish_timeout
            )

            # TODO: except all error codes from: https://cwiki.apache.org/confluence/display/qpid/AMQP+Error+Codes#space-menu-link-content
            if isinstance(result, DeliveredMessage):
                raise DeliveryException(result)

            return result
        except TimeoutError as e:
            raise PublishMessageException(routing_key, identifier, correlation_id)

    async def call(self, identifier: str, queue: str, payload=None, reply: bool = True,
                   expires: DateType = None, *args, **kwargs) -> AsyncResult:
        correlation_id = str(uuid.uuid4())
        body, content_type = serialize(payload)

        message = await self._get_message(
            body=body,
            content_type=content_type,
            type=RPCMessageType.call.value,
            correlation_id=correlation_id,
            identifier=identifier,
            reply_to=self._callback_queue_name if reply else None,
            expiration=expires
        )

        await self._publish_message(
            message=message,
            identifier=identifier,
            correlation_id=correlation_id,
            routing_key=queue
        )

        return AsyncResult(
            self,
            self._channel.default_exchange.name,
            queue,
            identifier,
            correlation_id,
            reply=reply
        )

    async def wait_result(self, result: AsyncResult, timeout: int = None):
        if self._callback_queue is None:
            await self._reset_callback_queue()
            await self._setup_callback_queue()

        if timeout is None:
            timeout = self.rpc_wait_timeout

        future = self.loop.create_future()
        self._futures[result.correlation_id] = future

        try:
            return await asyncio.wait_for(future, timeout=timeout, loop=self.loop)
        except TimeoutError as e:
            raise MessageTimeoutException(result.queue, result.identifier, result.correlation_id)
        except AiopikaException as e:
            raise
        except Exception as e:
            raise ExternalException(e)
