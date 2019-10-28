import datetime
from json import JSONEncoder as BuiltinJSONEncoder
from typing import Any
from uuid import UUID


def datetime_to_rfc3339(dt: datetime.datetime) -> str:
    # This is actually rfc3339 compliant
    return dt.isoformat("T")


class JSONEncoder(BuiltinJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.datetime):
            return datetime_to_rfc3339(o)
        elif isinstance(o, UUID):
            return str(o)
        else:
            return super().default(o)
