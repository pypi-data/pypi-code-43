import os
import socket
import threading
import logging
import easilyb.json_serialize as json

logger = logging.getLogger(__name__)
BUFFER_SIZE = 4096
MAX_OBJECT_SIZE = 1024 * 1024 * 1024  # 1GB
DEFAULT_MAX_TRIES = 5


class JsonSocket(object):
    def __init__(self, sock, max_tries=DEFAULT_MAX_TRIES):
        self.sock = sock
        self.max_tries = max_tries

    def _send(self, data):
        tries = 0
        while tries < self.max_tries:
            # Print('sending... ', end='')
            self.sock.sendall(data.encode())
            # Print('sent: ', data)
            # Print('receiving... ', end='')
            ret = self.sock.recv(1).decode()
            # Print('received : ' + ret)
            if ret == 'k':
                return
            elif ret == 'r':
                pass
            else:
                raise IOError('Excpected k or r from peer')
            tries += 1

    def _send_fragmented(self, obj_ser, size):
        tries = 0
        fragement_size = BUFFER_SIZE - 2
        while tries < self.max_tries:
            self._send('s' + str(size) + '\\')  # send size s555\
            # print 's' + str(size) + '\\'
            i = 0
            while i < size:
                self._send('c' + obj_ser[i:i + fragement_size] + '\\')
                # print 'c' + str(len(obj_ser[i:i + fragement_size])) + '\\'
                i += fragement_size
            # Print('sending... ', end='')
            self.sock.sendall(b'F\\')
            # Print('sent F\\')
            # print 'F\\'
            # Print('receiving... ', end='')
            ret = self.sock.recv(1).decode()
            # Print('received : ' + ret)
            if ret == 'K':
                return
            elif ret == 'R':
                pass
            else:
                raise IOError('Excpected K or R from peer')
            tries += 1

    def send(self, obj):
        # logger.debug("sending obj: %s", obj)
        obj_ser = json.dumps(obj)
        size = len(obj_ser)
        tries = 0
        if size > MAX_OBJECT_SIZE:
            raise ValueError("Can't send all this data!")
        try:
            if size < BUFFER_SIZE - 2:
                self._send('1' + obj_ser + '\\')
            else:
                self._send_fragmented(obj_ser, size)
        except Exception:
            # if tries > self.max_tries or not self.reconnect():
            if tries > self.max_tries:  #or not self.reconnect():
                raise
            else:
                tries += 1

    def receive(self):
        state = 0
        data = ''
        size = 0
        obj_ser = ''
        obj = None
        state2_tries = 0
        state8_tries = 0
        state12_tries = 0
        while True:
            if state == 0:
                # Print('receiving... ', end='')
                data = self.sock.recv(BUFFER_SIZE).decode()
                # Print('received : ' + data)
                if data.endswith('\\'):
                    state = 1
                else:
                    state = 2
            elif state == 1:
                if data.startswith('1'):
                    state = 3
                elif data.startswith('s'):
                    state = 4
                else:
                    state = 2
            elif state == 2:
                if state2_tries < self.max_tries:
                    state2_tries += 1
                    # Print('sending... ', end='')
                    self.sock.sendall(b'r')
                    # Print('sent k')

                    state = 0
                else:
                    raise IOError("Data malformated!")
            elif state == 3:
                obj_ser = data[1:-1]
                try:
                    obj = json.loads(obj_ser)
                    state = 5
                except:
                    state = 2
            elif state == 4:
                size = int(data[1:-1])
                obj_ser = ''
                # print 'received: s%d//' % (size)
                # Print('sending... ', end='')
                self.sock.sendall(b'k')
                # Print('sent k')
                state = 6
            elif state == 5:
                # Print('sending... ', end='')
                self.sock.sendall(b'k')
                # Print('sent k')
                # logger.debug('received obj: %s', obj)
                return obj
            elif state == 6:
                # Print('receiving... ', end='')
                data = self.sock.recv(BUFFER_SIZE).decode()
                # Print('received : ' + data)
                if data.endswith('\\'):
                    state = 7
                else:
                    state = 8
            elif state == 7:
                if data.startswith('c'):
                    # print 'received: c + %d'%(len(data)-2)
                    state = 9
                elif data.startswith('F'):
                    # print 'received: F'
                    state = 10
                else:
                    state = 8
            elif state == 8:
                if state8_tries < self.max_tries:
                    state8_tries += 1
                    # Print('sending... ', end='')
                    self.sock.sendall(b'r')
                    # Print('sent r')
                    state = 6
                else:
                    raise IOError("Data malformated!")
            elif state == 9:
                obj_ser += data[1:-1]
                # Print('sending... ', end='')
                self.sock.sendall(b'k')
                # Print('sent k')
                state = 6
            elif state == 10:
                if size == len(obj_ser):
                    try:
                        obj = json.loads(obj_ser)
                        state = 11
                    except:
                        state = 12
                else:
                    state = 12
            elif state == 11:
                # Print('sending... ', end='')
                self.sock.sendall(b'K')
                # Print('sent K')
                # logger.debug('received obj: %s', obj)
                return obj
            elif state == 12:
                if state12_tries < self.max_tries:
                    state12_tries += 1
                    # Print('sending... ', end='')
                    self.sock.sendall(b'R')
                    # Print('sent R')
                    state = 0
                else:
                    raise IOError("Data malformated!")

    def reconnect(self):
        # logger.debug("reconnecting...")
        return False

    def close(self):
        try:
            self.sock.close()
        except:
            pass
        finally:
            self.sock = None


