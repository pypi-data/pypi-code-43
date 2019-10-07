def getfirst(*args):
    """Returns first non-None argument or None if none is found.
    Now say it fast 10 times :)"""
    return next((x for x in args if x is not None), None)

