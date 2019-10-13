#!/usr/bin/python
"""
soundboard-relay

forwards mqtt messages to an mpd
"""

import argparse
from contextlib import contextmanager

import paho.mqtt.client as mqtt
from mpd import MPDClient


@contextmanager
def log_exception():
    """Helper for exception handling."""
    try:
        yield
    except Exception as exc: # pylint: disable=broad-except
        print("%s: %s" % (type(exc), exc))


class MPD:
    """Contextmanager for MPDClient."""
    def __init__(self, host, port):
        self.client = MPDClient()
        self.host = host
        self.port = port

    def __enter__(self):
        self.client.connect(self.host, self.port, 60)
        return self

    def __exit__(self, etype, value, traceback):
        if etype or value:
            print("%s: %s" % (etype, value))
        with log_exception():
            self.client.disconnect()
        return True

    def play(self, soundfile):
        """Play a soundfile."""
        with log_exception():
            self.client.clear()
            self.client.add(soundfile)
            self.client.play()


def on_connect(client, userdata, flags, rc): # pylint: disable=unused-argument,invalid-name
    """MQTT connection handler"""
    client.subscribe("psa/sound")
    client.subscribe("psa/alarm")
    client.subscribe("sensor/door/frame")
    client.subscribe("sensor/door/bell")
    print("listening")


def on_message_for_mpd(host, port):
    """wrapper for mpd configurated MQTT message handler"""
    def on_message(client, userdata, msg): # pylint: disable=unused-argument
        """MQTT message handler"""
        try:
            with MPD(host, port) as mpd:
                topic = msg.topic
                payload = msg.payload.decode()
                print(topic, payload)
                if topic == "psa/alarm":
                    payload = "ALARM.ogg"
                elif topic == "sensor/door/frame" and payload == "open":
                    payload = "door-louder.opus"
                elif topic == "sensor/door/bell" and payload == "pressed":
                    payload = "door-bell.ogg"
                elif topic != "psa/sound":
                    return
                mpd.play(payload)
        except Exception as exc: # pylint: disable=broad-except
            print(exc)
    return on_message


def main():
    """main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--mqtt', dest='mqtt', action='store_const',
                        default='mqtt.example.com')
    parser.add_argument('--mqtt-port', dest='mqtt_port', action='store_const',
                        type=int, default=1883)
    parser.add_argument('--mpd', dest='mpd', action='store_const',
                        default='mpd.example.com')
    parser.add_argument('--mpd-port', dest='mpd_port', action='store_const',
                        type=int, default=6600)
    args = parser.parse_args()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message_for_mpd(args.mqtt, args.mqtt_port)
    client.connect(args.mqtt, args.mqtt_port, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
