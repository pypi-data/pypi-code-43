import os
import json
import requests


def hump(s):
    a = [i for i in uline(s).split('_') if len(i) > 0]
    return a[0].lower() + ''.join(i.capitalize() for i in a[1:])


def uline(s):
    b = ''
    a = str(s)
    for i, v in enumerate(a):
        b += '_' + v if v.isupper() and a[i - 1].islower() else v
    return '_'.join([i.lower() for i in b.split('_') if len(i) > 0])


def llist(d, sep=' '):
    return [i.split(sep) for i in d.split('\n') if len(i) > 0]


def home(a='', *b):
    return os.path.join(os.path.expanduser("~"), a, *b).rstrip('\\')


def desktop(a='', *b):
    return home('Desktop', a, *b)


def mkdir(path):
    if os.path.exists(path):
        print(f'{path} exists! continue.')
        return
    os.makedirs(path.strip().rstrip("\\"))
    print(f'{path} created.')


def rmdir(path):
    if os.path.exists(path):
        os.removedirs(path)
        print(f'{path} deleted.')


def fread(f, encoding='utf-8'):
    if os.path.isfile(f):
        with open(f, 'r', encoding=encoding) as fd:
            return fd.read()


def fwrite(f, d, encoding='utf-8'):
    with open(f, 'w', encoding=encoding) as fd:
        fd.write(d)


def flist(f, sep=' ', encoding='utf-8'):
    return llist(fread(f, encoding), sep)


def get(url, headers=None):
    res = requests.get(url, headers=headers)
    return res.text


def post(url, headers=None):
    headers = headers or {'content-type': 'application/json;charset=utf-8'}
    data = msg if isinstance(msg, str) else tojson(msg)
    res = requests.post(url, data=data, headers=headers)
    return res.text


def tojson(msg):
    return json.dumps(msg, ensure_ascii=False)


def fromjson(msg):
    return json.loads(msg)
