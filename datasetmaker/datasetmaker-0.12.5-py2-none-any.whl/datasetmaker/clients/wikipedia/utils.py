import datetime
import requests


_api_url = 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions'
_wp_url = 'https://en.wikipedia.org/w/index.php'


def _create_ts(time_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')


def get_latest_revisions(title: str, limit: int = 2) -> list:
    """
    Gets the latest revisions with timestamps of a Wikipedia article.

    Parameters
    ----------
    title : str
        WikiMedia title of the article.
    limit : int
        Latest n revisions to get.
    """
    params = {'titles': title, 'rvlimit': limit, 'format': 'json'}
    r = requests.get(_api_url, params)  # type: ignore
    data = r.json()['query']['pages']
    key = list(data.keys())[0]
    ts = data[key]['revisions']
    return [{'revid': x['revid'], 'timestamp': _create_ts(x['timestamp'])} for x in ts]


def get_stable_page_url(title: str, minutes_stable: int) -> str:
    """
    Get a versioned page URL based on the number of minutes since the last edit.
    The idea is to avoid vandal edits by requiring a certain amount of time to
    have passed since the last revision of the page.

    TODO: This does not handle "edit wars" with lots of edits in a short time span.

    Parameters
    ----------
    title : str
        WikiMedia title of the article.
    minutes_stable : int
        The minimum number of minutes to have passed since the last revision.
    """
    revs = get_latest_revisions(title=title, limit=2)
    delta = datetime.datetime.utcnow() - revs[0]['timestamp']
    diff = int((delta).seconds / 60)
    if diff <= minutes_stable:
        oldid = revs[1]['revid']
        return f'{_wp_url}?title={title}&oldid={oldid}'
    oldid = revs[0]['revid']
    return f'{_wp_url}?title={title}&oldid={oldid}'
