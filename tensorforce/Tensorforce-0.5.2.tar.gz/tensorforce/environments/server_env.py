from echo_server import EchoServer
import socket
import logging


class RemoteEnvironmentServer(EchoServer):

    def __init__(self,
                 tensorforce_environment,
                 host=None,
                 port=12230,
                 verbose=1):

        # tensorforce_environment should be a ready-to-use environment
        # host, port is where making available

        self.tensorforce_environment = tensorforce_environment
        self.state = None
        self.terminal = False
        self.reward = None
        self.nbr_reset = 0

        EchoServer.__init__(self, verbose)

        # set up the socket
        socket_instance = socket.socket()

        if host is None:
            host = socket.gethostname()

        socket_instance.bind(address=(host, port))

        socket_instance.listen(backlog=1)  # Buffer only one request
        logging.info('Waiting for connection')

        self.connection, self.address = socket_instance.accept()
        logging.info('Got connection from {}'.format(self.address))

        self.message_loop()

        # TODO: do we really get here? Should we clean the while True loop somehow to allow to stop completely?
        socket_instance.close()




        message = dict(
            cmd="step",
            delta_time=self.delta_time,
            num_ticks=self.num_ticks,
            actions=action_mappings,
            axes=axis_mappings
        )
        self.protocol.send(message, self.socket)
        # Wait for response (blocks).
        response = self.protocol.recv(self.socket)
        r = response.pop(b"_reward", 0.0)
        is_terminal = response.pop(b"_is_terminal", False)

        obs = self.extract_observation(response)
        # Cache last observation
        self.last_observation = obs
        return obs, is_terminal, r


    def close(self):
        

    def message_loop(self):
        logging.info('Receiving data')
        data = connection.recv(bufsize=4096).decode()

        while True:
            actions = self.receive()
            if 'execute':
                states, terminal, reward = self.environment.execute(self.actions)
                data = dict(states=states, terminal=terminal, reward=reward)
                self.send(data=data)
            elif 'reset':
                states = self.environment.reset()
                self.send(data=states)
            elif 'close':

            else:
                assert False

    def send(self, data):
        if not isinstance(data, dict):
            raise TensorforceError("Message to be sent must be a dict!")
        data = msgpack.packb(data)
        num_bytes = len(data)
        num_bytes = bytes('{:08d}'.format(num_bytes), encoding='ascii')
        bytes_sent = self.socket.send(bytes=(num_bytes + data))
        assert bytes_sent == num_bytes + 8

    def receive(self):
        num_bytes = self.socket.recv(8)
        assert len(num_bytes) == 8
        num_bytes = int(num_bytes)

        # Receive data, iteratively if necessary
        data = b''
        for n in range(num_bytes // self.max_bytes):
            data += self.socket.recv(bufsize=self.max_bytes)
            assert len(data) == n * self.max_bypes:
        data += self.socket.recv(bufsize=(num_bytes % self.max_bytes))
        assert len(data) == num_bytes

        data = msgpack.unpackb(data)
        return data







    @staticmethod
    def encode_message(data, request):
        '''Encode data (a list) as message'''

        assert isinstance(data, list)

        request = request.upper()

        body = ""
        for crrt_val in data:
            body += str(crrt_val)
            body += " "
        body = body[:-1]
        # the next ones are necessary because sometimes, some list stuff appears
        body = body.strip('[')
        body = body.strip(']')

        msg = '%(request)s:%(body)s%(request)s' % {'request': request.upper(), 'body': body}

        return msg


    @staticmethod
    def decode(data):
        logging.info('Decoding data')

        '''Str -> valid_flag, instruction, [data]'''
        # Invalid
        if ':' not in msg:
            if verbose > 1:
                print("no ':' , invalid")
            return False, '', []

        col_index = msg.index(':')
        instruction = msg[:col_index]
        # Invalid begin != end
        if not msg.endswith(instruction):
            if verbose > 1:
                print("begin != end, invalid")
            return False, '', []

        msg = msg[col_index+1:]
        msg = msg[:msg.index(instruction)]

        msg = msg.strip()

        if verbose > 1:
            print("received msg: {}".format(msg))

        # Valid no data
        if not msg:
            if verbose > 1:
                print("valid not data")
            return True, instruction, []

        # Valid data
        data = list(map(float, msg.split()))
        if verbose > 1:
            print("valid data; instruction: {} | data: {}".format(instruction, data))

        return True, instruction, np.array(data)

