from __future__ import print_function
import logging
from mcutk.board import Board


class BoardUnion(object):
    """BoardUnion: unite boards to a group.

    Boards are involved in a group, each board has an alias.
    BoardUnion make the boards relationship more clearly.

    """
    def __init__(self, boards=None, id=None, name="union",  **kwargs):
        """Create a BoardUnion instance.

        Arguments:
            boards {list or dict} -- create a unio by  list of boards or a boards dict.
            id {string} -- union id, default: None
            name {string} -- the name of this union, default: union
        """
        self.id = id
        self.name = name
        self._boards = dict()

        if isinstance(boards, list):
            for bd in boards:
                self.add_board(bd)
        elif isinstance(boards, dict):
            for name, bd in boards.items():
                self.add_board(bd, name)
        else:
            ValueError("require list or dict.")
        for name, value in kwargs.items():
            setattr(self, name, value)


    def add_board(self, board, alias=None):
        """Add a board to this union

        Arguments:
            board {Board object} -- mcutk.board.Board object

        Keyword Arguments:
            alias {string} -- alias name in union (default: {None}),
                if is None, alias default will use Board.devicename

        Raises:
            ValueError -- raise When alias already in union.
        """

        assert isinstance(board, Board)

        if not alias:
            alias = board.devicename

        if alias in self._boards:
            raise ValueError("duplicate alias name in boardunion")

        self._boards[alias] = board
        setattr(self, alias, board)
        board.register_resource(self, "board_union")


    def remove_board(self, name):
        """remove a board

        Arguments:
            name {string} -- alias in union

        Raises:
            ValueError -- raise when name not in unio.
        """
        try:
            self._boards[name].remove_resource(self)
            del self._boards[name]
            delattr(self, name)
        except KeyError:
            raise ValueError("name is not in this union")


    def check_status(self):
        """Check boards status.
        """
        for bd in self._boards:
            status = bd.check_serial()
            print(bd.name + " " + status)
            if status != "pass":
                return status
        else:
            return "pass"

