class SeriousProblem(Exception):
    """The base Exception class that all Pawn-Pay Client & Module exceptions
    inherit from
    """
    pass


class RuinousMicroFluctuation(SeriousProblem):
    """Raised if client or module-specific behavior encounters an error

    ex. The credentials supplied to the Pawn-Pay client are invalid ex. The
    SQL Server used by PawnMaster is not reachable
    """
    pass


class CatastrophicPhaseVariance(SeriousProblem):
    """Raised if non-behavior related code encounters an error

    ex. An underlying support library throws an error that prohibits the
    functionality of the client or module, but does not crash the module itself,
    nor is it directly caused by the module or client
    """
    pass
