from urllib.parse import urlparse, parse_qs

UTM_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_referrer']


def parse_utm(url: str) -> dict:
    """
    return utms dict
    :param url: str
    :return: dict
    """
    out = {}
    try:
        url_params = parse_qs(urlparse(url.replace('#', '')).query)
        for utm in UTM_PARAMS:
            if utm in url_params:
                out[utm] = url_params[utm][0]
        return out
    except (KeyError, ValueError, IndexError, TypeError):
        return {}
