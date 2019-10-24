from inspect import signature
from collections import namedtuple
from inspect import stack

def dictToNamedTuple(d: dict, name: str):
    return namedtuple(name, d.keys())(**d)

def makeCompleteArgumentDict(func, args, kwargs):
    s = signature(func)
    p = s.parameters
    build = {}
    for a, b in zip(args, p.keys()):
        build[b] = a
    for k, v in p.items():
        if v.default:
            if k not in build:
                build[k] = v.default
    for k, v in kwargs.items():
        build[k] = v

    return build

def makeFileLocationString(filename: str, lineNum):
    return f'File "{filename}", line {lineNum}'

def getCallerData():
    #third element because it gets the caller's caller's info
    return stack()[2]

def preserveValues(preservers, Args):
    preserved = {}
    for preserver in preservers:
        preserved.update(preserver(Args))
    return preserved