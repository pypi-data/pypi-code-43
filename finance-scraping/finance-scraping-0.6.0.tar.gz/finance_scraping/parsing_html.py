from math import isnan
import re

from bs4 import BeautifulSoup


def string_to_float(string):
    """
    Convert a string with a comma (i.e. '3.14') to a float.

    :param str string: string representing a float
    :return numpy.float:
    """
    # \xa0 is non-breaking space in latin1
    string_modif = string.replace(u',', u'.').replace(u'\xa0', u'')

    # empty strings or symbols (e.g. '-') would throw a ValueError
    try:
        return float(string_modif)
    except ValueError:
        return float('nan')


def to_null(d):
    """
    Converts the NaN (not a number) or empty values of a dictionary to the
    string 'NULL'.

    :param dict d: dictionary to convert
    :return dict: dictionary where NaN and empty values are 'NULL'
    """
    for key, value in d.items():
        if isinstance(value, float):
            if isnan(value):
                d[key] = 'NULL'
        elif isinstance(value, str):
            if not value:
                d[key] = 'NULL'
    return d


def get_company_name(soup):
    """
    :param soup: BeautifulSoup object
    :return str: company name
    """
    found = soup.find(
        'span',
        attrs={'class': 'securityName'}
    ).get_text()
    return found


def get_last_quote(soup):
    """
    :param soup: BeautifulSoup object
    :return str: last quote of the day
    """
    found = soup.find('span', attrs={'id': 'Col0Price'}).get_text()
    return string_to_float(found)


def get_date_time(soup):
    """
    :param soup: BeautifulSoup object
    :return tuple(str, str): date and time of web page update
    """
    # get date and time
    timestamp = soup.find(
        'p',
        attrs={'id': 'Col0PriceTime'}
    ).get_text().split()[1]
    time = timestamp[10:]
    date_raw = timestamp[:10]

    # if there is not date, set to 'NULL'
    date = re.sub(r'(\d+)/(\d+)/(\d+)', r'\3-\2-\1', date_raw)
    if date == date_raw:
        date = 'NULL'

    return time, date


def get_daily_change(soup):
    """
    :param soup: BeautifulSoup object
    :return tuple(float, float): absolute and daily value change
    """
    quote_detail = soup.find(
        'span',
        attrs={'id': 'Col0PriceDetail'}
    ).get_text()

    quote_detail_abs = string_to_float(quote_detail.split('|')[0])
    quote_detail_rel = quote_detail.split('|')[1].replace('%', '')
    quote_detail_rel = string_to_float(quote_detail_rel) / 100

    return quote_detail_abs, quote_detail_rel


def get_bid_offer(soup):
    """
    :param soup: BeautifulSoup object
    :return tuple(float, float): bid and offer on the security
    """
    bid_offer = soup.find(
        'td',
        attrs={'id': 'Col0BidOffer'}
    ).get_text().split(' - ')

    bid = string_to_float(bid_offer[0])
    offer = string_to_float(bid_offer[1])

    return bid, offer


def get_low_high(soup):
    """
    :param soup: BeautifulSoup object
    :return tuple(float, float): daily low and high of the security
    """
    lo_hi = soup.find(
        'td',
        attrs={'id': 'Col0LowHigh'}
    ).get_text().split(' - ')

    if len(lo_hi) == 2:
        low = string_to_float(lo_hi[0])
        high = string_to_float(lo_hi[1])
    else:
        low, high = 'NULL', 'NULL'

    return low, high


def get_daily_volume(soup):
    """
    :param soup: BeautifulSoup object
    :return float: daily volume traded
    """
    day_vol = soup.find('td', attrs={'id': 'Col0DayVolume'}).get_text()
    return string_to_float(day_vol)


def get_capital(soup):
    """
    :param soup: BeautifulSoup object
    :return float: capital of the company
    """
    capital_str = soup.find('td', attrs={'id': 'Col0MCap'}).get_text()
    if capital_str[-3:] == 'Mil':
        capital = string_to_float(capital_str[:-3]) * 10e6
    elif capital_str[-3:] == 'Bil':
        capital = string_to_float(capital_str[:-3]) * 10e9
    else:
        capital = string_to_float(capital_str)

    return capital


def get_closing_value(soup):
    """
    :param soup: BeautifulSoup object
    :return float: closing value of the security
    """
    last_close = soup.find('td', attrs={'id': 'Col0LastClose'}).get_text()
    return string_to_float(last_close)


def get_PE_ratio(soup):
    """
    :param soup: BeautifulSoup object
    :return float: P/E ratio of the security
    """
    p_e = soup.find('td', attrs={'id': 'Col0PE'}).get_text()
    return string_to_float(p_e)


def get_yield(soup):
    """
    :param soup: BeautifulSoup object
    :return float: yield of the security, in percent
    """
    y = soup.find('td', attrs={'id': 'Col0Yield'}).get_text()
    y = string_to_float(y)
    return y / 100


def parse_webpage(page_contents, collection_date):
    """
    Parse the text of the HTML page.

    :param str page_contents: HTML code of the web page
    :param str collection_date: date when data was collected
    :return dict: dictionary where keys are stock attributes and values are
                  the corresponding values parsed from the HTML
    """
    results = {'collection_date': collection_date}

    # parse each relevant element of the web page, one at a time and put
    # them in a dictionary
    soup = BeautifulSoup(page_contents, 'html.parser')

    results['company_name'] = get_company_name(soup)

    results['last_quote'] = get_last_quote(soup)

    results['time'], results['date'] = get_date_time(soup)

    absolute, relative = get_daily_change(soup)
    results['daily_change_abs'] = absolute
    results['daily_change_rel'] = relative

    results['bid'], results['offer'] = get_bid_offer(soup)

    results['low'], results['high'] = get_low_high(soup)

    results['day_volume'] = get_daily_volume(soup)

    results['capital'] = get_capital(soup)

    results['last_close'] = get_closing_value(soup)

    results['p_e'] = get_PE_ratio(soup)

    results['yield_percent'] = get_yield(soup)

    # convert all NaN to 'NULL'
    results = to_null(results)

    return results
