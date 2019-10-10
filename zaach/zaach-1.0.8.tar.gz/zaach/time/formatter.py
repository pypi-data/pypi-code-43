import datetime


def iso_8601_duration(seconds):
    hours = seconds // 3600
    seconds = seconds % 3600
    minutes = seconds // 60
    seconds = seconds % 60

    formatted_date = "PT"
    if hours:
        formatted_date = "%s%dH" % (formatted_date, hours)
    if minutes:
        formatted_date = "%s%dM" % (formatted_date, minutes)
    if seconds or formatted_date == "PT":
        formatted_date = "%s%dS" % (formatted_date, seconds)

    return formatted_date


def timestamp(utc_dt=None):
    """
    Returns the utc timestamp of now or the given utc_dt object.
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    dt = utc_dt or datetime.datetime.utcnow()
    return (dt - epoch).total_seconds()
