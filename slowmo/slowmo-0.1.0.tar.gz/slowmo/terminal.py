from typing import Tuple

from blessed import Terminal


def location(t: Terminal) -> Tuple[int, int]:
    """Get cursor location as 0-indexed (row, column).

    See https://github.com/jquast/blessed/issues/94#issuecomment-286553209
    """
    row, col = t.get_location()
    return row - 1, col - 1


def move_row(t: Terminal, row: int) -> str:
    """

    `blessed.Terminal.move` is 0-indexed
    `blessed.Terminal.move_x` is 1-indexed
    See
    """
    return t.move(row, 0)
