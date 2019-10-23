__all__ = [
    'get_date_query', 'get_days_ago_query', 'get_hours_ago_query',
    'get_minutes_ago_query',
]

import dt_helper as dh
from bson.objectid import ObjectId


def get_date_query(date_string, fmt='%Y-%m-%d', timezone="America/Chicago",
                   timestamp_field='_id'):
    """Return a dict representing a query for matching date in a timezone

    - fmt: format the date_string is in
    - timezone: timezone to use for determining start of day
    - timestamp_field: name of timestamp field to query on
    """
    dt = dh.date_start_utc(date_string, fmt, timezone)
    query = {timestamp_field: {}}
    start = dt
    end = dt + dh.timedelta(days=1)
    if timestamp_field == '_id':
        start = ObjectId.from_datetime(start)
        end = ObjectId.from_datetime(end)
    query[timestamp_field]['$gte'] = start
    query[timestamp_field]['$lt'] = end
    return query


def get_days_ago_query(days_ago=0, until_days_ago=0, timezone="America/Chicago",
                       timestamp_field='_id'):
    """Return a dict representing a query for matching day(s) in a timezone

    - timestamp_field: name of timestamp field to query on
    """
    assert days_ago >= until_days_ago
    if days_ago > 0:
        assert days_ago != until_days_ago
    query = {timestamp_field: {}}
    start = dh.days_ago(days_ago, timezone=timezone)
    end = dh.days_ago(until_days_ago, timezone=timezone)
    if timestamp_field == '_id':
        start = ObjectId.from_datetime(start)
        end = ObjectId.from_datetime(end)
    query[timestamp_field]['$gte'] = start
    if days_ago > 0:
        query[timestamp_field]['$lt'] = end
    return query


def get_hours_ago_query(hours_ago=1, until_hours_ago=0, timestamp_field='_id'):
    """Return a dict representing a query for matching hour(s)

    - timestamp_field: name of timestamp field to query on
    """
    assert hours_ago > until_hours_ago
    now = dh.utc_now_localized()
    query = {timestamp_field: {}}
    start = now - dh.timedelta(hours=hours_ago)
    end = now - dh.timedelta(hours=until_hours_ago)
    if timestamp_field == '_id':
        start = ObjectId.from_datetime(start)
        end = ObjectId.from_datetime(end)
    query[timestamp_field]['$gte'] = start
    query[timestamp_field]['$lt'] = end
    return query


def get_minutes_ago_query(minutes_ago=1, until_minutes_ago=0, timestamp_field='_id'):
    """Return a dict representing a query for matching minute(s)

    - timestamp_field: name of timestamp field to query on
    """
    assert minutes_ago > until_minutes_ago
    now = dh.utc_now_localized()
    query = {timestamp_field: {}}
    start = now - dh.timedelta(minutes=minutes_ago)
    end = now - dh.timedelta(minutes=until_minutes_ago)
    if timestamp_field == '_id':
        start = ObjectId.from_datetime(start)
        end = ObjectId.from_datetime(end)
    query[timestamp_field]['$gte'] = start
    query[timestamp_field]['$lt'] = end
    return query
