import logging

from django.db import transaction
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.fields.date_time_field import DateTimeField
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy

logger = logging.getLogger(__name__)


def get_graph(request):
    from clndr.time_line import Timeline

    request = DSRequest(request=request)
    shiftsList = Timeline(calendar_id=request.json.get('calendar_id'), logger=logger).build()
    json = shiftsList.to_json()
    return json

class CalendarsQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def delete(self):
        from clndr.models.calendar_shifts_days import Calendar_shifts_days
        from clndr.models.holidays import Holidays

        with transaction.atomic():
            for item in self:
                Calendar_shifts_days.objects.filter(calendar=item).delete()
                Holidays.objects.filter(calendar=item).delete()

            return super().delete()

class CalendarsManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'begindate': record.begindate,
            'enddate': record.enddate,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res

    def get_queryset(self):
        return CalendarsQuerySet(self.model, using=self._db)

    def copyFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        id = data.get('id')

        calendar = Calendars.objects.get(id=id)
        calendar = calendar.copy()

        calendar = model_to_dict(calendar)

        return calendar


class Calendars(BaseRefHierarcy):
    begindate = DateTimeField(verbose_name='Начало', db_index=True, null=True, blank=True)
    enddate = DateTimeField(verbose_name='Конец', db_index=True, null=True, blank=True)

    objects = CalendarsManager()

    def __str__(self):
        return f"ID={self.id}, begindate={self.begindate}, enddate={self.enddate}"

    def copy(self):
        from clndr.models.calendar_shifts_days import Calendar_shifts_days
        from clndr.models.holidays import Holidays

        if self.begindate == None or self.enddate == None:
            raise Exception(f'Begindate or EndDate is null.')

        with transaction.atomic():
            calendar = model_to_dict(self)
            delAttr(calendar, 'id')
            parent = calendar.get('parent')
            delAttr(calendar, 'parent')
            setAttr(calendar, 'parent_id', parent)
            calendar = Calendars.objects.create(**calendar)

            for calendar_shifts_days in Calendar_shifts_days.objects.filter(calendar=self):
                _calendar_shifts_days = calendar_shifts_days.copy()
                _calendar_shifts_days.calendar = calendar
                _calendar_shifts_days.save()

            for holiday in Holidays.objects.filter(calendar=self):
                holiday = model_to_dict(holiday)
                delAttr(holiday, 'id')
                setAttr(holiday, 'calendar', calendar)
                daytype = holiday.get('daytype')
                delAttr(holiday, 'daytype')
                setAttr(holiday, 'daytype_id', daytype)
                Holidays.objects.create(**holiday)

            return calendar

    class Meta:
        verbose_name = 'Календари'
