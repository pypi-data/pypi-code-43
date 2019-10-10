from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from shuttlis.time import from_iso_format


@dataclass
class After:
    """
    This class represents how we make the cursor for cursor based pagination.
    The default logic is to combine the created_at and uuid of the object to create
    a cursor which is then used by the frontend. This class is used by Cursor and
    the Paginator class.

    The Cursor and Paginator classes are configurable to use any other class. Just make
    sure that the class has the `from_string`, `from_data` and `__str__` implemented.
    """

    id: UUID
    date: datetime

    @classmethod
    def from_string(cls, after) -> "After":
        offset = after.split("|")
        dt = from_iso_format(offset[0])
        id = UUID(offset[1])
        return cls(id, dt)

    @classmethod
    def from_data(cls, data) -> "After":
        return cls(data.id, data.created_at)

    def __str__(self):
        return f"{self.date.isoformat()}|{self.id}"


@dataclass
class Cursor:
    """
    This represents the cursor that the frontend will send to the backend. Consider
    the following requests

    /rs?limit=10
    /rs?after=2019-01-08T16:59:48+00:00|ce581a45-48a7-4ff8-b627-9ff2d43d2ea6
    /rs?after=2019-01-08T16:59:48+00:00|ce581a45-48a7-4ff8-b627-9ff2d43d2ea6&limit=9

    One can directly construct the Cursor object using the query params obj
    e.g. Flask
    >>> from flask import request
    >>> c = Cursor.from_dict(request.args)

    or if you have extracted out the params yourself then you can use the from_strings
    classmethod
    >>> c = Cursor.from_strings(
    >>>     "2019-01-08T16:59:48.377325+00:00|ce581a45-48a7-4ff8-b627-9ff2d43d2ea6",
    >>>     "10",
    >>> )

    Then one can use this object anywhere to do pagination at let's say db level
    >>> from sqlalchemy import or_, and_
    >>> from store import db, MyModel
    >>> query = db.session.query(MyModel)
    >>> if c.after:
    >>>     query = query.filter(
    >>>         or_(
    >>>             MyModel.created_at > c.after_date,
    >>>             and_(MyModel.created_at == c.after_date, MyModel.id > c.after_id),
    >>>         )
    >>>     )
    >>> return query.order_by(MyModel.created_at, MyModel.id).limit(c.limit).all()
    """

    after: Optional[After]
    limit: Optional[int] = 10

    @property
    def after_id(self) -> Optional[UUID]:
        return self.after.id if self.after else None

    @property
    def after_date(self) -> Optional[datetime]:
        return self.after.date if self.after else None

    def as_dict(self):
        dikt = {"limit": self.limit}

        if self.after:
            dikt["after"] = str(self.after)

        return dikt

    @classmethod
    def from_dict(cls, json, custom_class=After) -> "Cursor":
        after = None

        if json.get("after"):
            after = custom_class.from_string(json["after"])

        return Cursor(after, json.get("limit", 10))

    @classmethod
    def from_strings(cls, after: str = None, limit: str = "10") -> "Cursor":
        if after:
            after = After.from_string(after)

        if limit is None:
            limit = 10

        return Cursor(after, int(limit))


@dataclass
class Paginator:
    """
    This represents the pagination info that the backend will send to the frontend.
    Consider the following response.
    >>> {
    >>>     "data": [ ... ],
    >>>     "meta": {
    >>>         "cursor": {
    >>>             "limit": 10,
    >>>             "total": 100,
    >>>             "last": "2019-01-08T16:59:48|ce581a45-48a7-4ff8-b627-9ff2d43d2ea6"
    >>>         }
    >>>     }
    >>> }

    Now the frontend can use this info to query for the next page.
    Now let's look at how this can be constructed.

    Basic idea is that the objects that are involved in pagination should have `id` and
    `created_at` fields that are used to construct this data.

    This is how one can use this with flask
    >>> import json
    >>> from flask import Response

    Somewhere in your controller
    >>> data = [ ... ] # get from somewhere
    >>> p = Paginator.from_data(data)
    >>> payload = {"data": data, "meta": {"cursor": p.as_dict()}}
    >>> return Response(json.dumps(payload), mimetype="application/json")
    """

    after: Optional[After]
    limit: int = 10
    total: Optional[int] = None

    @property
    def after_id(self) -> Optional[UUID]:
        return self.after.id if self.after else None

    @property
    def after_date(self) -> Optional[datetime]:
        return self.after.date if self.after else None

    @classmethod
    def from_data(cls, data, page_size=10, total=None, custom_cls=After) -> "Paginator":
        cur = None

        if data:
            last = data[-1]
            cur = custom_cls.from_data(last)

        return cls(after=cur, limit=page_size, total=total)

    def as_dict(self) -> Dict:
        json_res = {"page_size": self.limit}

        if self.total:
            json_res["total"] = self.total

        if self.after:
            json_res["last"] = str(self.after)

        return json_res

    @classmethod
    def from_dict(cls, dikt, custom_cls=After) -> "Paginator":
        after = None

        if dikt.get("last"):
            after = custom_cls.from_string(dikt.get("last"))

        return cls(after, dikt.get("limit", 10), dikt.get("total"))
