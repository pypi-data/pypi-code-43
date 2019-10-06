import contentmatcher


short_sequence = ['test0', 'test1', 'test2', 'test2a', 'test3', 'test4', 'test4b', 'test5', 'test6', 'test7', 'test8']
short_pattern_input = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6']
short_pattern = contentmatcher.Pattern(short_pattern_input)
short_pattern_expected_fast_ratio = 1.0
short_pattern_expected_ordered_match_ratio = 2/6


def test_fast_match_ratio():
    result = short_pattern.fast_match_ratio(short_sequence)
    assert result == short_pattern_expected_fast_ratio


def test_longest_ordered_match_ratio():
    result = short_pattern.longest_ordered_chunk_match_ratio(short_sequence)
    assert result == short_pattern_expected_ordered_match_ratio
