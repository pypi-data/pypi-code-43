import logging
import time
import asyncio
from .base import MUDObject
from .base import MUDInterface
from .servers.telnet import TelnetServer
from .engine import Engine

class Game(MUDObject):

    name = "MUDEngine"

    server_factory = TelnetServer
    engine_factory = Engine

    shutdown_counter = None

    _instance = None

    def __init__(self, host=None, port=None):

        self.port = port
        self.host = host
        self.server = self.server_factory(host, port)
        self.engine = self.engine_factory()
        self.admins = []  # A list of names to make admins
        self.players = []
        self.geography = []
        self.channels = {}
        self.interface = MUDInterface()
        MUDInterface.game = self

        logging.info("Loading geography data")
        self.interface.geography.load_geography()

        logging.info("Loading communication channels")
        self.channels = self.interface.channel.load_channels()

        Game._instance = self

    async def run(self):

        logging.info(f"Game {self.name} starting up")

        return await asyncio.gather(
            self.engine.run(),
            self.server.run()
        )

    def get_connected_players(self):
        return [v for v in self.players if v.connected]


    @classmethod
    def add_player(self, player):

        # This is a bit hackish, act like a instance method when the engine has been instantiated
        # otherwise it's a class method. Need to be able to add NPCs before and after instantiation

        if self._instance:
            self = self._instance

        from .npc import NPC

        if isinstance(player, NPC):
            self.players.append(player)
        else:
            if player.name not in [v.name for v in self.players]:
                self.players.append(player)
            else:
                logging.debug(f"Attempted to add player {player} that is already in the engine")


    def disconnect_player(self, player):

        logging.info("Disconnecting player {}".format(player))
        player.connected = False
        if player.location:
            player.location.players.remove(player)
            for channel in player.channels:
                channel.players.remove(player)
        player._deregister_heartbeat()
        player.client.disconnect()
        del player.client
        import gc
        gc.collect()

    def connect_player(self, player):

        logging.info("Logging in player {}".format(player))

        player.connected = True

        if player.name.lower() in self.admins:
            logging.info("Admin logging in {}".format(player.name))
            player.admin = True

        self.add_player(player)

        if not player.location:
            player.set_location(self.geography[0])
        else:
            player.set_location(player.location)

        player.queue_message(f"Welcome to {self.name}, {player.name}", prompt=False)

        self.interface.channel.add_player_to_valid_channels(player)

        player.location.render_to_player(player)

    def shutdown(self):
        self.server.shutdown()

