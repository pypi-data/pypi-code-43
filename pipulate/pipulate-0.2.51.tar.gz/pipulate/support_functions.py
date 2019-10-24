def api_date(a_datetime, time=False):
    """Return datetime string in Google API friendly format."""
    if time:
        return ('{0:%Y-%m-%d %H:%M:%S}'.format(a_datetime))
    else:
        return ('{0:%Y-%m-%d}'.format(a_datetime))


def human_date(a_datetime, time=False):
    """Return datetime object as American-friendly string."""
    if time:
        return ('{0:%m/%d/%Y %H:%M:%S}'.format(a_datetime))
    else:
        return ('{0:%m/%d/%Y}'.format(a_datetime))


def date_ranges(human=False, yoy=True):
    """Return a list of 3 commonly used daterange tuples."""

    def dx(x):
        return api_date(x)

    def dh(x):
        return human_date(x)

    lot = list()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    thirty_days_ago = yesterday - timedelta(days=30)
    prior_30_end = thirty_days_ago - timedelta(days=1)
    prior_30_start = prior_30_end - timedelta(days=30)
    if yoy:
        last_range_end = yesterday.replace(year=yesterday.year - 1)
        last_range_start = thirty_days_ago.replace(year=thirty_days_ago.year - 1)
    else:
        last_range_end = thirty_days_ago - timedelta(days=32)
        last_range_start = prior_30_end - timedelta(days=60)
    if human:
        lot.append((dh(thirty_days_ago), dh(yesterday)))
        lot.append((dh(prior_30_start), dh(prior_30_end)))
        lot.append((dh(last_range_start), dh(last_range_end)))
        lot = [(x + ' - ' + y) for x, y in lot]
    else:
        lot.append((dx(thirty_days_ago), dx(yesterday)))
        lot.append((dx(prior_30_start), dx(prior_30_end)))
        lot.append((dx(last_range_start), dx(last_range_end)))
    return lot


def date_ranger(starts=(30, 90, 180), days=30, start=1, human=False):
    """Returns 3 date ranges from days-ago starts to days-later."""

    def dx(x):
        return api_date(x)

    def dh(x):
        return human_date(x)

    lot = list()
    today = datetime.now()
    yesterday = today - timedelta(days=start)
    firstrange_start = yesterday - timedelta(days=starts[0])
    firstrange_end = firstrange_start + timedelta(days=days)
    midrange_start = yesterday - timedelta(days=starts[1])
    midrange_end = midrange_start + timedelta(days=days)
    lastrange_start = yesterday - timedelta(days=starts[2])
    lastrange_end = lastrange_start + timedelta(days=days)
    if human:
        lot.append((dh(firstrange_start), dh(firstrange_end)))
        lot.append((dh(midrange_start), dh(midrange_end)))
        lot.append((dh(lastrange_start), dh(lastrange_end)))
        lot = [(x + ' - ' + y) for x, y in lot]
    else:
        lot.append((dx(firstrange_start), dx(firstrange_end)))
        lot.append((dx(midrange_start), dx(midrange_end)))
        lot.append((dx(lastrange_start), dx(lastrange_end)))
    return lot


def gmt():
    """Returns current time in Greenwich Mean Time"""
    from time import gmtime, strftime
    return strftime("%a, %d %b %Y %H:%M", gmtime())


def timestamp():
    """Returns local time formatted for timestamp."""
    return '{0:%a, %b %d ~%I:%m %p} GMT'.format(datetime.now(pytz.utc))


def ga_url(gaid, start, end, path):
    """Return Google Analytics metrics for a URL."""

    path = path.replace(',', r'\,')
    service = ga()
    metrics = ['users', 'newUsers', 'sessions', 'bounceRate',
               'pageviewsPerSession', 'avgSessionDuration']
    metrics = ''.join(['ga:%s,' % x for x in metrics])[:-1]
    ga_request = service.data().ga().get(
        ids='ga:' + gaid,
        start_date=start,
        end_date=end,
        metrics=metrics,
        dimensions='ga:pagePath',
        sort='-ga:users',
        filters='ga:pagePath==' + path,
        segment='sessions::condition::ga:medium==organic',
        max_results=1
    )
    ga_response = ga_request.execute()
    rval = []
    if 'rows' in ga_response:
        raw_rows = ga_response['rows'][0]
        rval = raw_rows
    return rval


def gsc_url_keyword(prop, start, end, query, url):
    service = gsc()
    request = {
        "startDate": start,
        "endDate": end,
        "dimensions": [
            "query",
            "page"],
        "dimensionFilterGroups": [
        {
            "filters": [
            {
                "operator": "equals",
                "expression": url,
                "dimension": "page"
            },
            {
                "operator": "equals",
                "expression": query,
                "dimension": "query"
            }]
        }]
    }
    dat = service.searchanalytics().query(siteUrl=prop, body=request).execute()
    val = []
    if 'rows' in dat:  # For the foolish Hobgoblins of PEP8 consistency
        r = dat['rows'][0]
        val = [start] + [r['keys'][0]] + [r['keys'][1]] + [
            r['position']] + [r['clicks']] + [r['impressions']] + [r['ctr']]
    return val


def h1(print_me, color=Fore.GREEN, font='standard'):
    ''' Never underestimate the power of a good nickname. '''
    ascii_art = figlet_format(print_me, font=font)
    print('%s%s%s' % (color, ascii_art, Fore.WHITE))
    return print_me


def h2(print_me, color=Fore.GREEN, font='cybermedium'):
    ''' The human brain generally only deals well with shallow nesting. '''
    ascii_art = figlet_format(print_me, font=font)
    print()
    print('%s%s%s' % (color, ascii_art, Fore.WHITE))
    return print_me
