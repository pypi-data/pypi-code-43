from urllib.parse import urlparse, urlunparse, parse_qs
from easilyb import urlnorm as un
import logging
logger = logging.getLogger(__name__)


class UrlSelector:
    def __init__(self):
        self.seen = set()
        self.notseen = set()

    def put(self, url):
        item = UrlItem(url)
        # check duplicates
        if item in self.seen or item in self.notseen:
            return
        self.notseen.add(item)

    def pop(self):
        if len(self.notseen) == 0:  # if not seen is empty
            return None
        if len(self.seen) == 0:  # if seen is empty (pick arbitrary element)
            for curitem in self.notseen:
                break
            self.notseen.remove(curitem)
            self.seen.add(curitem)
            return curitem.url_original

        curitem = None
        curdist = -1
        for n in self.notseen:
            sdist = -1
            for s in self.seen:
                dist = s.dist(n)
                if sdist == -1 or dist < sdist:
                    sdist = dist
            if sdist > curdist:
                curdist = sdist
                curitem = n

        self.notseen.remove(curitem)
        self.seen.add(curitem)
        return curitem.url_original

    def __len__(self):
        return len(self.notseen)


class UrlItem:
    def __init__(self, url):
        self.url_norm = un.norm_ex1(urlparse(url))
        self.url = urlunparse(self.url_norm[:-4] + ('',))
        try:
            self.url_unicode = self.url.decode('utf8')
        except AttributeError:
            self.url_unicode = self.url
        self.url_original = url
        self.host = self.url_norm[-2]
        self.distances = dict()

    def set_distance(self, item, dist):
        self.distances[item.url] = dist

    def get_distance(self, item):
        if item.url in self.distances:
            return self.distances[item.url]
        else:
            raise KeyError('UrlItem key does not exist: ' + str(item))

    def dist(self, item):
        if item.url in self.distances:
            return self.distances[item.url]
        dist = url_distance(self.url_norm, item.url_norm)
        self.set_distance(item, dist)
        item.set_distance(self, dist)
        return dist

    def __str__(self):
        return "UrlItem(%s)" % (self.url)

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)


def url_distance(url1, url2):
    scheme1, authority1, path1, parameters1, query1, fragment1, userinfo1, host1, port1 = url1
    scheme2, authority2, path2, parameters2, query2, fragment2, userinfo2, host2, port2 = url2
    sdiff = servicediff(scheme1, authority1, host1, scheme2, authority2, host2)
    if sdiff > 0:
        return sdiff * 50
    pdiff = pathdiff(path1, path2)
    if pdiff > 0:
        return pdiff * 2
    return querrydiff(query1, query2)


def servicediff(scheme1, authority1, host1, scheme2, authority2, host2):
    if scheme1 + authority1 == scheme2 + authority2:
        return 0
    if host1 == host2:
        return 10
    return min(20, edit_dist(host1, host2)) + 10


def pathdiff(path1, path2):
    if path1 == path2: return 0
    return edit_dist(path1, path2)


def querrydiff(query1, query2):
    dict1 = parse_qs(query1)
    dict2 = parse_qs(query2)
    diff = 0
    for k in dict1:
        if k not in dict2:
            diff += 10
        else:
            diff += edit_dist(','.join(dict1[k]), ','.join(dict2[k]))
            del dict2[k]
    diff += 10 * len(dict2)
    return diff


def edit_dist(str1, str2):
    l1 = len(str1) + 1
    l2 = len(str2) + 1
    arr = {}

    for i in range(l1): arr[i, 0] = i
    for j in range(l2): arr[0, j] = j
    for i in range(1, l1):
        for j in range(1, l2):
            c = 0 if str1[i - 1] == str2[j - 1] else 1
            arr[i, j] = min(arr[i, j - 1] + 1, arr[i - 1, j] + 1, arr[i - 1, j - 1] + c)

    return arr[i, j]