class JsonServerSocket(JsonSocket):
    def __init__(self, server_address, callback):
        self.server_address = server_address
        self.callback = callback
        super(JsonServerSocket, self).__init__(None)  # does not work
        # super(JsonServerSocket, self).__init__(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM))  # does not work
        # super call:
        # self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # self.max_tries = DEFAULT_MAX_TRIES
        # end super call

    def bind(self):
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        logger.info("binded to %s" % self.server_address)
        self.sock.listen(1)

    def accept(self):
        connection, client_address = self.sock.accept()
        logger.info("accepted connection from: %s", client_address)
        return JsonConnection(connection, self.callback), client_address

    def reconnect(self):
        logger.debug("reconnecting...")
        try:
            self.close()
        except:
            pass
        try:
            self.bind()
            return True
        except:
            return False

    def close(self):
        try:
            os.unlink(self.server_address)
        except:
            pass
        super(self, JsonServerSocket).close()


class JsonConnection(JsonSocket):
    def __init__(self, connection, callback):
        self.callback = callback
        super(JsonConnection, self).__init__(connection)  # does not work

    def receive_call(self):
        request = self.receive()
        logger.debug("received request: %s", request)
        if 'quit' in request:
            self.close()
            return False
        function, args, kwargs = request['func'], request['args'], request['kwargs']
        try:
            ret = self.callback(function, args, kwargs)
            response = {'return': ret}
            logger.debug("sending response: %s", response)
            self.send(response)
            return True
        except Exception as e:
            response = {'exception': {"name": str(e.__class__), "msg": str(e)}}
            logger.debug("sending response: %s", response)
            self.send(response)
            return True


class JsonClientSocket(JsonSocket):
    def __init__(self, server_address):
        self.server_address = server_address
        super(JsonClientSocket, self).__init__(None)  # # does not work
        # super(JsonClientSocket, self).__init__(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM))  # # does not work
        # self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def connect(self):
        # logger.debug("connecting to: %s", self.server_address)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)
        logger.debug("connected to: %s", self.server_address)

    def call_function(self, function, args=None, kwargs=None):
        request = {'func': function, 'args': args or list(), 'kwargs':kwargs or dict()}
        self.send(request)
        response = self.receive()
        logger.debug("received response: %s", response)
        # TODO: receive logs
        if 'exception' in response:
            _raise_exception(response['exception'])
        if 'return' in response:
            return response['return']

    def quit(self):
        request = {'quit': ''}
        self.send(request)
        self.close()

    def reconnect(self):
        logger.debug("reconnecting...")
        try:
            self.quit()
        except:
            pass
        try:
            self.connect()
            return True
        except:
            return False


class JsonServerMaster(threading.Thread):
    def __init__(self, server_address, threaded=False):
        self.server_address = server_address
        self.threaded = threaded
        self.server = JsonServerSocket(server_address, self.callback)
        self.up = True
        self.ipc_functions = dict()
        super().__init__()

    def ipc_function(self, f):
        self.ipc_functions[f.__name__] = f
        return f

    def callback(self, func, args, kwargs):
        try:
            func_call  = self.ipc_functions[func]
            return func_call(*args, **kwargs)
        except:
            logger.error("Error calling function", exc_info=True)
            raise

    def run(self):
        self.server.bind()
        try:
            while self.up:
                try:
                    connection, client_address = self.server.accept()
                    if self.up:
                        self._process_connection(connection, client_address)
                    else:
                        connection.close()
                except KeyboardInterrupt:
                        raise
                except Exception as e:
                    logger.error("Error in control server: %s", e, exc_info=True)
        finally:
            try:
                self.server.close()
            except:
                pass

    def _process_connection(self, connection, client_address):
        if self.threaded:
            t = threading.Thread(target=self._process_connection_run, args=(connection, client_address))
            t.setDaemon(True)
            t.start()
        else:
            self._process_connection_run(connection, client_address)

    def _process_connection_run(self, connection, client_address):
        try:
            while connection.receive_call():
                pass
        except KeyboardInterrupt:
            self.stop()
        except:
            logger.error("Error in connection", exc_info=True)
        finally:
            try:
                connection.close()
            except:
                pass

    def stop(self):
        if self.up:
            self.up =  False
            # os.kill(os.getpid(), signal.SIGINT)
            try:
                client = JsonClientSocket(self.server_address)
                client.connect()
                # client.quit()
            except:
                pass


class JsonServerProxy:
    def __init__(self, server_address):
        self.client = JsonClientSocket(server_address)
        self.client.connect()

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except:
            return self.get_func(item)

    def get_func(self, func):
        def _call_func(*args, **kwargs):
            return self.client.call_function(func, args, kwargs)
        return _call_func

    def quit(self):
        self.client.quit()


def _raise_exception(exception_object):
    exception_name, exception_msg = exception_object['name'], exception_object['msg']
    if exception_name == 'ValueError':
        raise ValueError(exception_msg)
    elif exception_name == 'KeyError':
        raise KeyError(exception_msg)
    else:
        raise Exception(exception_name + ": " + exception_msg)
