import pytest

from shuttlis.utils import one_or_none, one, id_map, next_or_none, pairwise


@pytest.mark.parametrize(
    "lizt,key,expected",
    [
        ([1, 2, 3], lambda x: x == 2, 2),
        (["a", "b", "c"], lambda x: x == "c", "c"),
        (["a", "b", "c"], lambda x: x == "d", None),
    ],
)
def test_one_or_none(lizt, key, expected):
    actual = one_or_none(lizt, key)
    assert expected == actual


def test_one_or_none_raises_assertion_error_if_more_than_one_match():
    with pytest.raises(AssertionError):
        one_or_none([1, 2, 2, 2], lambda x: x == 2)


@pytest.mark.parametrize(
    "lizt,key,expected",
    [
        ([1, 2, 3], lambda x: x == 2, 2),
        (["a", "b", "c"], lambda x: x == "c", "c"),
        (["a", "b", "c", "c"], lambda x: x == "c", "c"),
        (["a", "b", "c"], lambda x: x == "d", None),
    ],
)
def test_next_or_none(lizt, key, expected):
    actual = next_or_none(lizt, key)
    assert expected == actual


@pytest.mark.parametrize(
    "lizt,key,expected",
    [([1, 2, 3], lambda x: x == 2, 2), (["a", "b", "c"], lambda x: x == "c", "c")],
)
def test_one(lizt, key, expected):
    actual = one(lizt, key)
    assert expected == actual


def test_one_raises_assertion_error_if_more_than_one_match():
    with pytest.raises(AssertionError):
        one([1, 2, 2, 2], lambda x: x == 2)


def test_one_raises_assertion_error_if_none_match():
    with pytest.raises(AssertionError):
        one([1, 2, 2, 2], lambda x: x == 4)


@pytest.mark.parametrize(
    "lizt,key,expected", [(["a", "ab", "abc"], len, {1: "a", 2: "ab", 3: "abc"})]
)
def test_id_map(lizt, key, expected):
    assert expected == id_map(lizt, key=key)


def test_id_map_with_multiple_items_raises_error():
    with pytest.raises(AssertionError):
        id_map(["a", "b", "c"], key=len)


def test_pairwise():
    assert pairwise([1, 2, 3]) == ([(1, 2), (2, 3)])
    assert pairwise([]) == []
