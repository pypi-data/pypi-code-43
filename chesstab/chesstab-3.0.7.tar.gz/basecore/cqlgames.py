# cqlgames.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Evaluate a ChessQL query.

Methods defined on all database interfaces are used exclusively.

"""
from copy import deepcopy

from solentware_base.api.where import Where

from chessql.core import constants

from pgn_read.core.constants import MAP_PGN_SQUARE_NAME_TO_FEN_ORDER

from ..core.filespec import (
    PARTIAL_FILE_DEF,
    NEWGAMES_FIELD_DEF,
    NEWGAMES_FIELD_VALUE,
    PARTIALPOSITION_FIELD_DEF,
    PIECESQUAREMOVE_FIELD_DEF,
    )
from . import rayfilter

from .cqlgamescommon import (
    ChessQLGamesError,
    ChessQLGamesCommon,
    where_eq_piece_designator,
    AND_FILTERS,
    OR_FILTERS,
    move_number_in_key_range,
    )


class ChessQLGames(ChessQLGamesCommon):
    
    """Represent subset of games that match a list of piece designators.

    Use this class like:
    C(subclass<solentware_grid.core.dataclient.DataSource>, ChessQLGames)

    """

    def forget_cql_statement_games(
        self, sourceobject, commit=True):
        """Forget game records matching ChessQL statement.

        sourceobject is previously calculated answer.  Set to None to force
        recalculation from query (after editing query statement usually).
        
        """
        # Forget the list of games under the query key.
        if sourceobject is not None:
            if commit:
                self.dbhome.start_transaction()
            ppview = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                PARTIAL_FILE_DEF,
                key=sourceobject.key.recno)
            self.dbhome.unfile_records_under(
                self.dbset,
                PARTIALPOSITION_FIELD_DEF,
                self.dbhome.encode_record_number(sourceobject.key.recno))

            # Remove query from set that needs recalculating.
            changed = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                key=self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE))
            changed |= ppview
            changed ^= ppview

            self.dbhome.file_records_under(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                changed,
                self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE),
                )
            if commit:
                self.dbhome.commit()
            changed.close()
            ppview.close()

    def calculate_cql_statement_games(
        self, query, sourceobject, initial_recordset=None, commit=True):
        """Find game records matching ChessQL statement.

        query is detail extracted from query statement.
        sourceobject is previously calculated answer.  Set to None to force
        recalculation from query (after editing query statement usually).
        initial_recordset is games to which query is applied.
        
        """
        # Evaluate query.
        if initial_recordset is None:
            initial_recordlist = self.dbhome.make_recordset_all(self.dbset,
                                                                self.dbname)
        else:
            initial_recordlist = deepcopy(initial_recordset)
        games = self.get_games_matching_filters(
            query,
            self.get_games_matching_parameters(self, initial_recordlist))

        # File the list of games under the query key.
        if sourceobject is not None:
            if commit:
                self.dbhome.start_transaction()
            ppview = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                PARTIAL_FILE_DEF,
                key=sourceobject.key.recno)
            self.dbhome.file_records_under(
                self.dbset,
                PARTIALPOSITION_FIELD_DEF,
                games,
                self.dbhome.encode_record_number(sourceobject.key.recno))

            # Remove query from set that needs recalculating.
            changed = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                key=self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE))
            changed |= ppview
            changed ^= ppview

            self.dbhome.file_records_under(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                changed,
                self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE),
                )
            if commit:
                self.dbhome.commit()
            changed.close()
            ppview.close()

    def get_cql_statement_games(
        self, query, sourceobject, initial_recordset=None, commit=True):
        """Find game records matching ChessQL statement.

        query is detail extracted from query statement.
        sourceobject is previously calculated answer.  Set to None to force
        recalculation from query (after editing query statement usually).
        initial_recordset is games to which query is applied.
        
        """
        if query is None:
            self.set_recordset(self.dbhome.make_recordset(self.dbset))
            return

        # Use the previously calculated record set if possible.
        # sourceobject is set to None if query must be recalculated.
        if sourceobject is not None:
            games = self.dbhome.make_recordset(self.dbset)
            ppview = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                PARTIAL_FILE_DEF,
                key=sourceobject.key.recno)
            changed = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                key=self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE))
            pprecalc = ppview & changed
            changed.close()
            if pprecalc.count_records() == 0:
                ppcalc = self.dbhome.make_recordset_key_startswith(
                    self.dbset,
                    PARTIALPOSITION_FIELD_DEF,
                    key=self.dbhome.encode_record_number(
                        sourceobject.key.recno))
                if ppcalc.count_records() != 0:
                    calc = self.dbhome.make_recordset_key(
                        self.dbset,
                        PARTIALPOSITION_FIELD_DEF,
                        key=self.dbhome.encode_record_number(
                            sourceobject.key.recno))
                    games |= calc

                    # Hand the list of games over to the user interface.
                    self.set_recordset(games)

                    calc.close()
                    ppcalc.close()
                    ppview.close()
                    pprecalc.close()
                    return
                ppcalc.close()
            pprecalc.close()

        # Evaluate query.
        if initial_recordset is None:
            initial_recordlist = self.dbhome.make_recordset_all(self.dbset,
                                                                self.dbname)
        else:
            initial_recordlist = deepcopy(initial_recordset)
        games = self.get_games_matching_filters(
            query,
            self.get_games_matching_parameters(query, initial_recordlist))

        # File the list of games under the query key.  Either there is no list
        # already filed or it is out of date because games have been edited.
        # The existing list was used earlier if possible.
        if sourceobject is not None:
            if commit:
                self.dbhome.start_transaction()
            self.dbhome.file_records_under(
                self.dbset,
                PARTIALPOSITION_FIELD_DEF,
                games,
                self.dbhome.encode_record_number(sourceobject.key.recno))

            # Remove query from set that needs recalculating.
            changed = self.dbhome.make_recordset_key(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                key=self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE))
            changed |= ppview
            changed ^= ppview

            self.dbhome.file_records_under(
                PARTIAL_FILE_DEF,
                NEWGAMES_FIELD_DEF,
                changed,
                self.dbhome.encode_record_selector(NEWGAMES_FIELD_VALUE),
                )
            if commit:
                self.dbhome.commit()
            changed.close()
            ppview.close()

        # Hand the list of games over to the user interface.
        self.set_recordset(games)

    def get_games_matching_filters(self, query, games):
        """Select the games which meet the ChessQL cql() ... filters.

        Walk node tree for every movenumber and combine evaluated game sets.

        """
        found = self.dbhome.make_recordset(self.dbset)
        if not query.cql_filters:
            return found
        query.cql_filters.expand_child_piece_designators()
        cursor = self.dbhome.database_cursor(self.dbset,
                                             PIECESQUAREMOVE_FIELD_DEF)
        try:
            k = cursor.last()[0]
        except TypeError:
            return found
        finally:
            cursor.close()
            del cursor
        self.not_implemented = set()
        for movenumber in move_number_in_key_range(k):
            found |= self._games_matching_filter(
                query.cql_filters, games, movenumber, '0')
        return found

    # Version of get_games_matching_filters() to process CQL parameters.
    def get_games_matching_parameters(self, query, games):
        """Select the games which meet the ChessQL cql(...) parameters

        Walk node tree for cql parameters and combine evaluated game sets.

        """
        return games
        
    def _games_matching_filter(
        self, filter_, initialgames, movenumber, variation):
        """Return games matching filters in CQL statement.

        It is assumed FSNode.designator_set contains the expanded piece
        designators.

        """
        if filter_.type in AND_FILTERS:
            games = deepcopy(initialgames)
            for n in filter_.children:
                if n.type == constants.PIECE_DESIGNATOR_FILTER:
                    games &= self._games_matching_piece_designator(
                        n, games, movenumber, variation)
                    if not games.count_records():
                        return games
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                games &= self._games_matching_filter(
                    n, games, movenumber, variation)
                if not games.count_records():
                    return games
            return games
        elif filter_.type in OR_FILTERS:
            games = self.dbhome.make_recordset(self.dbset)
            for n in filter_.children:
                if self.is_filter_implemented(n):
                    continue
                games |= self._games_matching_filter(
                    n, initialgames, movenumber, variation)
            return games
        else:
            if filter_.type == constants.PIECE_DESIGNATOR_FILTER:
                return self._games_matching_piece_designator(
                    filter_, initialgames, movenumber, variation)
            if filter_.type == constants.ON:
                return self._games_matching_on_filter(
                    filter_, initialgames, movenumber, variation)
            if filter_.type == constants.RAY:
                return self._games_matching_ray_filter(
                    filter_, initialgames, movenumber, variation)
            return initialgames
        
    def _games_matching_piece_designator(
        self, filter_, datasource, movenumber, variation):
        """Return games matching a piece designator."""

        if filter_.type != constants.PIECE_DESIGNATOR_FILTER:
            raise ChessQLGamesError(''.join(("'",
                                             constants.PIECE_DESIGNATOR_FILTER,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        answer = self._evaluate_piece_designator(
            movenumber,
            variation,
            filter_.data.designator_set)
        return datasource & answer
        
    def _games_matching_on_filter(
        self, filter_, datasource, movenumber, variation):
        """Return games matching an on filter."""

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
        squares = left.intersection(right)
        if not squares:
            return self.dbhome.make_recordset(self.dbset)
        left = self.pieces_matching_filter(
            filter_.children[0],
            set(constants.ALL_PIECES))
        right = self.pieces_matching_filter(
            filter_.children[1],
            set(constants.ALL_PIECES))
        pieces = left.intersection(right)
        if not pieces:
            return self.dbhome.make_recordset(self.dbset)
        answer = self._evaluate_piece_designator(
            movenumber,
            variation,
            {p + s for p in pieces for s in squares})
        leftgames = self._games_matching_filter(
            filter_.children[0], datasource, movenumber, variation)
        rightgames = self._games_matching_filter(
            filter_.children[1], datasource, movenumber, variation)
        return leftgames & rightgames & answer
        
    def _games_matching_ray_filter(
        self, filter_, datasource, movenumber, variation):
        """Return games matching a ray filter."""

        if filter_.type != constants.RAY:
            raise ChessQLGamesError(''.join(("'",
                                             constants.RAY,
                                             "' expected but '",
                                             str(filter_.type),
                                             "'received",
                                             )))
        rf = rayfilter.RayFilter(filter_, movenumber, variation)
        rf.prune_end_squares(self.dbhome)
        rf.find_games_for_end_squares(self.cqlfinder)
        rf.find_games_for_middle_squares(self.cqlfinder)

        # So that downstream methods have a valid object to work with.
        recordset = self.dbhome.make_recordset(self.dbset)
        for gs in rf.ray_games.values():
            recordset |= gs
        return recordset

    def _evaluate_piece_designator(
        self, move_number, variation_code, piecesquares):
        """.

        The fieldname PieceSquareMove is now unavoidably a bit confusing, where
        move refers to a token in the movetext when the piece is on the square.
        Nothing to do with move number in the movetext, which is the ChessQL
        meaning of move in this context.

        """
        w = Where(where_eq_piece_designator(
            move_number, variation_code, piecesquares))
        w.lex()
        w.parse()

        # What if v != [] afterward.
        # Probably the call should be:
        # w.validate(self.cqlfinder._db, self.cqlfinder._dbset)
        # because it has to be so in dptcql since the datasource object cannot
        # provide dbhome and dbset.
        # Also the validation should be against the object cqlfinder is going
        # to search.
        v = w.validate(self.cqlfinder.db, self.cqlfinder.dbset)

        w.evaluate(self.cqlfinder)
        answer = w.node.result.answer
        w.close_all_nodes(self.cqlfinder)
        return answer
