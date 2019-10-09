import asyncio
import threading
import sys
import functools
import time
import struct
import queue
import ssl

# This class is annoyingly complicated, but I'll explain.
#
# The "do_X" functions do the work asked for by the X
# functions. Calling them must happen from INSIDE the core's event
# loop. So a task to call them 'soon' is posted to the loop.
#
# Reading pulls LENGTH-prefixed protobufs off the comms reader and
# sends them to the message-handler's 

class Connection(object):

    INIT = 0
    CONNECTING = 1
    CONNECTED = 2
    CLOSING = 3
    CLOSED = 4

    def __init__(self, core, name=None, logger=None):
        self.reader = None
        self.writer = None
        self.core = core
        self.logger = logger or core.logger
        self.core.register_connection(self)
        self.url = None
        self.outq = None
        self.message_handler = None
        self.send_loop = None
        self.recv_loop = None
        self.name = name or id(self)
        self.state = Connection.INIT

    def new_message_handler_type(self, message_handler_type, **kwargs):
        self.message_handler = message_handler_type(**kwargs)

    def set_message_handler(self, message_handler):
        self.message_handler = message_handler

    def connect(self, **kwargs):
        if self.url and self.url == kwargs.get('url', None):
            return
        self.core.call_soon_async(self.do_connect, **kwargs)

    def send(self, data):
        self.core.call_soon_async(self.do_send, data)

    def close(self):
        if self.state not in [ Connection.CONNECTING, Connection.CONNECTED ]:
            return
        else:
            self.state = Connection.CLOSING
            self.core.deregister_connection(self)
        self.core.call_soon_async(self.do_stop)

    def stop(self):
        self.close()
        self.wait_until_closed()

    def wait_until_closed(self):
        while self.state != Connection.CLOSED:
            time.sleep(0.3)

    def is_connected(self):
        return self.state == Connection.CONNECTED

# Internal workings.

    async def do_send(self, data):
        if self.outq != None:
            await self.outq.put(data)

    async def do_stop(self):
        self.reader = None
        w = self.writer
        self.writer = None
        if w:
            w.close();
            try:
                await w.wait_closed()
            except:
                pass
        if self.outq != None:
            await self.outq.put(None)
        if self.send_loop:
            self.send_loop.cancel()
        if self.recv_loop:
            self.recv_loop.cancel()

        while self.recv_loop != None and self.send_loop != None:
            if self.recv_loop != None and self.recv_loop.cancelled():
                self.recv_loop  = None
            if self.send_loop != None and self.send_loop.cancelled():
                self.send_loop  = None
            await asyncio.sleep(.3)
        self.state = Connection.CLOSED

    async def do_with_kwargs(self, function, kwargs):
        return await function(**kwargs)

    async def do_connect(self, url=None, **kwargs):
        self.state = Connection.CONNECTING
        if self.reader:
            self.reader = None
        if self.writer:
            self.writer.close()
            self.writer= None

        try:
            from oef.agents import OefConnectionHandler
            from oef.agents import OefLoginHandler

            self.message_handler = OefConnectionHandler(
                url=url,
                **kwargs)
            self.url = url
            self.addr, _, self.port = self.url.partition(':')
            self.port = int(self.port)
            x = await asyncio.open_connection(self.addr, self.port)
            self.outq = asyncio.Queue(maxsize=0)
            self.message_handler = OefLoginHandler(self, url=url, **kwargs)
            self.reader, self.writer = x
            try:
                self.send_loop = self.core.call_soon_async(self.do_send_loop)
                self.recv_loop = self.core.call_soon_async(self.do_recv_loop)
            except Exception as ex:
                self.logger("Connection.do_connect[{}]: exception".format(id(self)), ex)
            self.state = Connection.CONNECTED
        except Exception as ex:
            self.message_handler.handle_failure(ex, self)
        print("do connected finished")

    async def do_send_loop(self):
        sendable = await self.outq.get()
        if sendable == None:
            return
        if not self.writer:
            return
        self.outq.task_done()
        await self._transmit(sendable)
        if not self.writer or not sendable:
            self.core.call_soon_async(self.do_stopped)
            return
        self.core.call_soon_async(self.do_send_loop)

    def _message_arrived(self, data):
       self.message_handler.incoming(data, self.name, self)

    async def do_stopped(self):
        self.message_handler.handle_disconnection(self)

    async def do_recv_loop(self):
        data = None
        try:
            data = await self._receive()
            if data == None:
                self.core.call_soon_async(self.do_stopped)
                return
            self._message_arrived(data)
            self.core.call_soon_async(self.do_recv_loop)
        except EOFError:
            self.core.call_soon_async(self.do_stopped)

    async def _transmit(self, body):
        nbytes = len(body)
        header = struct.pack("I", nbytes)
        msg = header + body
        w = self.writer
        if w:
            w.write(msg)
            await w.drain()

    async def _receive(self):
        try:
            nbytes_packed = await self.reader.read(len(struct.pack("I", 0)))
        except:
            raise EOFError()
        if len(nbytes_packed) == 0:
            raise EOFError()
        nbytes = struct.unpack("I", nbytes_packed)[0]
        data = b""
        while self.reader and len(data) < nbytes:
            r = self.reader
            if r:
                input_bytes = await r.read(nbytes - len(data))
                if not self.reader:
                    raise EOFError()
            if len(input_bytes) == 0:
                raise EOFError()
            data += input_bytes
        return data

