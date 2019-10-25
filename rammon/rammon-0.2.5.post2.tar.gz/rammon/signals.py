import signal
from gi.repository import GLib


def set_handlers(mon):
    GLib.unix_signal_add(
        GLib.PRIORITY_HIGH,
        signal.SIGTERM,  # for the given signal
        mon.stop,  # on this signal, run this function
        signal.SIGTERM,  # with this argument
    )
    GLib.unix_signal_add(
        GLib.PRIORITY_HIGH,
        signal.SIGINT,  # for the given signal
        mon.stop,  # on this signal, run this function
        signal.SIGINT,  # with this argument
    )
