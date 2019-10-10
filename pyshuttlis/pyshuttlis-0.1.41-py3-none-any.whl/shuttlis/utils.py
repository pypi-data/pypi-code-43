import itertools as it
import random
from typing import List, Callable, Any, Optional, Dict
from uuid import uuid4

from shuttlis.geography import Location


def one_or_none(lizt: List[Any], key: Callable[[Any], bool]) -> Optional[Any]:
    gen = (x for x in lizt if key(x))
    elm = next(gen, None)
    if elm:
        assert next(gen, None) is None
    return elm


def next_or_none(lizt: List[Any], key: Callable[[Any], bool]) -> Optional[Any]:
    gen = (x for x in lizt if key(x))
    elm = next(gen, None)
    return elm


def one(lizt: List[Any], key: Callable[[Any], bool]) -> Any:
    maybe_elm = one_or_none(lizt, key)
    assert maybe_elm is not None
    return maybe_elm


def group_by(lizt: List[Any], key: Callable[[Any], Any]) -> Dict[Any, List[Any]]:
    sorted_list = sorted(lizt, key=key)
    return {k: list(v) for k, v in it.groupby(sorted_list, key)}


def id_map(lizt: List[Any], key: Callable[[Any], Any]) -> Dict[Any, Any]:
    list_map = group_by(lizt, key=key)
    assert all(len(v) == 1 for v in list_map.values())
    return {k: v[0] for k, v in list_map.items()}


def random_location():
    lat = random.uniform(-90, 90)
    lng = random.uniform(-180, 180)
    return Location(lat, lng)


def uuid4_str():
    return str(uuid4())


def pairwise(lizt):
    "[s0, s1, s2, s3] -> (s0,s1), (s1,s2), (s2, s3), ..."  # n-1 items from list
    return [x for x in zip(lizt[:-1], lizt[1:])]
