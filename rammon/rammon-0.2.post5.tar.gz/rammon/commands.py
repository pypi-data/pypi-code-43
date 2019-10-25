import os.path
import shutil
import signal
import sys
from typing import Union, List
from dataclasses import asdict, fields
from pydbus import SessionBus
from gi.repository.GLib import GError
from daemon import DaemonContext
from daemon.pidfile import PIDLockFile
from psutil import Process, NoSuchProcess, TimeoutExpired
from rammon.rammon import RamMonitor
from rammon.config import RAMMON_PATH, conf
from rammon.logging import logger
from rammon.systemd import try_systemd_start, try_systemd_stop, is_enabled
from rammon.signals import set_handlers


def start(daemon=True, **kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if lock.is_locked():
        try:
            Process(lock.read_pid())
            print("Rammon is already running")
            sys.exit(1)
        except NoSuchProcess:
            print(
                "Rammon was stopped, however it was stopped uncleanly leaving behind a pidfile.\n"
                "Breaking pidfile lock..."
            )
            lock.break_lock()
    if daemon:
        logger.info("Starting rammon as a daemon...")
    else:
        logger.info("Starting rammon in the foreground...")

    if daemon:
        if try_systemd_start():
            logger.info("Starting with systemd...")
            sys.exit(0)
        else:
            mon = RamMonitor()
            set_handlers(mon)
            logger.info("Starting without systemd...")
            with DaemonContext(umask=0o077, pidfile=lock, detach_process=daemon):
                mon.start()
    else:
        with lock:
            mon = RamMonitor()
            set_handlers(mon)
            mon.start()


def stop(**kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if try_systemd_stop():
        logger.info("Stopping rammon daemon with systemd...")
    if lock.is_locked():
        try:
            proc = Process(lock.read_pid())
            proc.terminate()
            try:
                proc.wait(1)
            except TimeoutExpired:
                print("Rammon did not stop gracefully, killing it...")
                proc.kill()
                lock.break_lock()
            logger.info("Rammon stopped successfully")
        except NoSuchProcess:
            logger.warning(
                "Rammon was already stopped, but had not stopped cleanly.\n"
                "Breaking pidfile lock..."
            )
            lock.break_lock()
    else:
        logger.error("Rammon is already stopped")
        sys.exit(1)


def status(**kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if lock.is_locked():
        try:
            Process(lock.read_pid())
            print(
                "Rammon is running"
                + (", and auto-start is enabled" if is_enabled() else "")
            )
        except NoSuchProcess:
            print(
                "Rammon is stopped, however it was stopped uncleanly leaving behind a pidfile.\n"
                "Breaking pidfile lock..."
            )
            lock.break_lock()
    else:
        print(
            "Rammon is stopped"
            + (", but auto-start is enabled" if is_enabled() else "")
        )


def enable(**kwargs):
    os.umask(0o077)
    rammon_path = shutil.which("rammon")
    if rammon_path is None:
        print(
            "Could not find rammon in $PATH, this likely means it is installed in a virtualenv.\n"
            "Try leaving the virtualenv and installing with:\n"
            "   pip3 install --user rammon"
        )
        sys.exit(1)
    if shutil.which("systemctl") is None:
        print(
            "Your system doesn't appear to be using systemd and is not currently supported.\n"
            "If you are interested in support for other init systems, please open an issue "
            "on Github."
        )
        sys.exit(1)
    rammon_unit_path = os.path.expanduser("~/.local/share/systemd/user/rammon.service")
    os.makedirs(os.path.dirname(rammon_unit_path), exist_ok=True)
    if not os.path.exists(rammon_unit_path):
        print(
            "Creating systemd unit at:\n"
            "   ~/.local/share/systemd/user/rammon.service"
        )
        with open(rammon_unit_path, "w") as f:
            f.write(
                f"""[Unit]
Description=Memory usage monitor and notification daemon
[Service]
Type=simple
TimeoutStartSec=0
TimeoutStopSec=1
ExecStart={rammon_path} -d
Environment=LAUNCHED_FROM_SYSTEMD=1
Restart=on-failure
RestartSec=20

[Install]
WantedBy=default.target
"""
            )
    bus = SessionBus()
    systemd = bus.get(".systemd1")
    if systemd.GetUnitFileState("rammon.service") == "enabled":
        print("Rammon auto-start is already enabled")
        sys.exit(1)
    if systemd.EnableUnitFiles(["rammon.service"], False, False)[0]:
        print("Rammon enable and will now start on login!")
    else:
        print(
            "Rammon failed to be enabled and I don't know why...\n"
            "Try enabling it manually with:\n"
            "   systemctl enable --user rammon"
        )


def disable(settings, **kwargs):
    try:
        bus = SessionBus()
        systemd = bus.get(".systemd1")
        if systemd.DisableUnitFiles(["rammon.service"], False):
            print("Disabled rammon, it will no longer auto-start")
            sys.exit(0)
    except GError:
        pass
    print("Rammon is already disabled")
    sys.exit(1)


def config(settings: Union[List[str], None], **kwargs):
    if settings:
        try:
            conf_field_types = {f.name: f.type for f in fields(conf)}
            new_values = [setting.split("=") for setting in settings]
            for k, v in new_values:
                setattr(conf, k, conf_field_types[k](v))
            conf.persist()
        except ValueError:
            print("Values must be in the format SETTING=value")
            exit(1)
        except KeyError as e:
            print(f"Unknown setting: {e.args[0]}")
            print(1)
    print("rammon config:")
    print("\n".join(f"{k}={v!r}" for k, v in asdict(conf).items()))
