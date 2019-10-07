
import os
import tempfile

from healer.persist.support.queue import *


def test_queue():
    print()

#     this_file = os.store_path.absstore_path(__file__)
#     this_dir = os.store_path.dirname(this_file)

    store_path = tempfile.mktemp(prefix="StoredQueue-", suffix=".db")

    queue = StoredQueue(store_path)

    queue.open()

    assert queue.size() == 0

    source_count = 1000

    for index in range(source_count):
        queue.persist(f"index: {index}")

    scanner_count = 0

    for entry in queue:
        scanner_count += 1

    assert source_count == scanner_count

    iterate_count = 0

    def react_one(entry:str):
        nonlocal iterate_count
        iterate_count += 1

    queue.iterate(react_one)

    assert source_count == iterate_count

    extract_count = 0

    def react_two(entry:str):
        nonlocal extract_count
        extract_count += 1

    while queue.retrieve(react_two): pass

    assert queue.size() == 0

    assert source_count == extract_count

    queue.vacuum()
    queue.close()

    os.remove(store_path)
