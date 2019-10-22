import os

from mercury.client.model.direction import Direction
from mercury.client.model.option_contract_type import OptionContractType

NUM_TRADE = os.getenv('NUM_TRADE', 15)
NUM_PRICE = os.getenv('NUM_PRICE', 30)
DELTA_RANGE = os.getenv('DELTA_RANGE', '0.1,0.9')
NUM_QUANTITY = os.getenv('NUM_QUANTITY', 10.0)
STOP_BEFORE = os.getenv('STOP_BEFORE', 14)
SEQ_LEN = os.getenv('SEQ_LEN', 5)
MARGIN = os.getenv('MARGIN', 10000.0)


def idx2direction(idx):
    """
    idx -> Direction

    :param int idx: Index

    :return: Direction
    """
    return Direction.LONG if idx == 0 else Direction.SHORT


def direction2idx(direction):
    """
    Direction -> idx

    :param direction: Direction

    :return int: Index
    """
    return 0 if direction == Direction.LONG else 1


def idx2optiontype(idx):
    """
    idx -> OptionType

    :param int idx: Index

    :return: OptionType
    """
    return OptionContractType.CALL if idx == 0 else OptionContractType.PUT


def optiontype2idx(option_type):
    """
    OptionType -> idx

    :param option_type: OptionType

    :return int: Index
    """
    return 0 if option_type == OptionContractType.CALL else 1
