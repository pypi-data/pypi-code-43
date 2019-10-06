"""Speed tests for use with e.g. 'python3 -m pytest --durations=0' to show call times"""


import contentmatcher
import random
import string


def generate_string(string_length: int = 8):
    return ''.join(random.choices(string.ascii_lowercase, k=string_length))


def generate_string_list(length: int) -> list:
    return [generate_string() for _ in range(length)]


speed_test_iterations = 1000000

short_sequence = ['test0', 'test1', 'test2', 'test2a', 'test3', 'test4', 'test4b', 'test5', 'test6', 'test7', 'test8']
short_pattern_input = ['test1', 'test2', 'test3', 'test4', 'test5', 'test6']
short_pattern = contentmatcher.Pattern(short_pattern_input)

long_sequence = generate_string_list(40)
long_pattern_input = generate_string_list(10)
long_pattern = contentmatcher.Pattern(long_pattern_input)


def test_short_fast_match_ratio_speed():
    for x in range(speed_test_iterations):
        results = short_pattern.fast_match_ratio(short_sequence)


def test_long_fast_match_ratio_speed():
    for x in range(speed_test_iterations):
        results = long_pattern.fast_match_ratio(long_sequence)


def test_short_ordered_match_ratio_speed():
    for x in range(speed_test_iterations):
        results = short_pattern.longest_ordered_chunk_match_ratio(short_sequence)


def test_long_ordered_match_ratio_speed():
    for x in range(speed_test_iterations):
        results = long_pattern.longest_ordered_chunk_match_ratio(long_sequence)
