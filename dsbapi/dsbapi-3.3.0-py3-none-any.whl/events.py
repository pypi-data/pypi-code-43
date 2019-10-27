from dataclasses import dataclass
import requests
import datetime
from typing import Optional, List
from mashumaro import DataClassJSONMixin
from icalendar import Calendar
from datetime import timedelta, timezone
import icalendar
from dateutil.rrule import *


EVENTS_URL = "https://calendar.google.com/calendar/ical/carl.humann.gymnasium%40gmail.com/public/basic.ics"


def parse_recurrences(recur_rule, start, exclusions):
    """ Find all reoccuring events """
    rules = rruleset()
    first_rule = rrulestr(recur_rule, dtstart=start)
    rules.rrule(first_rule)
    if not isinstance(exclusions, list):
        exclusions = [exclusions]
        for xdate in exclusions:
            try:
                rules.exdate(xdate.dts[0].dt)
            except AttributeError:
                pass
    now = datetime.datetime.now(timezone.utc)
    this_year = now + timedelta(days=60)
    dates = []
    for rule in rules.between(now, this_year):
        dates.append(rule.strftime("%D %H:%M UTC "))
    return dates


def truncate_datetime(datetimeordate) -> datetime.date:
    if isinstance(datetimeordate, datetime.datetime):
        return datetimeordate.date()
    else:
        return datetimeordate


@dataclass
class Event(DataClassJSONMixin):
    """Ein Event repräsentiert einen Termin des CHGs.
    Falls das '''startdate''' '''None''' ist, so ist es ein eintägiges Event,
    falls das nicht der Fall ist geht der Termin von eingeschlossen startdate
    zu eingeschlossen enddate.
    """

    title: str
    startdate: Optional[datetime.date]
    enddate: datetime.date
    time: Optional[str]
    location: Optional[str]

    def from_vevent(component):
        if component.name == "VEVENT":
            title = component.get("summary")
            description = component.get("description")
            location = component.get("location")
            startdt: datetime.datetime = component.get("dtstart").dt
            enddt: datetime.datetime = component.get("dtend").dt
            # exdate = component.get('exdate')
            # if component.get('rrule'):
            #    reoccur = component.get('rrule').to_ical().decode('utf-8')
            #    for item in parse_recurrences(reoccur, startdt, exdate):
            #        print("{0} {1}: {2} - {3}".format(item, summary, description, location))

            return Event(
                title,
                truncate_datetime(startdt),
                truncate_datetime(enddt),
                description,
                location,
            )
        else:
            return None


def parse_events() -> List[Event]:
    response = requests.get(EVENTS_URL)

    if response.status_code != 200:
        raise Exception("dsb event response not 200")

    calendar = Calendar.from_ical(response.content)
    return sorted(
        [x for x in [Event.from_vevent(e) for e in calendar.walk()] if x is not None],
        key=lambda x: x.startdate,
    )
