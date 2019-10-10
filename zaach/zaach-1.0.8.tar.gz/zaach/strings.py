def lcut(s, sub):
    """
    Cuts off the substring `sub` if string `s` starts with it.
    """
    len_sub = len(sub)
    if s[:len_sub] == sub:
        return s[len_sub:]
    return s


def rcut(s, sub):
    """
    Cuts off the substring `sub` if string `s` ends with it.
    """
    len_sub = len(sub)
    if s[-len_sub:] == sub:
        return s[:-len_sub]
    return s


def cut(s, sub):
    """
    Cuts off the substring `sub` from the start and end of string `s`.
    """
    return rcut(lcut(s, sub), sub)
