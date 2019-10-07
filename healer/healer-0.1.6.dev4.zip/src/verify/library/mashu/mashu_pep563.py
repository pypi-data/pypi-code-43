from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy


class FormattedDateTime(SerializationStrategy):

    def __init__(self, fmt):
        self.fmt = fmt

    def _serialize(self, actor_ref: datetime) -> str:
        return actor_ref.strftime(self.fmt)

    def _deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)


@dataclass
class DateTimeFormats(DataClassDictMixin):
    short: FormattedDateTime(fmt='%d%m%Y%H%M%S') = datetime.now()
    verbose: FormattedDateTime(fmt='%A %B %d, %Y, %H:%M:%S') = datetime.now()


formats = DateTimeFormats(
    short=datetime(2019, 1, 1, 12),
    verbose=datetime(2019, 1, 1, 12),
)
dictionary = formats.to_dict()
# {'short': '01012019120000', 'verbose': 'Tuesday January 01, 2019, 12:00:00'}
assert DateTimeFormats.from_text(dictionary) == formats
