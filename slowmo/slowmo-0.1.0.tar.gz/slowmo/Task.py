from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from slowmo.Status import Running, Success


def format_time(t: datetime) -> str:
    return t.strftime("%H:%M:%S")


def format_duration(d: timedelta):
    s = int(d.seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if d > 0:
        return f"{d}d{h}h{m}m{s}s"
    elif h > 0:
        return f"{h}h{m}m{s}s"
    elif m > 0:
        return f"{m}m{s}s"
    else:
        return f"{s}s"
    return str(d)


@dataclass(frozen=True)
class Task:
    description: str
    begin: datetime = field(default_factory=lambda: datetime.now())
    status: TaskStatus = Running()

    @staticmethod
    def duration(t: Task) -> timedelta:
        if isinstance(t.status, Running):
            now = datetime.now()
            return now - t.begin
        return t.status.end - t.begin

    @staticmethod
    def display(t: Task, spinner="X") -> str:
        # TODO account for columns/width
        if isinstance(t.status, Success):
            spinner = "✓"
        begin = format_time(t.begin)
        duration = format_duration(Task.duration(t))
        prefix = f"{spinner} {t.description} [{begin}|{duration}"
        if isinstance(t.status, Running):
            return prefix + "]"
        end = format_time(t.status.end)
        return prefix + f"|{end}]"

    @staticmethod
    def replace_status(t: Task, st: Status) -> Task:
        return Task(t.description, t.begin, st)
