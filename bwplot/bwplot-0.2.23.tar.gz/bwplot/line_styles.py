line_style = "-"
line_styles = ["-", "--", "-.", ":"]


def lsbox(i):
    """
    Cycles through line styles based on index

    :param i: int, index
    :return:
    """
    indy = i % len(line_styles)
    return line_styles[indy]