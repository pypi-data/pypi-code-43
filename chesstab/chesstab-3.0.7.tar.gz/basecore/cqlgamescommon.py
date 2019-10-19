# cqlgamescommon.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Evaluate a ChessQL query.

Methods and functions which are independent of database interface.

"""
from ast import literal_eval

from solentware_base.api.where import (
    EQ,
    OR,
    NOT,
    )

from chessql.core import constants
from chessql.core.constants import (
    ALL_GAMES_MATCH_PIECE_DESIGNATORS,
    ANY_WHITE_PIECE_NAME,
    ANY_BLACK_PIECE_NAME,
    ALL_PIECES,
    WHITE_PIECE_NAMES,
    BLACK_PIECE_NAMES,
    )

from pgn_read.core.constants import (
    MAP_PGN_SQUARE_NAME_TO_FEN_ORDER,
    MOVE_NUMBER_KEYS,
    WKING,
    )

from ..core.filespec import (
    PIECESQUAREMOVE_FIELD_DEF,
    PIECEMOVE_FIELD_DEF,
    SQUAREMOVE_FIELD_DEF,
    )

AND_FILTERS = frozenset((constants.LEFT_BRACE_FILTER,
                         'cql',
                         ))
OR_FILTERS = frozenset((constants.OR,
                        constants.FLIP,
                        constants.FLIPDIHEDRAL,
                        constants.FLIPHORIZONTAL,
                        constants.FLIPVERTICAL,
                        constants.FLIPCOLOR,
                        constants.NEXT_STAR,
                        constants.PREVIOUS_STAR,
                        constants.ROTATE45,
                        constants.ROTATE90,
                        constants.SHIFT,
                        constants.SHIFTHORIZONTAL,
                        constants.SHIFTVERTICAL,
                        ))
_filters = {constants.PIECE_DESIGNATOR_FILTER,
            constants.ON,
            constants.RAY,
            }
_SUPPORTED_FILTERS = frozenset(AND_FILTERS.union(OR_FILTERS.union(_filters)))
del _filters


class ChessQLGamesError(Exception):
    pass


class ChessQLGamesCommon:
    
    """Collection of methods which are database interface independent.

    Use this class like:
    C(subclass<solentware_grid.core.dataclient.DataSource>, ChessQLGamesCommon)

    """
        
    def pieces_matching_filter(self, filter_, initialpieces):
        """Return squares matching filters in CQL statement.

        It is assumed FSNode.designator_set contains the expanded piece
        designators.

        """
        if filter_.type in AND_FILTERS:
            pieces = set(initialpieces)
            for n in filter_.children:
                if n.type == constants.PIECE_DESIGNATOR_FILTER:
                    pieces.intersection_update(
                        self.pieces_matching_piece_designator(n))
                    if not pieces:
                        return pieces
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                pieces.intersection_update(
                    self.pieces_matching_filter(n, pieces))
                if not pieces:
                    return pieces
            return pieces
        elif filter_.type in OR_FILTERS:
            pieces = set(ALL_PIECES)
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                pieces.union(
                    self.pieces_matching_filter(n, initialpieces))
            return pieces
        else:
            if filter_.type == constants.PIECE_DESIGNATOR_FILTER:
                return self.pieces_matching_piece_designator(filter_)
            if filter_.type == constants.ON:
                return self.pieces_matching_on_filter(filter_)
            return initialpieces
        
    def squares_matching_filter(self, filter_, initialsquares):
        """Return squares matching filters in CQL statement.

        It is assumed FSNode.designator_set contains the expanded piece
        designators.

        """
        if filter_.type in AND_FILTERS:
            squares = set(initialsquares)
            for n in filter_.children:
                if n.type == constants.PIECE_DESIGNATOR_FILTER:
                    squares.intersection_update(
                        self.squares_matching_piece_designator(n))
                    if not squares:
                        return squares
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                squares.intersection_update(
                    self.squares_matching_filter(n, squares))
                if not squares:
                    return squares
            return squares
        elif filter_.type in OR_FILTERS:
            squares = set(MAP_PGN_SQUARE_NAME_TO_FEN_ORDER)
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                squares.union(
                    self.squares_matching_filter(n, initialsquares))
            return squares
        else:
            if filter_.type == constants.PIECE_DESIGNATOR_FILTER:
                return self.squares_matching_piece_designator(filter_)
            if filter_.type == constants.ON:
                return self.squares_matching_on_filter(filter_)
            return initialsquares
        
    def pieces_matching_piece_designator(self, filter_):
        """Return pieces matching a piece designator."""

        if filter_.type != constants.PIECE_DESIGNATOR_FILTER:
            raise ChessQLGamesError(''.join(("'",
                                             constants.PIECE_DESIGNATOR_FILTER,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        pieces = set()
        for ps in filter_.data.designator_set:
            p = ps[0]
            if p == ANY_WHITE_PIECE_NAME:
                pieces.update(WHITE_PIECE_NAMES)
            elif p == ANY_BLACK_PIECE_NAME:
                pieces.update(BLACK_PIECE_NAMES)
            else:
                pieces.add(p)
        return pieces
        
    def squares_matching_piece_designator(self, filter_):
        """Return squares matching a piece designator."""

        if filter_.type != constants.PIECE_DESIGNATOR_FILTER:
            raise ChessQLGamesError(''.join(("'",
                                             constants.PIECE_DESIGNATOR_FILTER,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        squares = set()
        for ps in filter_.data.designator_set:
            if len(ps) == 1:
                squares.update(MAP_PGN_SQUARE_NAME_TO_FEN_ORDER)
            else:
                squares.add(ps[1:])
        return squares
        
    def pieces_matching_on_filter(self, filter_):
        """Return pieces matching an on filter."""

        if filter_.type != constants.ON:
            raise ChessQLGamesError(''.join(("'",
                                             constants.ON,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        left = self.pieces_matching_filter(
            filter_.children[0],
            set(ALL_PIECES))
        right = self.pieces_matching_filter(
            filter_.children[1],
            set(ALL_PIECES))
        return left.intersection(right)
        
    def squares_matching_on_filter(self, filter_):
        """Return squares matching an on filter."""

        if filter_.type != constants.ON:
            raise ChessQLGamesError(''.join(("'",
                                             constants.ON,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        left = self.squares_matching_filter(
            filter_.children[0],
            set(MAP_PGN_SQUARE_NAME_TO_FEN_ORDER))
        right = self.squares_matching_filter(
            filter_.children[1],
            set(MAP_PGN_SQUARE_NAME_TO_FEN_ORDER))
        return left.intersection(right)

    # Incomprehensible!!!
    def is_filter_implemented(self, filter_):
        if filter_.type == constants.PLAIN_FILTER:
            self.not_implemented.add(filter_.leaf)
            return True
        elif filter_.type not in _SUPPORTED_FILTERS:
            self.not_implemented.add(filter_.type)
            return True
        return False


def where_eq_piece_designator(move_number, variation_code, designator_set):
    """.

    The fieldname PieceSquareMove is now unavoidably a bit confusing, where
    move refers to a token in the movetext when the piece is on the square.
    Nothing to do with move number in the movetext, which is the ChessQL
    meaning of move in this context.

    """
    anypiece = ANY_WHITE_PIECE_NAME + ANY_BLACK_PIECE_NAME
    psmfield = PIECESQUAREMOVE_FIELD_DEF
    pmfield = PIECEMOVE_FIELD_DEF
    smfield = SQUAREMOVE_FIELD_DEF
    mns = move_number_str(move_number)
    psmds = set()
    pmds = set()
    emptyds = set()
    smds = set()
    for ps in designator_set:
        if len(ps) == 1:

            # Rules of chess imply whole piece designator finds all games if
            # any of 'A', 'a', 'K', 'k', and '.', are in designator set.
            if ps[0] in ALL_GAMES_MATCH_PIECE_DESIGNATORS:
                return ' '.join(
                    (pmfield, EQ, ''.join((mns, variation_code, WKING))))
            
            pmds.add(''.join((mns, variation_code, ps[0])))
            continue
        if ps[0] == constants.EMPTY_SQUARE_NAME:
            sq = ps[1:]
            emptyds.add(' '.join(
                (NOT,
                 psmfield,
                 EQ,
                 ''.join((mns, variation_code, sq + ANY_WHITE_PIECE_NAME)),
                 OR,
                 ''.join((mns, variation_code, sq + ANY_BLACK_PIECE_NAME)),
                 )))
            continue
        if ps[0] in anypiece:
            smds.add(''.join(
                (mns,
                 variation_code,
                 ps[1:] + ps[0],
                 )))
            continue
        psmds.add(''.join(
            (mns,
             variation_code,
             ps[1:] + ps[0],
             )))

    phrases = []
    if psmds:
        phrases.append(' '.join((psmfield, EQ, OR.join('  ').join(psmds))))
    if pmds:
        phrases.append(' '.join((pmfield, EQ, OR.join('  ').join(pmds))))
    if smds:
        phrases.append(' '.join((smfield, EQ, OR.join('  ').join(smds))))
    if emptyds:
        phrases.append(OR.join('  ').join(emptyds))
    if phrases:
        return OR.join('  ').join(phrases)


def move_number_str(move_number):
    """"""
    # Adapted from module pgn_read.core.parser method add_move_to_game().
    try:
        return MOVE_NUMBER_KEYS[move_number]
    except IndexError:
        c = hex(move_number)
        return str(len(c)-2) + c[2:]


def move_number_in_key_range(key):
    """Yield the move number keys in a range one-by-one."""
    for n in range(1, literal_eval('0x' + key[1:int(key[0]) + 1])):
        yield n
