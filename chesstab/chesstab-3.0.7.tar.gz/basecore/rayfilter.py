# rayfilter.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess Query Language (ChessQL) ray filter evaluator.

Examples of ray filters are 'ray ( Q n k )' and 'ray ( Q[a4,c3] n kh1-8 )'.

RayFilter expands the list of square descriptions into the particular rays,
horizontal, vertical, and diagonal, which need to be evaluated.

pgn_read.core.constants.GAPS provides the lists of squares between pairs of
squares from which the rays are calculated.

"""
from ..core import filespec
from .rayfiltercommon import RayFilterCommon


class RayFilter(RayFilterCommon):
    """ChessQL ray filter evaluator.

    The ray and between filters have a list of square specifiers, usually piece
    designators, which define the rays to be evaluated.

    This class assumes the caller has expanded the piece designator parameters
    to the ray or between filter; and applied any transforms.

    """

    def add_recordset_to_ray_games(
        self, start, final, rayindex, finder):
        """Remove ray-end squares with no game references"""
        rg = start & final
        if rg.count_records():
            if rayindex in self.ray_games:
                self.ray_games[rayindex] |= rg
            else:
                self.ray_games[rayindex] = rg

    @staticmethod
    def create_empty_recordset(finder):
        """Return empty recordset."""
        return finder.db.make_recordset(filespec.GAMES_FILE_DEF)

    @staticmethod
    def add_recordset_to_squareset(recordset, squareset):
        """Add recordset to squareset."""
        squareset |= recordset

    def collect_line_recordsets_for_ray(
        self, linegames, raygames, index, finder):
        """Add linegames recordsets to self.raygames for index."""
        squareset = linegames.pop() & self.ray_games[index]
        for lg in linegames:
            squareset &= lg
        raygames.append(squareset)

    @staticmethod
    def destroy_recordset(recordset, finder):
        """Destroy recordset: do nothing, present for DPT compatibility."""

    @staticmethod
    def replace_records(recordset, newrecords):
        """Replace records in recordset with newrecords.

        This method exists for compatibility with DPT where simply binding an
        attribute to newrecords may not be correct.

        """
        recordset.clear_recordset()
        recordset |= newrecords
