from datetime import timedelta


def format_date(datetime_obj, fmt):
    return datetime_obj.strftime(fmt)


def day_delta(datetime_obj, number_of_days):
    return datetime_obj + timedelta(number_of_days)
