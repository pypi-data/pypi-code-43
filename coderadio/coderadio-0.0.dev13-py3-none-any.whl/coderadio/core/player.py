import time

from threading import Event
from threading import Thread

import vlc

from notify import Notification

from coderadio.core.log import logger
from coderadio.core.classes import Station
from coderadio.core.utils import load_plugin
from coderadio.core.exchange import play_now
from coderadio.core.exchange import display_now


class RunPlugin(Thread):
    def __init__(self, func):
        super().__init__()
        self.daemon = True
        self.func = func
        self._stop = Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):

        while not self.stopped():
            try:
                resp = self.func()
                service = resp[0]
                artist = resp[1]
                title = resp[2]
                Notification(
                    f"Artist: {artist}\nTitle: {title}",
                    title=service,
                    app_name="coderadio",
                )
                display_now.put(
                    f"\nService: {service}\n\nPlaying now: {artist} - {title}\n"
                )
            except Exception as exc:
                logger.debug("*" * 80)
                logger.debug(exc)
            time.sleep(60 * 2)


class Vlc:
    instance = vlc.Instance("--verbose -1")
    player = instance.media_player_new()


class Play(Vlc):
    def __init__(self, station):
        self.station = station

    def __call__(self):
        media = self.instance.media_new(self.station.url)
        self.player.set_media(media)
        self.player.play()


class Stop(Vlc):
    def __call__(self):
        self.player.stop()


class Radio(Thread):

    plugins = []
    plug = None

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.start()

    def run_plugin(self):
        p = RunPlugin(self.plug.run)
        p.start()
        self.plugins.append(p)

    def kill_plugin(self):
        try:
            self.plugins[0].stop()
            self.plugins.pop()
        except IndexError as exc:
            logger.debug(exc)

    def run(self):

        while True:
            obj = play_now.get()  # block!!

            if isinstance(obj, Stop):
                self.kill_plugin()
                obj()  # stop playing
            if isinstance(obj, Station):
                self.plug = load_plugin("plugins." + obj.plugin_name())
                self.kill_plugin()
                if self.plug:
                    self.run_plugin()
                Play(obj)()


radio = Radio()
