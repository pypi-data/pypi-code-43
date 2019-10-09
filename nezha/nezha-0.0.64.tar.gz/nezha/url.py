from collections import OrderedDict
from typing import Union, Dict, Any,Mapping
from urllib import parse
from warnings import warn


def urljoin(base: str, url: str = '', params: Union[str, Mapping] = '') -> str:
    return '?'.join((parse.urljoin(base, url), parse.urlencode(params))).rstrip('?')


def urlencode(data: Dict[str, Any], safe: bool = True, sorted_by_ascii: bool = False) -> str:
    warn("deprecated", DeprecationWarning)
    if safe:
        return parse.urlencode(data)
    else:
        may_sorted = data.copy()
        if sorted_by_ascii:
            may_sorted = OrderedDict()
            for k in sorted(data):
                may_sorted[k] = data[k]
        return "&".join((f'{k}={v}' for k, v in may_sorted.items()))


if __name__ == '__main__':
    print(urljoin('http://ww.sx/s/'))
