import time
from threading import Event
from threading import Thread

import vlc
from notify import Notification
from pyradios import RadioBrowser


from coderadio.exchange import display_now
from coderadio.log import logger
from coderadio.classes import Station
from coderadio.classes import StationList


class RunPlugin(Thread):
    def __init__(self, func):
        super().__init__()
        self.daemon = True
        self._stop = Event()
        self.func = func

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
                logger.info(exc)
            time.sleep(60 * 2)


class Player:
    def __init__(self):
        self._instance = vlc.Instance("--verbose -1")
        self._player = self._instance.media_player_new()
        self.obj = None

    def play(self, obj):
        self.obj = obj

        media = self._instance.media_new(obj.url)
        self._player.set_media(media)
        self.obj.state = ">"
        self._player.play()

    def stop(self):
        self.obj.state = " "
        self._player.stop()


class Radio:
    def __init__(self, start="bbc"):
        self._player = Player()
        self._rb = RadioBrowser()
        # TODO: Pegar do banco de dados favoritos ou buscar na web
        self._station_list = StationList(self._rb.stations_bytag(start))

        self.station = None
        self.plug = None
        self.plugins = []

    def play(self, **kwargs):

        command, term = kwargs["command"], kwargs["term"]

        data = getattr(self._rb, f"stations_{command}")(term)

        self.station = Station(**data[0])

        # display_buffer.buffer = self.station.show_info()
        display_now.put(self.station.show_info())
        self.kill_plugin()
        self.plug = self.station.path_to_plugin()

        # TODO: passsar somente a url para play
        self._player.play(self.station)

        if self.plug:
            self.run_plugin()

    def run_plugin(self):

        p = RunPlugin(self.plug.run)
        p.start()
        self.plugins.append(p)

    def kill_plugin(self):
        try:
            self.plugins[0].stop()
            self.plugins.pop()
        except Exception as exc:
            logger.info(exc)

    def playable_station(self):
        pass

    def stop(self):
        self._player.stop()
        self.kill_plugin()

    def list(self, **kwargs):

        if not kwargs:
            return self._station_list.content

        command = kwargs.get("command")
        term = kwargs.get("term")
        command = "stations_{}".format(command)
        self._station_list.data = getattr(self._rb, command)(term)
        return self._station_list.content


radio = Radio()
