from asyncio import Lock, create_subprocess_exec
from asyncio.locks import Event
from asyncio.subprocess import PIPE
from itertools import cycle
from typing import List

from click import secho

colors = cycle(["green", "red", "yellow", "blue", "magenta", "cyan"])


class Writer:
    def __init__(self, prefix, should_print=True, color=None):
        self.prefix = f"{prefix} > "
        self.color = color or next(colors)
        self.messages = []
        self.print = should_print

    def write(self, message):
        if not message:
            return
        msg = self.prefix + message
        self.messages.append(msg)
        if self.print:
            secho(msg, fg=self.color)


class Executable:
    name: str

    def __init__(
        self, prefix: str = "", should_print: bool = True, global_lock: Lock = None
    ):
        self.done = Event()
        self.bad = Event()
        self.lock = global_lock
        self.messages: List[str] = []
        self.writer = Writer(prefix, should_print)
        self.should_shutdown = False

    def run(self):
        raise NotImplementedError()

    def set_done(self):
        self.done.set()

    def set_bad(self):
        self.bad.set()
        self.done.set()

    async def wait(self):
        await self.done.wait()

    def is_good(self):
        return not self.bad.is_set()

    async def run_command(self, command, env):
        if not command or not self.is_good():
            return
        proc = await create_subprocess_exec(*command, env=env, stdout=PIPE, stderr=PIPE)
        while not proc.stdout.at_eof():
            data = await proc.stdout.readline()
            self.writer.write(data.decode("utf-8").rstrip())
        while not proc.stderr.at_eof():
            data = await proc.stderr.readline()
            self.writer.write(data.decode("utf-8").rstrip())
        await proc.wait()
        if proc.returncode:
            self.set_bad()

    async def run_locked(self, command, env):
        async with self.lock:
            await self.run_command(command, env)
