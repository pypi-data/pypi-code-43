import os.path
import shutil
from daemon import DaemonContext
from daemon.pidfile import PIDLockFile
from psutil import Process, NoSuchProcess
from rammon.rammon import RamMonitor
from rammon.config import RAMMON_PATH


def start(daemon=True, **kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if lock.is_locked():
        print("Rammon is already running")
        exit(1)
    elif daemon:
        print("Starting rammon as a daemon...")
    else:
        print("Starting rammon in the foreground")
    with DaemonContext(umask=0o077, pidfile=lock, detach_process=daemon) as context:
        mon = RamMonitor()
        mon.start()


def stop(**kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if lock.is_locked():
        try:
            proc = Process(lock.read_pid())
            proc.terminate()
            print("Rammon stopped successfully")
        except NoSuchProcess:
            print(
                "Rammon was already stopped, but had not stopped cleanly.\n"
                "Breaking pidfile lock..."
            )
            lock.break_lock()
    else:
        print("Rammon is already stopped")
        exit(1)


def status(**kwargs):
    lock = PIDLockFile(os.path.join(RAMMON_PATH, "rammon.pid"))
    if lock.is_locked():
        try:
            Process(lock.read_pid())
            print("Rammon is running")
        except NoSuchProcess:
            print(
                "Rammon is stopped, however it was stopped uncleanly leaving behind a pidfile.\n"
                "Breaking pidfile lock..."
            )
            lock.break_lock()
    else:
        print("Rammon is stopped")


def enable(**kwargs):
    os.umask(0o077)
    rammon_path = shutil.which("rammon")
    if rammon_path is None:
        print(
            "Could not find rammon in $PATH, this likely means it is installed in a virtualenv.\n"
            "Try leaving the virtualenv and installing with:\n"
            "   pip3 install --user rammon"
        )
        exit(1)
    if shutil.which("systemctl") is None:
        print(
            "Your system doesn't appear to be using SystemD and is not currently supported.\n"
            "If you are interested in support for other init systems, please open an issue "
            "on Github."
        )
        exit(1)
    rammon_unit_path = os.path.expanduser("~/.local/share/systemd/user/rammon.service")
    os.makedirs(os.path.dirname(rammon_unit_path), exist_ok=True)
    if not os.path.exists(rammon_unit_path):
        with open(rammon_unit_path, "w") as f:
            f.write(
                f"""[Unit]
Description=Memory usage monitor and notification daemon
[Service]
Type=simple
TimeoutStartSec=0
TimeoutStopSec=1
ExecStart={rammon_path}

[Install]
WantedBy=default.target
"""
            )
