import datetime
import decimal
import json
from uuid import UUID

from bson import ObjectId


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.seconds
        elif isinstance(obj, decimal.Decimal):
            return float(str(obj))
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode(encoding="utf8", errors='ignore')
        elif isinstance(obj, UUID):
            return obj.hex
        else:
            return super().default(obj)
