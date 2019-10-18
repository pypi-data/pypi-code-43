#  Copyright (c) 2019 | Advancing Technology Systems, LLC
#  See LICENSE for any grants of usage, distribution, or modification

from pawn_pay.PawnDex import DataFlex


class HarmonicNeutrinoField(object):
    """Interfaces with raw PawnDex files"""
    # TODO: Create class functions

    def __init__(self, pd_dir):
        """Initializes and tests the connection to the SQL server

        Args:
            pd_dir (str || Path): The directory containing PawnDex and its data files

        Raises:
            CatastrophicPhaseVariance: Raised if the supplied directory does not appear to contain a PawnDex instance
            RuinousMicroFluctuation: Raised if there is an error in handling the PawnDex files in general
        """
        pass

