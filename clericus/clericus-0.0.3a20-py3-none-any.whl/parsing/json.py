import dataclasses
from json import *
from json import dumps as _dumps


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


def dumps(o, *args, **kwargs):
    return _dumps(o, cls=EnhancedJSONEncoder, *args, **kwargs)