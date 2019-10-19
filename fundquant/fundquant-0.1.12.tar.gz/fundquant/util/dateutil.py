import datetime as dt


def today():
    return dt.datetime.today().strftime('%Y%m%d')


def today_plus(n: int, format_tpl: str = '%Y%m%d'):
    tmp = dt.datetime.today() + dt.timedelta(days=n)
    return tmp.strftime(format_tpl)


if __name__ == '__main__':
    d = today_plus(0, '%Y-%m-%dT%H:%M:%S.000Z')
    print(d)
