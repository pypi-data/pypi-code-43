import os
import tempfile

from healer.persist.support.mapping import *


def test_mapping():
    print()

    store_path = tempfile.mktemp(prefix="StoredMapping-", suffix=".db")

    mapping = StoredMapping(store_path)

    mapping.open()
    mapping.clear()
    mapping.vacuum()

    assert bool(mapping) == False
    assert mapping.size() == 0
    mapping['hello'] = 'kitty'
    assert 'hello' in mapping
    assert mapping['hello'] == 'kitty'
    assert mapping.size() == 1
    assert bool(mapping) == True

    for key in mapping:
        print(f"key={key}")

    for key, value in mapping.items():
        print(f"key={key} value={value}")

    del mapping['hello']

    assert mapping.size() == 0
    assert mapping.is_empty()

    source_count = 1000

    for index in range(source_count):
        key = f"key-{index}"
        value = f"value-{index}"
        mapping[key] = value

    assert not mapping.is_empty()
    assert len(mapping) == source_count
    assert mapping.size() == source_count

    mapping.clear()
    mapping.vacuum()

    assert mapping.is_empty()
    assert mapping.size() == 0

    mapping.close()

    os.remove(store_path)
