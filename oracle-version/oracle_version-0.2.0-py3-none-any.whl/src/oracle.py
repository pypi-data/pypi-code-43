import json
import random
from binascii import hexlify
from os import urandom
from typing import Any, Dict, Optional, Tuple

DATASET: Dict[str, Any] = {}

with open("src/dataset.json", "r") as f:
    DATASET = json.load(f)


def get_object() -> str:
    """
        Get object from dataset
    """
    object_type = random.choice(list(DATASET["objects"].keys()))

    return random.choice(DATASET["objects"][object_type]).capitalize()


def get_property() -> str:
    """
        Get property from dataset
    """
    property_type = random.choice(list(DATASET["properties"].keys()))

    return random.choice(DATASET["properties"][property_type])


def get_version_name(seed: Optional[str] = None) -> Tuple[str, Any]:
    """Get object and property random names

    :param seed: seed for generate version name
    """
    if not seed:
        seed = hexlify(urandom(4)).decode().upper()

    random.seed(seed)

    return f"{get_property()} {get_object()}", seed
