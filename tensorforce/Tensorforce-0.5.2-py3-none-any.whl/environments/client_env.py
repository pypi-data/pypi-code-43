from threading import Thread
from tensorforce import TensorforceError
from tensorforce.environments import Environment
import socket
from echo_server import EchoServer
import logging


class RemoteEnvironmentClient(Environment):
    """Used to communicate with a RemoteEnvironmentServer. The idea is that the pair
    (RemoteEnvironmentClient, RemoteEnvironmentServer) allows to transmit information
    through a socket seamlessly.
    The RemoteEnvironmentClient can be directly given to the Runner.
    The RemoteEnvironmentServer herits from a valid Environment add adds the socketing.
    """

    def __init__(self, example_environment,
                 port=12230,
                 host=None,
                 ):
        super().__init__()


        # make arguments available to the class
        # socket
        self.port = port
        if host is None:
            self.host = socket.gethostname()
        else:
            self.host = host
        # states and actions
        self.example_environment = example_environment

        self.socket = socket.socket()
        self.socket.connect(address=(self.host, self.port))
        if self.verbose > 0:
            logging.info('Connected to {}:{}'.format(self.host, self.port))

        self.episode = 0
        self.step = 0

    def __str__(self):
        return self.__class__.__name__

    def states(self):
        # Return the state space. Might include subdicts if multiple states are 
        # available simultaneously.

        # Returns:
        #     specification: States specification, with the following attributes:
        #     - type: one of 'bool', 'int', 'float' (default: 'float').
        #     - shape: integer, or list/tuple of integers (required).
        raise NotImplementedError

    def actions(self):
        # Return the action space. Might include subdicts if multiple actions are 
        # available simultaneously.

        # Returns:
        #     specification: Actions specification, with the following attributes:
        #     - type: one of 'bool', 'int', 'float' (required).
        #     - shape: integer, or list/tuple of integers (default: []).
        #     - num_actions: integer (required if type == 'int').
        #     - min_value and max_value: float (optional if type == 'float', default: none).
        raise NotImplementedError

    def max_episode_timesteps(self):
        return None

    def close(self):
        """
        Close environment. No other method calls possible afterwards.
        """
        # TODO: think about sending a killing message to the server? Maybe not necessary - can reuse the
        # server maybe - but may be needed if want to clean after us.
        self.socket.close()

    def reset(self):
        """
        Reset environment and setup for new episode.
        Returns:
            initial state of reset environment.
        """

        # perform the reset
        _ = self.communicate_socket("RESET: RESET")

        # get the state
        _, _, init_state = self.communicate_socket("STATE: STATE")

        # Updating episode and step numbers
        self.episode += 1
        self.step = 0

        if self.verbose > 1:
            print("reset done; init_state:")
            print(init_state)

        return(init_state)

    def execute(self, actions):
        """
        Executes action, observes next state(s) and reward.
        Args:
            actions: Actions to execute.
        Returns:
            Tuple of (next state, bool indicating terminal, reward)
        """

        # build the string to send through socket
        message_actions = "CONTROL:"

        list_actions = actions.tolist()

        for crrt_component_action in list_actions:
            message_actions += " "
            message_actions += str(crrt_component_action)

        message_actions += "CONTROL"

        # send the control message
        self.communicate_socket(message_actions)

        # ask to evolve
        self.communicate_socket("EVOLVE: EVOLVE")

        # obtain the next state
        _, _, next_state = self.communicate_socket("STATE: STATE")

        # check if terminal
        _, _, terminal = self.communicate_socket("TERMINAL: TERMINAL")

        # because we send a value rather than a true bool need an ugly cast...
        # TODO: clean somehow?
        terminal = terminal[0] > 0.5

        # get the reward
        _, _, reward = self.communicate_socket("REWARD: REWARD")

        # now we have done one more step
        self.step += 1

        if self.verbose > 1:
            print("execute performed; state, terminal, reward:")
            print(next_state)
            print(terminal)
            print(reward)

        return (next_state, terminal, reward)

    def communicate_socket(self, request):
        """Send a request through the socket, and wait for the answer message.
        """

        self.socket.send(request.encode())

        if self.verbose > 1:
            print("send request: {}".format(request))

        # TODO: the recv argument gives the max size of the buffer, can be a source of missouts if
        # a message is larger than this; add some checks to verify that no overflow
        received_msg = self.socket.recv(4096).decode()

        if self.verbose > 1:
            print("received message: {}".format(received_msg))

        is_valid, instruction, data = EchoServer.decode_message(received_msg, verbose=self.verbose)

        if not is_valid:
            print("DUMP FOR CHECK")
            print("REQUEST:")
            print(request)
            print("RECEIVED MSG:")
            print(received_msg)
            print("source of errors here: wrong message, crashing server, buffer overflow in recv / send")
            raise RuntimeError("Received non valid answer!")

        return(is_valid, instruction, data)
