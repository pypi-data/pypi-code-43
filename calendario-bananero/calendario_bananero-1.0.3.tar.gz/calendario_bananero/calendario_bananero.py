from datetime import datetime, timedelta


"""
We have a default dictionary with the initial dates of each year.
dates : {year: start_date ...}
tz: pytz object
"""

class CalendarioBananero:
    def __init__(self, dates):
        self.dates = dates

    def get_leap(self, year):
        date = self.dates[year]
        starting_day_of_year = datetime.now().date().replace(year=year, month=1, day=1)
        diff = date - starting_day_of_year

        return diff

    def get_weekdates_range(self, year, week):
        firstdayofweek = datetime.strptime(f'{year}-W{int(week)- 1}-1', "%Y-W%W-%w").date()
        lastdayofweek = firstdayofweek + timedelta(days=6.9)

        leap = self.get_leap(year)
        if leap:
            firstdayofweek = firstdayofweek + timedelta(days=leap.days + 1)
            lastdayofweek = lastdayofweek + timedelta(days=leap.days + 1)

        return (firstdayofweek, lastdayofweek)

    def get_week_from_date(self, year, date):
        leap = self.get_leap(year)
        return int((date + timedelta(days=leap.days + 3)).strftime("%V"))

    def get_periods_date_range(self, year, period):
        semanas = [period * 3 - 2, period * 3 - 1, period * 3]
        fechas = [self.get_weekdates_range(year, semana) for semana in semanas]

        return [fechas[0][0], fechas[len(fechas) - 1][1]]
