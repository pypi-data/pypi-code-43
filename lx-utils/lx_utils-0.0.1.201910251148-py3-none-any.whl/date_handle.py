from calendar import Calendar
from datetime import datetime as dt


def get_year_dates(year: int, date_format='%Y%m%d'):
    '''

    :param year:
    :param date_format:
    :return: -> list[str]  某年所有日期
    '''

    d = []
    c = Calendar(year)
    for i in range(12):
        for week in c.monthdatescalendar(year, int(i + 1)):
            for date in week:
                if date.year == year:
                    date = date.strftime(date_format)
                    if date not in d:
                        d.append(date)

    return d


def change_str_date_format(str_date, old_format='%Y/%m/%d', new_format='%Y-%m-%d'):
    '''

    :param str_date:date str
    :param old_format:str
    :param new_format:str
    :return:
    '''
    d1 = dt.strptime(str_date, old_format)
    return d1.strftime(new_format)