class SecureConnection(Connection):
    def __init__(self, prv_key_file, core, name=None, logger=None):
      super().__init__(core, name, logger)
      self.private_key_file = prv_key_file

    async def do_connect(self, url=None, **kwargs):
        self.state = Connection.CONNECTING
        if self.reader:
            self.reader = None
        if self.writer:
            self.writer.close()
            self.writer= None

        try:
            self.message_handler = OefConnectionHandler(
                url=url,
                **kwargs)
            self.url = url
            self.addr, _, self.port = self.url.partition(':')
            self.port = int(self.port)
            # setup ssl
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT);
            ssl_ctx.options |= ssl.OP_NO_TLSv1
            ssl_ctx.options |= ssl.OP_NO_TLSv1_1
            ssl_ctx.load_cert_chain(self.private_key_file, keyfile=self.private_key_file)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.VerifyMode.CERT_NONE
            ssl_ctx.set_ciphers('DHE-RSA-AES256-SHA256')
            x = await asyncio.open_connection(self.addr, self.port, ssl=ssl_ctx)
            self.outq = asyncio.Queue(maxsize=0)
            self.message_handler = OefLoginHandler(self, url=url, **kwargs)
            self.reader, self.writer = x
            try:
                self.send_loop = self.core.call_soon_async(self.do_send_loop)
                self.recv_loop = self.core.call_soon_async(self.do_recv_loop)
            except Exception as ex:
                self.logger("Connection.do_connect[{}]: exception".format(id(self)), ex)
            self.state = Connection.CONNECTED
        except Exception as ex:
            self.message_handler.handle_failure(ex, self)



class AsyncioCore(object):

# If you want to use this in an ASYNCIO world, pass a suitable loop into the constructor
    def __init__(self, loop = None, logger=None):
        self.loop = loop
        self.logger = logger or print
        self.done = None
        if loop:
            self.done = loop.create_future()

        self.connections = set()
        self.url_to_connections = {}

# This is the interface for use in THREADED applications. Call
# run_threaded() to start the app's networking and then stop() when
# you're done.

    def run_threaded(self):
        def execute(core):
            core.loop = asyncio.new_event_loop()
            core.loop.run_forever()

        self.thread = threading.Thread(target=execute, args=(self,) )
        self.thread.start()
        while self.loop == None:
            time.sleep(0.1)

    def data(self):
        print(asyncio.all_tasks())

    def stop(self):
        if self.loop == None and self.done:
            return

        conns = self.connections
        self.connections = set()
        for conn in conns:
            conn.stop()
        for attempt in range(0,10):
            if self.loop == None or len(asyncio.all_tasks(self.loop)) == 0:
                break
            time.sleep(0.3)

        if self.done:
            self.done.set_result(True)
            self.done = None
        elif self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.thread = None
            self.loop = None

# If you want to use this in an ASYNCIO world, pass a suitable loop
# into the constructor and this function will give you a waitable
# which will complete when stop() has been called.

    def get_awaitable(self):
        return asyncio.gather(self.done)

# functions for scheduling work onto our loop. Note that the loop runs
# the networking and hence long-running tasks posted to it will block
# the network from running until they complete.

    def call_soon_async(self, func, *args, **kwargs):
        def taskify(func, args, kwargs):
            asyncio.create_task(func(*args, **kwargs))
        return self.loop.call_soon_threadsafe(taskify,func, args, kwargs)

    def call_soon(self, func, *args):
        if self.loop:
            return self.loop.call_soon_threadsafe(func, *args)
        else:
            raise ValueError("Start my loop first!")

    def call_later(self, seconds, func, *args):
        if self.loop:
            return self.loop.call_later(seconds, func, *args)
        else:
            raise ValueError("Start my loop first!")

    def call_soon(self, func, *args):
        if self.loop:
            return self.loop.call_soon_threadsafe(func, *args)
        else:
            raise ValueError("Start my loop first!")

# functions used by Connection objects.

    def register_connection(self, connection):
        self.connections.add(connection)

    def deregister_connection(self, connection):
        self.connections.discard(connection)
