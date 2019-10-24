marker_styles = [
    ".",
    ",",
    "o",
    "v",
    "^",
    "<",
    ">",
    "1",
    "2",
    "3",
    "4",
    "s",
    "p",
    "*",
]


def mkbox(i):
    """
    Cycles through marker styles based on index

    :param i: int, index for marker
    :return:
    """
    indy = i % len(marker_styles)
    return marker_styles[indy]
