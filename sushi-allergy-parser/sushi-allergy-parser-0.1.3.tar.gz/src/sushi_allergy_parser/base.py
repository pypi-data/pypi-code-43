from abc import ABCMeta, abstractmethod
from enum import Enum, auto, unique

from pandas import DataFrame


@unique
class Allergen(Enum):
    EGG = "egg"
    WHEAT = "wheat"
    MILK = "milk"
    PEANUT = "peanut"
    BUCKWHEAT = "buckwheat"
    SHRIMP = "shrimp"
    CRAB = "crab"
    SQUID = "squid"
    SALMON_ROE = "salmonRoe"
    SALMON = "salmon"
    MACKEREL = "mackerel"
    BEEF = "beef"
    CHICKEN = "chicken"
    PORK = "pork"
    SOYBEAN = "soybean"
    ORANGE = "orange"
    APPLE = "apple"
    GELATIN = "gelatin"
    WALNUT = "walnut"
    BANANA = "banana"
    KIWI = "kiwi"
    YAM_OR_SWEET_POTATO = "yamOrSweetPotato"
    PEACH = "peach"
    SESAME = "sesame"
    ABALONE = "abalone"
    CASHEW_NUT = "cashewNut"
    MATSUTAKE_MUSHROOM = "matsutakeMushroom"

    @classmethod
    def values(cls):
        return [enum.value for enum in list(Allergen)]


class AllergenState(Enum):
    CONTAIN = auto()  # 含む
    MAY_CONTAIN = auto()  # 製造工程で混入する可能性あり
    NOT_CONTAIN = auto()  # 含まない

    def __str__(self):
        return self.name


class BaseParser(metaclass=ABCMeta):
    @abstractmethod
    def parse(self, filename: str) -> DataFrame:
        raise NotImplementedError

    @abstractmethod
    def allergen_state_of(self, value: str) -> AllergenState:
        raise NotImplementedError

