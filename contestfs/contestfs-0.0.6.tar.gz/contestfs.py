#!/usr/bin/env python
"""
Continous monitor/run loop.
"""

import argparse
import itertools
import os
import subprocess
import sys
import time
from datetime import timedelta

import colorama
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

__version__ = "0.0.6"


class RuntimeCounter(object):
    def __init__(self):
        self.time0 = self.prev = time.time()
        self.number = itertools.count(1)

    def elapsed(self, now):
        return timedelta(seconds=now - self.time0)

    def interval(self, now):
        try:
            return timedelta(seconds=now - self.prev)
        finally:
            self.prev = now

    def report(self, now):
        return "{}. {} / {}".format(
            next(self.number), self.interval(now), self.elapsed(now)
        )


class VerbosePrinter(RuntimeCounter):
    def __init__(self):
        super(VerbosePrinter, self).__init__()
        colorama.init()

    def before_run(self, path, command):
        print("\nRun: {}".format(command))

    def after_run(self, rc):
        now = time.time()
        if rc == 0:
            self._ok(now)
        else:
            self._failed(now)

    def _ok(self, now):
        sys.stdout.write(colorama.Fore.GREEN)
        sys.stdout.write("[OK] ")
        sys.stdout.write(colorama.Fore.RESET)
        print(self.report(now))

    def _failed(self, now):
        sys.stdout.write(colorama.Fore.RED)
        sys.stdout.write("[FAILED] ")
        sys.stdout.write(colorama.Fore.RESET)
        print(self.report(now))


class TimeInterval(object):
    """Prevent too frequent exeuction"""

    def __init__(self, interval):
        self.interval = interval
        self.last_time = time.time() - self.interval

    def enough(self):
        return time.time() - self.last_time > self.interval

    def update_last_time(self):
        self.last_time = time.time()


class ContestHandler(PatternMatchingEventHandler):
    def __init__(self, command, patterns):
        self.running = False
        super(ContestHandler, self).__init__(patterns=patterns, ignore_directories=True)
        self.command = [x.replace("{}", "{path}") for x in command]
        self.interval = TimeInterval(1)
        self.printer = VerbosePrinter()

    def _on_modified(self, path):
        if self.interval.enough():
            self.run(path)
            self.interval.update_last_time()

    def on_moved(self, event):
        self._on_modified(event.dest_path)

    def on_modified(self, event):
        self._on_modified(event.src_path)

    on_created = on_modified

    def run(self, path):
        self.running = True
        fn, ext = os.path.splitext(os.path.basename(path))
        ext = ext[1:]
        try:
            args = [arg.format(path=path, fn=fn, ext=ext) for arg in self.command]
            self.printer.before_run(path, " ".join(args))
            rc = subprocess.call(args, shell=sys.platform == "win32")
            self.printer.after_run(rc)
        finally:
            self.running = False


def _main(command, patterns, recursive, path, initial_run):
    event_handler = ContestHandler(command, patterns)
    observer = Observer()
    try:
        observer.schedule(event_handler, path=path, recursive=recursive)
    except KeyboardInterrupt:
        return

    if initial_run:
        event_handler.run("")

    observer.start()
    try:
        while True:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                if not event_handler.running:
                    break
    finally:
        observer.unschedule_all()
        observer.stop()
        observer.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s {}".format(__version__)
    )
    parser.add_argument(
        "-r",
        dest="recursive",
        action="store_false",
        default=True,
        help="no recursive (default: recursive)",
    )
    parser.add_argument("-p", dest="path", default=".")
    parser.add_argument(
        "-1",
        dest="initial_run",
        action="store_true",
        default=False,
        help="Run at least once before any change.",
    )
    parser.add_argument("extensions", nargs=1, help="extensions, - for all, ex: py,pyc")
    parser.add_argument(
        "command", nargs=argparse.REMAINDER, help="A command to execute"
    )
    args = parser.parse_args()

    if args.extensions == ["-"]:
        patterns = ["*"]
    else:
        patterns = ["*." + ext for ext in args.extensions[0].split(",")]

    _main(args.command, patterns, args.recursive, args.path, args.initial_run)


if __name__ == "__main__":
    main()
