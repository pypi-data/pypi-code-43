from ehelply_bootstrapper.drivers.driver import Driver
from socketio import AsyncServer, ASGIApp

from ehelply_bootstrapper.utils.connection_details import ConnectionDetails


class Socketio(Driver):
    def __init__(self, connection_details: ConnectionDetails = None, dev_mode: bool = False, verbose: bool = False):
        super().__init__(connection_details, dev_mode, verbose)
        self.socket_app = None

    def setup(self):
        self.instance = AsyncServer(async_mode='asgi', logger=True)
        self.socket_app = ASGIApp(self.instance, socketio_path='server')
