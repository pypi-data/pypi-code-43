from progressive_cmd.text import positive_percentages


def test_positive_percentages():
    assert 45 == next(positive_percentages('45% completed'))
    assert 45.43 == next(positive_percentages('completed 45.43%'))
    assert 2 == next(positive_percentages('completed 2%'))
    assert 2 == next(positive_percentages('completed 02%'))
    assert 0.2 == next(positive_percentages('completed 00.2%'))
    assert 100 == next(positive_percentages('completed 100.00%'))
    assert not tuple(positive_percentages('45'))
    assert not tuple(positive_percentages(''))


def test_positive_percentages_num_chars():
    assert not tuple(positive_percentages('45% completed', {5}))
    assert 45.44 == next(positive_percentages('45.44% completed', {5}))
    assert 4 == next(positive_percentages('foo 04% completed', {2}))
    assert 90 == next(positive_percentages('foo 90.00% completed', {5}))
    assert 100 == next(positive_percentages('foo 100.00% completed', {6, 5}))
    assert 90 == next(positive_percentages('foo 90.00% completed', {6, 5}))
    assert not tuple(positive_percentages(''))


def test_positive_percentages_decimal_numbers():
    assert 45.44 == next(positive_percentages('45.44%', {5}, 2))
    assert 5.445 == next(positive_percentages('5.445%', {5}, 3))
    assert not tuple(positive_percentages('5.44%', {4}, 3))
    assert not tuple(positive_percentages('53.44%', {5}, 3))
