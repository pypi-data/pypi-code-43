import time
from threading import Event, Thread

from notify import Notification
from pyradios import RadioBrowser
from streamscrobbler import streamscrobbler

import vlc
from coderadio.classes import Station, StationList
from coderadio.exchange import display_now
from coderadio.log import logger


def get_metada(stream_url):
    stationinfo = streamscrobbler.get_server_info(stream_url)
    return stationinfo["metadata"]


class RunPlugin(Thread):
    def __init__(self, station):
        super().__init__()
        self.daemon = True
        self._stop = Event()
        self.func = None
        self.station = station

        if self.station.path_to_plugin():
            self.plugin = self.station.path_to_plugin()
            self.func = self.plugin.run

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):

        while not self.stopped():
            try:
                if callable(self.func):
                    service, artist, title = self.func()
                    Notification(
                        "Artist: {}\nTitle: {}".format(artist, title),
                        title=service,
                        app_name="coderadio",
                    )
                    display_now.put(
                        "\nService: {}\n\nPlaying now: {} - {}\n".format(
                            service, artist, title
                        )
                    )
                else:
                    try:
                        metadata = get_metada(self.station.url)
                    except Exception as exc:
                        logger.debug("Metada Error: ")
                    logger.debug(metadata)
                    if not metadata:
                        display_now.put(self.station.show_info())
                    else:
                        artist, title = metadata["song"].split("-", 1)
                        artist, title = artist.strip(), title.strip()
                        service = self.station.name
                        Notification(
                            "Artist: {}\nTitle: {}".format(artist, title),
                            title=service,
                            app_name="coderadio",
                        )
                        display_now.put(
                            "\nService: {}\n\nPlaying now: {} - {}\n".format(
                                service, artist, title
                            )
                        )
            except Exception as exc:
                logger.exception("Plugin Error: ")
            time.sleep(60)


class Player:
    # https://wiki.videolan.org/VLC_command-line_help
    def __init__(self):
        # "--verbose 3 --file-logging --logfile=vlc-log.log --logmode=text"
        self._instance = vlc.Instance("--verbose -1")
        self._player = self._instance.media_player_new()

    def play(self, url):
        media = self._instance.media_new(url)
        self._player.set_media(media)
        self._player.play()

    def stop(self):
        self._player.stop()


class Radio:
    # TODO: Pegar do banco de dados favoritos ou buscar na web
    def __init__(self, start="bbc"):
        self._player = Player()
        self._rb = RadioBrowser()
        self._station_list = StationList(self._rb.stations_bytag(start))
        self._station = None
        self._plugin = None

    def play(self, **kwargs):
        self._kill_plugin()

        command, term = kwargs["command"], kwargs["term"]
        data = getattr(self._rb, f"stations_{command}")(term)
        self._station = Station(**data[0])

        self._player.play(self._playable_station(self._station.id))
        self._run_plugin(self._station)

    def _playable_station(self, id):
        try:
            station = self._rb.playable_station(id)
            logger.debug("playing now... ")
            logger.debug(station)
        except Exception as exc:
            logger.exception("Playable Station Error:")
            return
        return station["url"]

    def stop(self):
        self._player.stop()
        self._kill_plugin()

    def _run_plugin(self, station):
        self._plugin = RunPlugin(station)
        self._plugin.start()

    def _kill_plugin(self):
        try:
            self._plugin.stop()
            self._plugin = None
        except:
            pass

    # Por que esse método está aqui?
    def list(self, **kwargs):

        if not kwargs:
            return self._station_list.content

        command = kwargs.get("command")
        term = kwargs.get("term")
        command = "stations_{}".format(command)
        self._station_list.data = getattr(self._rb, command)(term)
        return self._station_list.content


radio = Radio()
