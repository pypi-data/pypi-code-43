import datetime
import decimal
import json


class DateTimeDecimalJSONEncoder(json.encoder.JSONEncoder):

    class FakeFloat(float):
        def __init__(self, value):
            super().__init__()
            self._value = value

        def __repr__(self):
            return str(self._value)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return self.FakeFloat(obj)
        else:
            return super(DateTimeDecimalJSONEncoder, self).default(obj)
