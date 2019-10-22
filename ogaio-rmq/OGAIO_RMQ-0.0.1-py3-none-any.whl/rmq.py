import asyncio
import json

import aio_pika

from aiorpc.utils import get_logger

logger = get_logger()


class OGAIO_RMQ:
    def __init__(
        self,
        rmq_url='amqp://guest:guest@127.0.0.1/',
        request_queue='request_queue',
        response_queue='response_queue',
        loop=None,
    ):
        self.rpc_methods = {}
        self.loop = loop if loop else asyncio.get_event_loop()
        self.rmq_url = rmq_url
        self.response_queue = response_queue
        self.request_queue = request_queue
        self.loop.run_until_complete(self.init_rmq())
        logger.info('Initialization complete')

    def RPC(self, func):
        self.rpc_methods[func.__name__] = func
        return func

    async def init_rmq(self):
        connection = await aio_pika.connect(loop=self.loop, url=self.rmq_url)
        channel = await connection.channel()
        queue = await channel.declare_queue(self.request_queue)
        self.connection = connection
        self.exchange = channel.default_exchange
        await queue.consume(self.listener)

    async def send(self, body, queue):
        await self.exchange.publish(
            aio_pika.Message(body=json.dumps(body).encode()), routing_key=queue
        )

    async def listener(self, message):
        async with message.process():
            response_body = {'jsonrpc': '2.0'}
            try:
                body = json.loads(message.body.decode())
            except json.decoder.JSONDecodeError:
                error_msg = f'message {message.body.decode()} is not json'
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32700}},
                    },
                    self.response_queue,
                )
                return

            jsonrpc_id = body.get('id')
            if not jsonrpc_id:
                error_msg = f'message {body} don\'t have "id" field'
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32600}},
                    },
                    self.response_queue,
                )
                return

            response_body['id'] = jsonrpc_id

            method_name = body.get('method')
            if not method_name:
                error_msg = f'message {body} don\'t have "method" field'
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32600}},
                    },
                    self.response_queue,
                )
                return

            if body.get('jsonrpc') != '2.0':
                error_msg = (
                    f'message {body} "jsonrpc" field \'2.0\' was expected'
                )
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32600}},
                    },
                    self.response_queue,
                )
                return

            # call rpc method with params
            method = self.rpc_methods.get(method_name)
            if not method:
                error_msg = f'message {body} method not provided'
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32601}},
                    },
                    self.response_queue,
                )
                return

            params = body.get('params')
            try:
                if isinstance(params, list):
                    response = await method(*params)
                elif isinstance(params, dict):
                    response = await method(**params)
                else:
                    response = await method()
            except Exception as e:
                error_msg = f'message {body} raise exception {e}'
                logger.error(error_msg)
                await self.send(
                    {
                        **response_body,
                        **{'error': {'message': error_msg, 'code': -32603}},
                    },
                    self.response_queue,
                )
                return

            # building response json
            if response.get('result'):
                response_body['result'] = response['result']
            elif response.get('error'):
                response_body['error'] = response['error']
            else:
                error_msg = f'message {body} RPC method return nothing'
                logger.error(error_msg)
                await self.send(
                    {**response_body, **{'error': error_msg}},
                    self.response_queue,
                )
                return

            await self.send(response_body, self.response_queue)
