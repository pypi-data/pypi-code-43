#!/usr/bin/env python

"""
Produce JS from PY while watching
"""

from __future__ import annotations

import logging
import subprocess
import sys
import time

from devrepo import base_dir, shell
from watchdog.events import LoggingEventHandler, RegexMatchingEventHandler
from watchdog.observers import Observer

project_dir = base_dir()
source_path = base_dir(with_path='src/main/healer/station/client/')
source_file = base_dir(with_path='src/main/healer/station/client/arkon.py')

print(f"source_path={source_path}")
print(f"source_file={source_file}")

command = [
    'bash', '-c',
    f"transcrypt {source_file} --map --nomin --dassert",
]


class BuildEventHandler(RegexMatchingEventHandler):
    ""

    def __init__(self):
        super().__init__(
            regexes=[r".*[.]py"],
            ignore_regexes=[],
            ignore_directories=True,
         )

    def on_any_event(self, event):
        print(f"event: {event}")
        print(f"source_file: {source_file}")
        try:
            subprocess.check_call(command, cwd=project_dir)
        except Exception as error:
            pass


logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

event_handler = BuildEventHandler()

observer = Observer(timeout=3)
observer.schedule(event_handler, source_path, recursive=False)
observer.start()

try:
    while True:
        print("watch")
        time.sleep(10)
except KeyboardInterrupt:
    observer.stop()

observer.join()
