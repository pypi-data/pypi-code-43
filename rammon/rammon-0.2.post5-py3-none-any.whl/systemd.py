import functools
from pydbus import SessionBus
from gi.repository.GLib import GError

try:
    bus = SessionBus()
    systemd = bus.get(".systemd1")
except GError:
    systemd = None


def gerror_free(func):
    """
    Wraps a function such that it returns false if systemd doesn't exist or a GEvent error is raised
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if systemd is None:
            return False
        try:
            return func(*args, **kwargs)
        except GError:
            return False

    return wrapper


@gerror_free
def try_systemd_start() -> bool:
    """
    Attempts to start rammon with systemd
    :return: whether succesful
    """
    # GetUnitFileState raises GError if the service doesn't exist
    systemd.GetUnitFileState("rammon.service")
    systemd.StartUnit("rammon.service", "fail")
    return True


@gerror_free
def try_systemd_stop() -> bool:
    """
    Attempts to stop rammon with systemd
    :return: whether succesful
    """
    # GetUnit raises GError if the service doesn't exist
    systemd.GetUnit("rammon.service")
    systemd.StopUnit("rammon.service", "fail")
    return True


@gerror_free
def is_enabled() -> bool:
    return systemd.GetUnitFileState("rammon.service") == "enabled"
