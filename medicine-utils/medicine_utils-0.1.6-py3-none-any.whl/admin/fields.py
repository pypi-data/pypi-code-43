
import datetime

from django import forms
from django.utils.dates import MONTHS


class DateYearMonthWidget(forms.MultiWidget):

    def __init__(self, attrs=None, **kwargs):
        year_start = kwargs.pop('year_start', 2007)
        year_end = kwargs.pop('year_end', datetime.datetime.now().year + 1)
        widgets = (
            forms.Select(choices=list(MONTHS.items())),
            forms.Select(choices=((year, year) for year in range(year_start, year_end))),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.month, value.year]
        return [None, None]


class DateYearMonthField(forms.DateField):

    widget = DateYearMonthWidget

    def to_python(self, value):
        if isinstance(value, (list, tuple)):
            year = value[1]
            month = str(value[0]).zfill(2)
            value = f'{year}-{month}-01'
        return super().to_python(value)
