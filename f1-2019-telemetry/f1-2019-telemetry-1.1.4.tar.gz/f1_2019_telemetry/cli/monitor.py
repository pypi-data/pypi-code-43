#! /usr/bin/env python3

"""This script monitors a UDP port for F1 2019 telemetry packets and prints useful info upon reception."""

import argparse
import sys
import socket
import threading
import logging
import selectors
import math

from .threading_utils import WaitConsoleThread, Barrier
from ..packets import PacketID, unpack_udp_packet


class PacketMonitorThread(threading.Thread):
    """The PacketMonitorThread receives incoming telemetry packets via the network and shows interesting information."""

    def __init__(self, udp_port):
        super().__init__(name='monitor')
        self._udp_port = udp_port
        self._socketpair = socket.socketpair()

        self._current_frame = None
        self._current_frame_data = {}

    def close(self):
        for sock in self._socketpair:
            sock.close()

    def run(self):
        """Receive incoming packets and print info about them.

        This method runs in its own thread.
        """

        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Allow multiple receiving endpoints.
        if sys.platform in ['darwin']:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        elif sys.platform in ['linux', 'win32']:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Accept UDP packets from any host.
        address = ('', self._udp_port)
        udp_socket.bind(address)

        selector = selectors.DefaultSelector()

        key_udp_socket = selector.register(udp_socket, selectors.EVENT_READ)
        key_socketpair = selector.register(self._socketpair[0], selectors.EVENT_READ)

        logging.info("Monitor thread started, reading UDP packets from port {}.".format(self._udp_port))

        quitflag = False
        while not quitflag:
            for (key, events) in selector.select():
                if key == key_udp_socket:
                    # All telemetry UDP packets fit in 2048 bytes with room to spare.
                    udp_packet = udp_socket.recv(2048)
                    packet = unpack_udp_packet(udp_packet)
                    self.process(packet)
                elif key == key_socketpair:
                    quitflag = True

        self.report()

        selector.close()
        udp_socket.close()
        for sock in self._socketpair:
            sock.close()

        logging.info("Monitor thread stopped.")

    def process(self, packet):

        if packet.header.frameIdentifier != self._current_frame:
            self.report()
            self._current_frame = packet.header.frameIdentifier
            self._current_frame_data = {}

        self._current_frame_data[PacketID(packet.header.packetId)] = packet


    def report(self):
        if self._current_frame is None:
            return

        any_packet = next(iter(self._current_frame_data.values()))

        player_car = any_packet.header.playerCarIndex

        try:
            distance = self._current_frame_data[PacketID.LAP_DATA].lapData[player_car].totalDistance
        except:
            distance = math.nan

        message = "frame {:6d} distance {:10.3f}".format(self._current_frame, distance)

        if message is not None:
            logging.info(message)

    def request_quit(self):
        """Request termination of the PacketMonitorThread.

        Called from the main thread to request that we quit.
        """
        self._socketpair[1].send(b'\x00')


def main():
    """Record incoming telemetry data until the user presses enter."""

    # Configure logging.

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)-23s | %(threadName)-10s | %(levelname)-5s | %(message)s")
    logging.Formatter.default_msec_format = '%s.%03d'

    # Parse command line arguments.

    parser = argparse.ArgumentParser(description="Monitor UDP port for incoming F1 2019 telemetry data and print information.")

    parser.add_argument("-p", "--port", default=20777, type=int, help="UDP port to listen to (default: 20777)", dest='port')

    args = parser.parse_args()

    # Start recorder thread first, then receiver thread.

    quit_barrier = Barrier()

    monitor_thread = PacketMonitorThread(args.port)
    monitor_thread.start()

    wait_console_thread = WaitConsoleThread(quit_barrier)
    wait_console_thread.start()

    # Monitor and wait_console threads are now active. Run until we're asked to quit.

    quit_barrier.wait()

    # Stop threads.

    wait_console_thread.request_quit()
    wait_console_thread.join()
    wait_console_thread.close()

    monitor_thread.request_quit()
    monitor_thread.join()
    monitor_thread.close()

    # All done.

    logging.info("All done.")


if __name__ == "__main__":
    main()
