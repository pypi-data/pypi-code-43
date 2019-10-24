"""just a bunch of functions that make life easier"""
import json
import datetime
import calendar

def ga_dim_met_create(dims, mets):
    #make GA dimension / metric list
    return [{'name': 'ga:' + d} for d in dims], [{'expression': 'ga:' + m} for m in mets]

def derive_dates(dt):
    """derive 1st of the current month and 1st of the next month from date padded in"""
    s = datetime.datetime.strftime((datetime.datetime(dt.year, dt.month, 1)), '%Y-%m-%d')
    e = datetime.datetime.strftime((datetime.datetime(dt.year, dt.month, dt.day+1)), '%Y-%m-%d')
    return s, e

def derive_dates_posts(dt):
    """parameters to query data for relative to today, return start and end of current month"""
    s = datetime.datetime.strftime((datetime.datetime(dt.year, dt.month, 1)), '%Y-%m-%d')
    e = datetime.datetime.strftime(dt.replace(day=calendar.monthrange(dt.year, dt.month)[1]),
                                   '%Y-%m-%d')
    return s, e

# functions to help with JSON
def print_json(j):
    print(json.dumps(j, indent=4, sort_keys=True))

def write_json(p: list, pth: str, fn: str):
    with open(f'./{pth}/{fn}.json', 'w') as f:
        json.dump(p, f)

def read_json(pth: str, fn: str):
    try:
        with open(f'{pth}/{fn}.json', 'r', encoding='utf-8') as f:
            d = json.load(f)
    except FileNotFoundError:
        with open(f'{fn}.json', 'r', encoding='utf-8') as f:
            d = json.load(f)

    return d

