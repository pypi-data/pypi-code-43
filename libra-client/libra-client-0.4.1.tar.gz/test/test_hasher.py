from libra.hasher import *

def test_placeholder_hash():
    assert ACCUMULATOR_PLACEHOLDER_HASH == [65, 67, 67, 85, 77, 85, 76, 65, 84, 79, 82, 95, 80, 76, 65, 67, 69, 72, 79, 76, 68, 69, 82, 95, 72, 65, 83, 72, 0, 0, 0, 0]
    assert SPARSE_MERKLE_PLACEHOLDER_HASH == [83, 80, 65, 82, 83, 69, 95, 77, 69, 82, 75, 76, 69, 95, 80, 76, 65, 67, 69, 72, 79, 76, 68, 69, 82, 95, 72, 65, 83, 72, 0, 0]
    assert PRE_GENESIS_BLOCK_ID == [80, 82, 69, 95, 71, 69, 78, 69, 83, 73, 83, 95, 66, 76, 79, 67, 75, 95, 73, 68, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert GENESIS_BLOCK_ID == [71, 69, 78, 69, 83, 73, 83, 95, 66, 76, 79, 67, 75, 95, 73, 68, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
