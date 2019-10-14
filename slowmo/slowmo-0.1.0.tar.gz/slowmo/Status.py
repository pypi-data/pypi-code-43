from dataclasses import dataclass, field
from datetime import datetime
from typing import Union


@dataclass
class Running:
    pass


@dataclass
class Success:
    end: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class Fail:
    # TODO reason? error?
    end: datetime = field(default_factory=lambda: datetime.now())


Status = Union[Running, Success, Fail]
