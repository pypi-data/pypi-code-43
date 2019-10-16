import logging
import time
import asyncio
from .base import MUDObject
from .base import MUDInterface
from .player import HumanPlayer
from .player import ConnectingPlayer


class EngineInterface(MUDInterface):
    name = 'engine'


class Engine(MUDObject):

    pulse = 1.5 * 1000000000 # 1 beat per 1.5 seconds
    _last_heartbeat = 0 # Nanoseconds since last heartbeat
    _instance = None

    name = "Engine"
    events = []

    def __init__(self):

        self.events = []

        self.interface = MUDInterface.get_interface("engine")()

        Engine._instance = self

    async def run(self):

        logging.info(f"Engine starting up - {self.pulse / 1000000000} beats a second")

        self._last_heartbeat = time.time_ns()

        while True:

            # We're async here - need to release context for other workes to do stuff
            await asyncio.sleep(0)

            t = time.time_ns()
            if t - self._last_heartbeat > self.pulse:
                self.heartbeat()
                self._last_heartbeat = t

            self.handle_events()

            if self.interface.game.shutdown_counter is None:
                continue

            if self.interface.game.shutdown_counter == 0:
                logging.info("Shutdown command received, shutting down")
                self.interface.game.shutdown()
                return



    def heartbeat(self):

        for obj, heartbeat in [(k,v) for k,v in MUDObject._heartbeats.items()]:
            if obj != self:
                heartbeat()

        if self.interface.game.shutdown_counter is None:
            return

        from .communication import Red
        from .communication import NoColor

        self.interface.channel.get_channel_by_name("general")\
            .queue_message(f"{Red}Server shutting down in {self.interface.game.shutdown_counter} heartbeats{NoColor}", prompt=False)
        self.interface.game.shutdown_counter -= 1

    def handle_events(self):
        events = self.events
        self.events = []
        while events:
            event = events.pop(0)
            if not hasattr(event, "player") \
                    or (isinstance(event.player, HumanPlayer) and event.player.connected) \
                    or (isinstance(event.player, ConnectingPlayer) \
                        and event.player.login_state != ConnectingPlayer.LOGIN_STATE_CONNECTED):
                event.execute()
