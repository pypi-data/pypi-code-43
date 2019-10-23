import dataclasses
import enum
import json


class _EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return StrongJson.dumps(obj)


class StrongJson:
    @staticmethod
    def _is_json(json_value) -> bool:
        try:
            json.loads(json_value)
        except ValueError:
            return False
        return True

    @staticmethod
    def dumps(obj) -> str:
        if dataclasses.is_dataclass(obj):
            return json.dumps(dataclasses.asdict(obj), cls=_EnumEncoder)
        elif hasattr(obj, '__dict__'):
            json_value = json.dumps(obj.__dict__, cls=_EnumEncoder)
            if StrongJson._is_json(json_value):
                return json_value
        elif isinstance(obj, str):
            if StrongJson._is_json(obj):
                return obj

        raise ValueError(obj)
