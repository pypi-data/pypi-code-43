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


def ms_to_timecode(ms, fps=None):
    """
    Formats milliseconds into an hour-minute-second timecode,
    like 01:30:43 if `fps` is not set, or a hour-minute-second-frame
    timecode if fps is set, like 01:30:43:12

    When fps is set to 29.97 (NTSC), it autocorrects it to 30000/1001
    (29.97002997002997).
    """
    hours = ms // 3600000
    ms = ms - hours * 3600000
    minutes = ms // 60000
    ms = ms - minutes * 60000
    seconds = ms // 1000
    ms = ms - seconds * 1000

    if fps:
        if fps == 29.97:
            fps = 30000 / 1001.0
        frame = ms / (1000.0 / fps)
        tc = "%02d:%02d:%02d:%02d" % (hours, minutes, seconds, frame)
    else:
        tc = "%02d:%02d:%02d" % (hours, minutes, seconds)

    return tc
