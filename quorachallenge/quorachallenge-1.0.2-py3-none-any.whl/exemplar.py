def func(a,b):
    if a < 0 and b < 0:
        raise ValueError
    if a < 0 or b < 0:
        return 0
    if a == 0 and b == 0:
        return 1
    if a == 0 or b == 0:
        return 0
    return a + b