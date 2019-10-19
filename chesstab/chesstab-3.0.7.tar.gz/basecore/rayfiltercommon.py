# rayfiltercommon.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess Query Language (ChessQL) ray filter evaluator.

Examples of ray filters are 'ray ( Q n k )' and 'ray ( Q[a4,c3] n kh1-8 )'.

RayFilter expands the list of square descriptions into the particular rays,
horizontal, vertical, and diagonal, which need to be evaluated.

pgn_read.core.constants.GAPS provides the lists of squares between pairs of
squares from which the rays are calculated.

"""
#import pgn_read.core.constants

from chessql.core import constants
from chessql.core import piecedesignator

from ..core import filespec
from .cqlgamescommon import move_number_str

# Longest line is eight squares.  Two end points give a maximum of six internal
# squares.  Shorter lines drop elements from the right.  May add a seventh zero
# element to avoid a len() < 8 test to work around an index error exception.
# ray ( Q n b r ) for lines of length five uses MAP_RAY_TO_LINE[2][:][:3] where
# the [:3] part contains two non-zero elements.  These are the lines with one
# empty internal square.
# Non-zero elements in MAP_RAY_TO_LINE[n][m] are the internal piece designator
# in the ray.
MAP_RAY_TO_LINE = [
    [[0, 0, 0, 0, 0, 0]], # ray ( a A )
    [[1, 0, 0, 0, 0, 0],  # ray ( a A K )
     [0, 1, 0, 0, 0, 0],
     [0, 0, 1, 0, 0, 0],
     [0, 0, 0, 1, 0, 0],
     [0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 1]],
    [[1, 2, 0, 0, 0, 0],  # ray ( a Q b K )
     [1, 0, 2, 0, 0, 0],
     [0, 1, 2, 0, 0, 0],
     [1, 0, 0, 2, 0, 0],
     [0, 1, 0, 2, 0, 0],
     [0, 0, 1, 2, 0, 0],
     [1, 0, 0, 0, 2, 0],
     [0, 1, 0, 0, 2, 0],
     [0, 0, 1, 0, 2, 0],
     [0, 0, 0, 1, 2, 0],
     [1, 0, 0, 0, 0, 2],
     [0, 1, 0, 0, 0, 2],
     [0, 0, 1, 0, 0, 2],
     [0, 0, 0, 1, 0, 2],
     [0, 0, 0, 0, 1, 2]],
    [[1, 2, 3, 0, 0, 0],  # ray ( a Q b N K )
     [1, 2, 0, 3, 0, 0],
     [1, 0, 2, 3, 0, 0],
     [0, 1, 2, 3, 0, 0],
     [1, 2, 0, 0, 3, 0],
     [1, 0, 2, 0, 3, 0],
     [1, 0, 0, 2, 3, 0],
     [0, 1, 2, 0, 3, 0],
     [0, 0, 1, 2, 3, 0],
     [1, 2, 0, 0, 0, 3],
     [1, 0, 2, 0, 0, 3],
     [1, 0, 0, 2, 0, 3],
     [1, 0, 0, 0, 2, 3],
     [0, 1, 2, 0, 0, 3],
     [0, 0, 1, 2, 0, 3],
     [0, 0, 1, 0, 2, 3],
     [0, 0, 0, 1, 2, 3]],
    [[1, 2, 3, 4, 0, 0],  # ray ( a Q b N p K )
     [1, 2, 3, 0, 4, 0],
     [1, 2, 0, 3, 4, 0],
     [1, 0, 2, 3, 4, 0],
     [0, 1, 2, 3, 4, 0],
     [1, 2, 3, 0, 0, 4],
     [1, 2, 0, 3, 0, 4],
     [1, 2, 0, 0, 3, 4],
     [1, 0, 2, 3, 0, 4],
     [1, 0, 2, 0, 3, 4],
     [1, 0, 0, 2, 3, 4],
     [0, 1, 2, 3, 0, 4],
     [0, 1, 2, 0, 3, 4],
     [0, 1, 0, 2, 3, 4],
     [0, 0, 1, 2, 3, 4]],
    [[1, 2, 3, 4, 5, 0],  # ray ( a Q b N p p K )
     [1, 2, 3, 4, 0, 5],
     [1, 2, 3, 0, 4, 5],
     [1, 2, 0, 3, 4, 5],
     [1, 0, 2, 3, 4, 5],
     [0, 1, 2, 3, 4, 5]],
    [[1, 2, 3, 4, 5, 6]],  # ray ( a Q b N p p N K )
    ]


class RayFilterCommonError(Exception):
    pass


class RayFilterCommon:
    """ChessQL ray filter evaluator.

    The ray and between filters have a list of square specifiers, usually piece
    designators, which define the rays to be evaluated.

    This class assumes the caller has expanded the piece designator parameters
    to the ray or between filter; and applied any transforms.

    Use this class like:
    C(RayFilterCommon)

    Subclasses must implement the database interface specific methods defined
    in this class which raise RayFilterCommonError('Not implemented')
    exceptions.

    """

    def __init__(self, filter_, move_number, variation_code):
        """"""
        if filter_.type not in {constants.BETWEEN, constants.RAY}:
            raise RayFilterCommonError(
                ''.join(("Filter '",
                         filter_.type,
                         "' does not support rays.",
                         )))

        # Is this really needed!
        if len(filter_.children) != 1:
            raise RayFilterCommonError(
                ''.join(("Filter '",
                         filter_.type,
                         "' format not correct.",
                         )))
        if filter_.children[0].type != constants.LEFT_PARENTHESIS_FILTER:
            raise RayFilterCommonError(
                ''.join(("Filter '",
                         filter_.type,
                         "' format not correct.",
                         )))

        self.move_number = move_number
        self.variation_code = variation_code
        raycomponents = []
        psti = piecedesignator.PieceDesignator.piece_square_to_index
        mvi = move_number_str(move_number) + variation_code
        for c in filter_.children[0].children:
            designator_set = set()
            raycomponents.append(designator_set)
            stack = [c]
            while stack:
                if stack[-1].type == constants.PIECE_DESIGNATOR_FILTER:
                    designator_set.update(
                        psti(stack[-1].data.designator_set, mvi))
                    stack.pop()
                    continue
                sp = stack.pop()
                for spc in sp.children:
                    stack.append(spc)
        self.raycomponents = raycomponents
        self.emptycomponents = [set() for i in range(len(raycomponents))]
        self.empty_square_games = set()
        self.piece_square_games = set()
        self.recordset_cache = {}
        self.ray_games = {}

    def prune_end_squares(self, database):
        """Remove ray-end squares with no game references"""
        anypiece = (constants.ANY_WHITE_PIECE_NAME +
                    constants.ANY_BLACK_PIECE_NAME)
        nopiece = constants.EMPTY_SQUARE_NAME
        fd = filespec.PIECESQUAREMOVE_FIELD_DEF, filespec.SQUAREMOVE_FIELD_DEF
        values_finder = database.values_finder(filespec.GAMES_FILE_DEF)
        move = move_number_str(self.move_number)
        nextmove = move_number_str(self.move_number + 1)
        psmwhere, smwhere = [
            database.values_selector(
                ' '.join((f, 'from', move, 'below', nextmove)))
            for f in fd]
        for w in psmwhere, smwhere:
            w.lex()
            w.parse()
            w.evaluate(values_finder)
        moveindex = set(psmwhere.node.result + smwhere.node.result)
        for end in 0, -1:
            if nopiece in ''.join(self.raycomponents[end]):
                emptyset = self.emptycomponents[end]
                empty = [s[:-1] for s in self.raycomponents[end]
                         if nopiece in s]
                for p in anypiece:
                    for e in empty:
                        if e + p in moveindex:
                            continue
                        emptyset.add(e)
            self.raycomponents[end].intersection_update(moveindex)

    def find_games_for_end_squares(self, finder):
        """Remove ray-end squares with no game references"""
        anywhitepiece = constants.ANY_WHITE_PIECE_NAME
        anyblackpiece = constants.ANY_BLACK_PIECE_NAME
        anypiece = anywhitepiece + anyblackpiece
        record_selector = finder.db.record_selector
        rays = constants.RAYS
        empty_square_games = self.empty_square_games
        piece_square_games = self.piece_square_games
        recordset_cache = self.recordset_cache
        start = self.raycomponents[0]
        final = self.raycomponents[-1]
        for s in start:
            start_square = s[-3:-1]
            rs = rays[start_square]
            for f in final:
                final_square = f[-3:-1]
                if final_square not in rs:
                    continue
                for ps in s, f,:
                    if ps not in piece_square_games:
                        if ps[-1] in anypiece:
                            w = record_selector(
                                ' '.join((filespec.SQUAREMOVE_FIELD_DEF,
                                          'eq',
                                          ps,
                                          )))
                        else:
                            w = record_selector(
                                ' '.join((filespec.PIECESQUAREMOVE_FIELD_DEF,
                                          'eq',
                                          ps,
                                          )))
                        w.lex()
                        w.parse()
                        w.evaluate(finder)
                        piece_square_games.add(ps)
                        recordset_cache[ps] = w.node.result.answer
                i = start_square, final_square
                self.add_recordset_to_ray_games(
                    recordset_cache[s], recordset_cache[f], i, finder)
        start = self.emptycomponents[0]
        final = self.emptycomponents[-1]
        for s in start:
            start_square = s[-2:]
            rs = rays[start_square]
            for f in final:
                final_square = f[-2:]
                if final_square not in rs:
                    continue
                for ps in s, f,:
                    if ps not in empty_square_games:
                        w = record_selector(
                            ' '.join(('not',
                                      '(',
                                      filespec.SQUAREMOVE_FIELD_DEF,
                                      'eq',
                                      ps + anywhitepiece,
                                      'or',
                                      ps + anyblackpiece,
                                      ')',
                                      )))
                        w.lex()
                        w.parse()
                        w.evaluate(finder)
                        empty_square_games.add(ps)
                        recordset_cache[ps] = w.node.result.answer
                i = start_square, final_square
                self.add_recordset_to_ray_games(
                    recordset_cache[s], recordset_cache[f], i, finder)
        start = self.raycomponents[0]
        final = self.raycomponents[-1]
        for e in self.emptycomponents[0]:
            if e not in empty_square_games:
                continue
            start_square = e[-2:]
            sc = recordset_cache[e]
            for f in final:
                fc = recordset_cache[f]
                final_square = f[-3:-1]
                i = start_square, final_square
                self.add_recordset_to_ray_games(sc, fc, i, finder)
        for e in self.emptycomponents[-1]:
            if e not in empty_square_games:
                continue
            final_square = e[-2:]
            fc = recordset_cache[e]
            for s in start:
                sc = recordset_cache[s]
                start_square = s[-3:-1]
                i = start_square, final_square
                self.add_recordset_to_ray_games(sc, fc, i, finder)

    def add_recordset_to_ray_games(
        self, start, final, rayindex, finder):
        """Remove ray-end squares with no game references"""
        raise RayFilterCommonError(
            'Implement add_recordset_to_ray_games in subclass.')

    def find_games_for_middle_squares(self, finder):
        """Remove ray-end squares with no game references"""
        anywhitepiece = constants.ANY_WHITE_PIECE_NAME
        anyblackpiece = constants.ANY_BLACK_PIECE_NAME
        anypiece = anywhitepiece + anyblackpiece
        nopiece = constants.EMPTY_SQUARE_NAME
        record_selector = finder.db.record_selector
        internal_ray_length = len(self.raycomponents) - 2
        empty_square_games = self.empty_square_games
        piece_square_games = self.piece_square_games
        recordset_cache = self.recordset_cache
        raycomponents = self.raycomponents
        internal_raycomponents = raycomponents[1:-1]
        mvi = move_number_str(self.move_number) + self.variation_code
        c_sqi = [{}] # Maybe the empty square index values?
        for e, rc in enumerate(internal_raycomponents):
            sqi = {}
            c_sqi.append(sqi)
            for i in rc:
                sqi.setdefault(i[-3:-1], set()).add(i)
        for start, final in self.ray_games:
            line = constants.RAYS[start][final][1:-1]
            if len(line) < len(internal_raycomponents):
                continue
            mapraytoline = MAP_RAY_TO_LINE[len(internal_raycomponents)]
            raygames = []
            for mrtl in mapraytoline:
                if len(line) < 6: # mapraytoline[7] = 0 avoids this test.
                    if mrtl[len(line)]:
                        break
                linesets = []
                for e, v in enumerate(mrtl[:len(line)]):
                    if line[e] not in c_sqi[v]:
                        if v:
                            linesets.clear()
                            break
                        c_sqi[v][line[e]] = {mvi + line[e] + nopiece}
                    linesets.append(c_sqi[v][line[e]])
                linegames = []
                for lg in linesets:
                    squareset = self.create_empty_recordset(finder)
                    linegames.append(squareset)
                    for i in lg:
                        if i in recordset_cache:
                            self.add_recordset_to_squareset(
                                recordset_cache[i], squareset)
                            continue
                        if i[-1] == nopiece:
                            w = record_selector(
                                ' '.join(('not',
                                          '(',
                                          filespec.SQUAREMOVE_FIELD_DEF,
                                          'eq',
                                          i[:-1] + anywhitepiece,
                                          'or',
                                          i[:-1] + anyblackpiece,
                                          ')',
                                          )))
                            w.lex()
                            w.parse()
                            w.evaluate(finder)
                            recordset_cache[i] = w.node.result.answer
                            self.add_recordset_to_squareset(
                                recordset_cache[i], squareset)
                            continue
                        if i[-1] in anypiece:
                            w = record_selector(
                                ' '.join((filespec.SQUAREMOVE_FIELD_DEF,
                                          'eq',
                                          i,
                                          )))
                        else:
                            w = record_selector(
                                ' '.join((filespec.PIECESQUAREMOVE_FIELD_DEF,
                                          'eq',
                                          i,
                                          )))
                        w.lex()
                        w.parse()
                        w.evaluate(finder)
                        recordset_cache[i] = w.node.result.answer
                        self.add_recordset_to_squareset(
                            recordset_cache[i], squareset)
                if linegames:
                    self.collect_line_recordsets_for_ray(
                        linegames, raygames, (start, final), finder)
            if raygames:
                rayset = raygames.pop()
                for rg in raygames:
                    self.add_recordset_to_squareset(rg, rayset)
                    self.destroy_recordset(rg, finder)
                self.replace_records(self.ray_games[start, final], rayset)
            else:
                self.replace_records(self.ray_games[start, final],
                                     self.create_empty_recordset(finder))

    @staticmethod
    def create_empty_recordset(finder):
        """Return empty recordset."""
        raise RayFilterCommonError(
            'Implement create_empty_recordset in subclass.')

    @staticmethod
    def add_recordset_to_squareset(recordset, squareset):
        """Add recordset to squareset."""
        raise RayFilterCommonError(
            'Implement add_recordset_to_squareset in subclass.')

    def collect_line_recordsets_for_ray(
        self, linegames, raygames, index, finder):
        """Add linegames recordsets to self.raygames for index."""
        raise RayFilterCommonError(
            'Implement collect_line_recordsets_for_ray in subclass.')

    @staticmethod
    def destroy_recordset(recordset, finder):
        """Destroy recordset."""
        raise RayFilterCommonError(
            'Implement destroy_recordset in subclass.')

    @staticmethod
    def replace_records(recordset, newrecords):
        """Replace records in recordset with newrecords."""
        raise RayFilterCommonError(
            'Implement replace_records in subclass.')
