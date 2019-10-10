import datetime


CET_OFFSET = 1
CEST_OFFSET = 2


def get_last_sunday(year, month):
    """
    Returns the last sunday in a given year of a given month as a date.
    """
    for day in range(31, 0, -1):
        try:
            dt = datetime.date(year, month, day)
        except ValueError:
            continue
        else:
            weekday = dt.weekday()
            if weekday != 6:
                dt = dt - datetime.timedelta(days=weekday + 1)
            return dt


def get_utc_offset_reference(utc_dt):
    """
    Returns the offset from UTC to Central European (Summer) time, in hours.
    This implementation is not very performant and should only be used for
    edge cases and as a reference implementation to test against.
    """
    year = utc_dt.year

    sun = get_last_sunday(year, 3)
    cest_barrier = datetime.datetime(year, 3, sun.day, 1)

    sun = get_last_sunday(year, 10)
    cet_barrier = datetime.datetime(year, 10, sun.day, 1)

    if utc_dt < cest_barrier:  # 1.1. till xx.03.
        return CET_OFFSET
    elif utc_dt < cet_barrier:  # xx.3. till xx.10.
        return CEST_OFFSET
    else:  # xx.10. till 31.12.
        return CET_OFFSET


def get_utc_offset(utc_dt):
    """
    Returns the offset from UTC to Central European (Summer) time, in hours.
    This implementation is way more performant, due to the following facts:
    * November, December, January, February are CET
    * March is CET up to the last sunday, 1am UTC, then CEST
    * April, May, June, July, August, September are CEST
    * October is CEST up to the last sunday, 1am UTCu, then CET
    * A month with 31 days cannot have a last sunday earlier than the 25th.
    """
    month, day = utc_dt.month, utc_dt.day
    if month in [4, 5, 6, 7, 8, 9]:
        return CEST_OFFSET
    elif month in [1, 2, 11, 12]:
        return CET_OFFSET
    elif month == 3:
        if day < 25:
            return CET_OFFSET
        else:  # days 25 to 31
            return get_utc_offset_reference(utc_dt)
    else:  # month == 10
        if day < 25:
            return CEST_OFFSET
        else:  # days 25 to 31
            return get_utc_offset_reference(utc_dt)


def utc_to_cet_or_cest(utc_dt):
    """
    Returns a datetime in CET or CEST, whatever is used at that time.
    """
    utc_offset = datetime.timedelta(hours=get_utc_offset(utc_dt))
    return utc_dt + utc_offset
