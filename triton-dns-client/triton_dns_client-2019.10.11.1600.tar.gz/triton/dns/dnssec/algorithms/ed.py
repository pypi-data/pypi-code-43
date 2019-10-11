from .base import Algorithm


class EDAlgorithm(Algorithm):
    pass


class ED448(EDAlgorithm):
    id = 16


class ED25519(EDAlgorithm):
    id = 15
