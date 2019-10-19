# dptrayfilter.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess Query Language (ChessQL) ray filter evaluator.

Examples of ray filters are 'ray ( Q n k )' and 'ray ( Q[a4,c3] n kh1-8 )'.

RayFilter expands the list of square descriptions into the particular rays,
horizontal, vertical, and diagonal, which need to be evaluated.

pgn.core.constants.GAPS provides the lists of squares between pairs of squares
from which the rays are calculated.

"""
from dptdb import dptapi

from ..core import filespec
from ..basecore.rayfiltercommon import RayFilterCommon


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
        rg = finder.context.CreateRecordList()
        rg.Place(start)
        rg.Place(final)
        s = finder.context.CreateRecordList()
        for l in start, final:
            s.Place(rg)
            s.Remove(l)
            rg.Remove(s)
        finder.context.DestroyRecordSet(s)
        if rg.Count():
            if rayindex in self.ray_games:
                self.ray_games[rayindex].Place(rg)
                finder.context.DestroyRecordSet(rg)
            else:
                self.ray_games[rayindex] = rg

    @staticmethod
    def create_empty_recordset(finder):
        """Return empty recordset."""
        return finder.context.CreateRecordList()

    @staticmethod
    def add_recordset_to_squareset(recordset, squareset):
        """Add recordset to squareset."""
        squareset.Place(recordset)

    def collect_line_recordsets_for_ray(
        self, linegames, raygames, index, finder):
        """Add linegames recordsets to self.raygames for index."""
        squareset = finder.context.CreateRecordList()
        lgp = linegames.pop()
        rgi = self.ray_games[index]
        squareset.Place(lgp)
        squareset.Place(rgi)
        s = finder.context.CreateRecordList()
        s.Place(squareset)
        s.Remove(lgp)
        squareset.Remove(s)
        s.Place(squareset)
        s.Remove(rgi)
        squareset.Remove(s)
        finder.context.DestroyRecordSet(lgp)
        for lg in linegames:
            s.Clear()#s.Remove(s) # clear the list
            s.Place(squareset)
            s.Remove(lg)
            squareset.Remove(s)
            finder.context.DestroyRecordSet(lg)
        finder.context.DestroyRecordSet(s)
        raygames.append(squareset)

    @staticmethod
    def destroy_recordset(recordset, finder):
        """Destroy recordset."""
        finder.context.DestroyRecordSet(recordset)

    @staticmethod
    def replace_records(recordset, newrecords):
        """Replace records in recordset with newrecords."""
        recordset.Clear()
        recordset.Place(newrecords)
