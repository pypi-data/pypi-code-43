#! /usr/bin/env python3

"""This script reads F1 2019 telemetry packets stored in a SQLite3 database file and sends them out over UDP, effectively replaying a session of the F1 2019 game."""

import sys
import logging
import threading
import argparse
import time
import sqlite3
import socket
import selectors

from .threading_utils import WaitConsoleThread, Barrier
from ..packets import HeaderFieldsToPacketType


class PacketPlaybackThread(threading.Thread):
    """The PacketPlaybackThread reads telemetry data from an SQLite3 file and plays it back as UDP packets."""

    def __init__(self, filename, destination, port, realtime_factor, quit_barrier):
        super().__init__(name='playback')
        self._filename = filename
        self._destination = destination
        self._port = port
        self._realtime_factor = realtime_factor
        self._quit_barrier = quit_barrier

        self._packets = []
        self._packets_lock = threading.Lock()
        self._socketpair = socket.socketpair()

    def close(self):
        for sock in self._socketpair:
            sock.close()

    def run(self):
        """Read packets from database and replay them as UDP packets.

        The run method executes in its own thread.
        """
        selector = selectors.DefaultSelector()
        key_socketpair = selector.register(self._socketpair[0], selectors.EVENT_READ)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if self._destination is None:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.connect(('<broadcast>', self._port))
        else:
            sock.connect((self._destination, self._port))

        conn = sqlite3.connect(self._filename)
        cursor = conn.cursor()

        query = "SELECT timestamp, packet FROM packets ORDER BY pkt_id;"

        cursor.execute(query)

        logging.info("Playback thread started.")

        packet_count = 0
        quitflag = False

        t_first_packet = None
        t_start_playback = time.monotonic()
        while not quitflag:
            timestamped_packet = cursor.fetchone()
            if timestamped_packet is None:
                quitflag = True
                continue

            (timestamp, packet) = timestamped_packet
            if t_first_packet is None:
                t_first_packet = timestamp
            t_playback = t_start_playback + (timestamp - t_first_packet) / self._realtime_factor

            while True:
                t_sleep = max(0.0, t_playback - time.monotonic())
                for (key, events) in selector.select(t_sleep):
                    if key == key_socketpair:
                        quitflag = True

                if quitflag:
                    break

                delay = time.monotonic() - t_playback

                if delay >= 0:
                    sock.send(packet)
                    packet_count += 1
                    if packet_count % 500 == 0:
                        logging.info("{} packages sent, delay: {:.3f} ms".format(packet_count, 1000.0 * delay))
                    break


        cursor.close()
        conn.close()

        sock.close()

        self._quit_barrier.proceed()

        logging.info("playback thread stopped.")

    def request_quit(self):
        """Called from the main thread to request that we quit."""
        self._socketpair[1].send(b'\x00')


def main():

    # Configure logging.

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)-23s | %(threadName)-10s | %(levelname)-5s | %(message)s")
    logging.Formatter.default_msec_format = '%s.%03d'

    # Parse command line arguments.

    parser = argparse.ArgumentParser(description="Replay an F1 2019 session as UDP packets.")

    parser.add_argument("-r", "--rtf", dest='realtime_factor', type=float, default=1.0, help="playback real-time factor (higher is faster, default=1.0)")
    parser.add_argument("-d", "--destination", type=str, default=None, help="destination UDP address; omit to use broadcast (default)")
    parser.add_argument("-p", "--port", type=int, default=20777, help="destination UDP port (default: 20777)")
    parser.add_argument("filename", type=str, help="SQLite3 file to replay packets from")

    args = parser.parse_args()

    # Start threads.

    quit_barrier = Barrier()

    playback_thread = PacketPlaybackThread(args.filename, args.destination, args.port, args.realtime_factor, quit_barrier)
    playback_thread.start()

    wait_console_thread = WaitConsoleThread(quit_barrier)
    wait_console_thread.start()

    # Playback and wait_console threads are now active. Run until we're asked to quit.

    quit_barrier.wait()

    # Stop threads.

    wait_console_thread.request_quit()
    wait_console_thread.join()
    wait_console_thread.close()

    playback_thread.request_quit()
    playback_thread.join()
    playback_thread.close()

    # All done.

    logging.info("All done.")


if __name__ == "__main__":
    main()
