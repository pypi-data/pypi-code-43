from builtins import map
from builtins import range
from .grow import grow
from .base_utils import wilt
from .lilyblock import block
from .borders import border_char


def bordered(s, bordercolor="", borderstyle="thin"):
    blc = block(s)
    horiz_char = border_char("lr", borderstyle)
    horiz = horiz_char * blc.width()
    horiz = grow(horiz, bordercolor)
    top = block(horiz)
    partial = top.append(blc).append(horiz)
    top_left = _brderchar("br", bordercolor, borderstyle)
    top_right = _brderchar("bl", bordercolor, borderstyle)
    bot_left = _brderchar("tr", bordercolor, borderstyle)
    bot_right = _brderchar("tl", bordercolor, borderstyle)
    vert = _brderchar("tb", bordercolor, borderstyle)
    vert = [vert] * blc.height()
    l_vert = block([top_left] + vert + [bot_left])
    r_vert = block([top_right] + vert + [bot_right])
    return l_vert + partial + r_vert


def _brderchar(vector, color, style):
    ch = border_char(vector, style)
    return grow(ch, color)


def sortify(iter, case_insensitive=True):
    if case_insensitive:

        def sortkey(s):
            return wilt(s).lower()

    else:
        sortkey = wilt
    return sorted(list(iter), key=sortkey)


def columnify(
    iter,
    cols=0,
    width=80,
    justify="left",
    sort=True,
    spacing=3,
    left_to_right=False,
):
    iter = list(map(grow, iter))
    if sort:
        iter = sortify(iter)

    if cols == 0:
        cols = width // (max(list(map(len, iter))) + spacing)
        cols = min(len(iter), cols)
        if cols == 0:
            cols = 1
    if cols == 0:
        cols = 1
    colsize = width // cols

    # Trim a bit more off of the string to adjust for the whitespace in the col
    resized = _resize_all(iter, colsize - spacing, justify)

    # Technically this is only the count for the leftmost column, so its a max.
    entries_per_column, remainder = divmod(len(iter), cols)
    if remainder > 0:
        entries_per_column += 1

    groups = []
    if left_to_right:
        # items populate left to right, then wrap to next row
        for i in range(entries_per_column):
            start = cols * i
            stop = start + cols
            groups.append(resized[start:stop])
    else:
        # items populate top to bottom, then wrap to next column
        # min is used here to avoid empty groups
        for i in range(entries_per_column):
            groups.append(resized[i::entries_per_column])

    output = ""
    for group in groups:
        s = group[0]
        for q in group[1:]:
            s += grow(" " * spacing)
            s += q
        output += s + "\n"
    return output


def _resize_all(iter, size, justify):
    return [
        s.resize(size, justify, add_elipsis=True, fillchar=" ") for s in iter
    ]
