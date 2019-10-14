from __future__ import print_function
import numpy as np


class EchoServer(object):
    '''Implement a simple echo server for sending data through a socket.
    Every request from client to server is followed by await of message
    The format of the message is REQUEST: bodyREQUEST. empty body or
    body is formed by space separated numbers
    '''

    def __init__(self, verbose=0):

        # the commands that are supported; should correspond to methods
        # in the RemoteEnvironmentServer class. Those commands can be
        # used by the RemoteEnvironmentClient.

        self.supported_instructions = (
            # Put the simulation to the state from which learning begins.
            # If successfull RESET: 1RESET, fail empty
            'RESET',
            # Respond with the state of Simulation (some vector in state space)
            'STATE',
            # CONTROL: valuesCONTROL, success CONTROL: 1CONTROL, fail empty
            'CONTROL',
            # Evolve using the set control, success EVOLVE: 1EVOLVE, fail empty
            'EVOLVE',
            # Response to reward, sucess REWARD: valueREWARD, fail empty
            'REWARD',
            # Is the solver done? value 0 1, empty fail
            'TERMINAL',
            )

        self.verbose = verbose

    @staticmethod
    def decode_message(msg, verbose=1):
        if verbose > 1:
            print("start decode_message: {}".format(msg))

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

    def handle_message(self, msg):
        '''Trigger action base on client message.'''

        is_valid, instruction, data = EchoServer.decode_message(msg, verbose=self.verbose)

        # Conform to standard?
        if not is_valid:
            print("START DUMP")
            print("msg:")
            print(msg)
            RuntimeError("not valid; the message is not conform to the standard")
            return EchoServer.encode_message([], instruction)

        # No support?
        if instruction not in self.supported_instructions:
            print("START DUMP")
            print("msg:")
            print(msg)
            RuntimeError("unknown command; no support for the command")
            return EchoServer.encode_message([], instruction)

        # Dispatch to action which returns the data. This is what
        # children need to implement
        # so this calls the method of the EchoSolver (or the class derived from it)
        # such as RemoteEnvironmentServer
        result = getattr(self, instruction)(data)

        # Wrap
        return EchoServer.encode_message(result, instruction)
