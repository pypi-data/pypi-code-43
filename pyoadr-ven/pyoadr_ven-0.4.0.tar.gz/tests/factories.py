from datetime import datetime
from datetime import timedelta

import factory
from factory import fuzzy
from pony import orm
from pyoadr_ven import database


class EventFactory(factory.Factory):
    class Meta:
        model = database.Event

    request_id = factory.Sequence(lambda n: str(n))
    event_id = factory.Sequence(lambda n: str(n))

    official_start = fuzzy.FuzzyNaiveDateTime(
        datetime.utcnow() + timedelta(days=+1), datetime.utcnow() + timedelta(days=+14)
    )
    duration = timedelta(minutes=30)
    start_after = timedelta(seconds=0)
    start_offset = timedelta(seconds=0)
    start_time = factory.LazyAttribute(lambda e: e.official_start + e.start_offset)
    end_time = factory.LazyAttribute(lambda e: e.official_start + e.duration)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        orm.commit()
        return obj


class ReportFactory(factory.Factory):
    class Meta:
        model = database.Report

    start_time = datetime.utcnow()
    end_time = datetime.utcnow() + timedelta(hours=12)
    duration = timedelta(hours=12)
    name = "test_report"
    interval_secs = 1
    telemetry_parameters = ""
    request_id = factory.Sequence(lambda n: str(n))
    specifier_id = factory.Sequence(lambda n: str(n))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = model_class(*args, **kwargs)
        orm.commit()
        return obj
