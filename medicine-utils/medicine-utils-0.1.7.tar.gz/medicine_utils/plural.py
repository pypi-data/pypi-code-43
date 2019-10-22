
from pytils.numeral import choose_plural


def convert_to_int(value, default=None):
    if isinstance(value, (int,)):
        return value

    if value.isdigit():
        return int(value)

    return default


def age_plural(age, skip_zero=False, string_format='{age} {age_plural}', default=None):
    age = convert_to_int(age)
    if age is not None:
        if age > 0 or (age == 0 and skip_zero is False):
            return string_format.format(age=age, age_plural=choose_plural(age, ('год', 'года', 'лет')))

    return default


def month_plural(month, string_format='{month} {month_plural}', default=None):
    month = convert_to_int(month)
    if month is not None:
        return string_format.format(month=month, month_plural=choose_plural(month, ('месяц', 'месяца', 'месяцев')))

    return default


def days_plural(days, string_format='{days} {days_plural}', default=None):
    days = convert_to_int(days)
    if days is not None:
        return string_format.format(days=days, days_plural=choose_plural(days, ('день', 'дня', 'дней')))

    return default


def smart_age_plural(age, month, default=None):
    age = convert_to_int(age, default=0)
    month = convert_to_int(month, default=0)
    if age > 0 and month > 0:
        return '{age_plural} {month_plural}'.format(
            age_plural=age_plural(age),
            month_plural=month_plural(month))

    if age == 0 and month > 0:
        return month_plural(month)

    if age > 0 and month == 0:
        return age_plural(age)

    return default


def age_display(years, months, days):
    if years > 0:
        if years < 2 and months > 0:
            return f'{age_plural(years)} {month_plural(months)}'
        else:
            return age_plural(years)
    elif months > 0:
        return month_plural(months)
    else:
        return days_plural(days)
