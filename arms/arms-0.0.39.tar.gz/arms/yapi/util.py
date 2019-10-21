import re


def prefix(lines, f):
    for line in lines:
        tmp = f(line)
        if tmp:
            yield tmp
        else:
            break


def extract_include(line):
    if not line: return None
    if line.startswith('`:include ') and line[-1] == '`':
        return line[1:-1].split(':include', 1)[-1].strip()
    else:
        return None


def lined_group(lines, starter, ender):
    def get(p):
        return lines[p] if p < len(lines) else None

    def single_group(p):
        next = ''
        isGrouping = False
        first = last = None
        for i in range(p, len(lines) + 1):
            prev, next = next, get(i)
            if not isGrouping and starter(prev, next):
                first, isGrouping = i, True
            elif isGrouping and ender(prev, next):
                last = i
                return (first, last)
        return (first, last)

    i = 0
    while True:
        first, last = single_group(i)
        if first is None or last is None:
            break
        yield lines[first:last]
        i = last


def mdtitle_level(line):
    """
    >>> mdtitle_level("#### hehe")
    4
    >>> mdtitle_level("#haha")
    1
    >>> mdtitle_level(".#haha")
    0
    """
    segs = re.findall("^#+", line)
    return len(segs[0]) if segs else 0


def big_mdtitle_group(lines):
    for group in lined_group(
            lines,
            lambda _, next: next is not None and mdtitle_level(next) == 1,
            lambda _, next: next is None or mdtitle_level(next) == 1):
        yield group


def small_mdtitle_group(lines):
    for group in lined_group(
            lines,
            lambda _, next: next is not None and mdtitle_level(next) >= 2,
            lambda _, next: next is None or mdtitle_level(next) >= 2):
        yield group


def mdyaml_group(lines):
    for group in lined_group(
            lines,
            lambda _, next: next is not None and next == '```yaml',
            lambda prev, next: next is None or prev == '```'):
        yield group


def pathparam_names(path):
    """
    >>> pathparam_names("/school/{schoolId}")
    ['schoolId']
    >>> pathparam_names("/{school}/{schoolId}")
    ['school', 'schoolId']
    >>> pathparam_names("/schools")
    []
    """
    return re.findall(r'\{([^/]+)\}', path)


def merge_dicts(dicts):
    """
    >>> merge_dicts([{'a':1, 'b':2}, {'c':3, 'b':4}])
    {'a': 1, 'b': 4, 'c': 3}
    """
    ret = {}
    for d in dicts:
        ret.update(d)
    return ret


def list_find(arr, f):
    for i, item in enumerate(arr):
        if f(item):
            return i
    return -1


def is_comment_format(value):
    """
    >>> is_comment_format("+int = 1 //数量")
    True
    >>> is_comment_format("abcde #hehe")
    False
    """
    if not isinstance(value, str) or '//' not in value:
        return False
    head = value.rsplit('//', 1)[0]
    if '=' not in head:
        return False
    pytype, sample = head.split('=', 1)
    if not sample.strip():
        return False
    return all(ord(c) < 128 for c in pytype.strip())


def parse_comment(value):
    """
    >>> parse_comment("+int = 1 //数量")
    ('+int', '1', '数量', '')
    >>> parse_comment('str ="abc"// 文本 #A')
    ('str', '"abc"', '文本', 'A')
    >>> parse_comment('int = 22 //hehe')
    ('int', '22', 'hehe', '')
    >>> parse_comment('str(50) =\"22\"//hehe')
    ('str(50)', '"22"', 'hehe', '')
    >>> parse_comment('  int=2 //#')
    ('int', '2', '', '')
    """
    assert is_comment_format(value), "invalid value: " + str(value)
    head, tail = value.rsplit('//', 1)
    pytype, sample = head.split('=', 1)
    comment, tag = tail.split('#', 1) if '#' in tail else (tail, '')
    return pytype.strip(), sample.strip(), comment.strip(), tag.strip()
