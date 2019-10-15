from enum import Enum


class GeneratorType(Enum):
    """
    An enumeration describing a type of environment generator
    """
    DOCKER = 0
    SHELL = 1
