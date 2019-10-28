from datetime import datetime, timedelta


def this_month(two_dig: bool = False):
    d = datetime.date.today()
    if two_dig:
        return [d.year, '{:02d}'.format(d.month)]
    else:
        return [d.year, d.month]


def previous_month(min: int = 1, two_dig: bool = False):
    now = datetime.now()
    past = now - timedelta(days=(min * 365) / 12)
    if two_dig:
        return [past.year, '{:02d}'.format(past.month)]
    else:
        return [past.year, past.month]


if __name__ == '__main__':
    print('One digit months')
    print('last month', previous_month(1))
    print('previous month', previous_month(3))
    print('last month, last year', previous_month(13))

    print('Two digit months')
    print('last month', previous_month(1, True))
    print('previous month', previous_month(3, True))
    print('last month, last year', previous_month(13, True))







