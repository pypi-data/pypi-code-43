from ..base import MUDObject
from ..base import MUDInterface

class ServerInterface(MUDInterface):

    name = 'server'

class MUDServer(MUDObject):

    def __init__(self):
        self.interface = MUDInterface.get_interface('server')()

class MUDMessageBus(MUDObject):

    def __init__(self):
        pass


class MUDClientConnection:

    buff = ""
    connection_id = None

    def parse_message(self, message: str):
        pass

    def get_incoming_message(self):
        pass

    def send_message(self, message):
        pass

    def establish_connection(self, *args, **kwargs):
        pass

    def teardown_connection(self, *args, **kwargs):
        pass

    def disconnect(self, *args, **kwargs):
        return self.teardown_connection(*args, **kwargs)
