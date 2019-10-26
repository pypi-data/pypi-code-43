import pytest
import collections
from card_game.player import Player

InputResult = collections.namedtuple('InputResult', 'card_indices round_results score')


@pytest.mark.parametrize('params', [
    InputResult([1, 40, 20], 'p w n'.split(), [0, 2, 0]),
    InputResult([5, 40, 20], 'n w n'.split(), [0, 2, 0]),
    InputResult([1, 1, 1], 'p p p'.split(), [0, 0, 0]),
    InputResult([30, 6, 8], 'w n n'.split(), [2, 0, 0]),
])
def test_first_round_scoring(fixture_get_players, params):

    # setup
    card_indices, expected_result, expected_score_results = params
    player_count = len(card_indices)
    players = fixture_get_players(player_count, card_indices)
    cards = [player.card for player in players]

    # find check_for_winner / penalties
    for player in players:
        player.determine_round_status(cards)

    # assert
    actual_result = [player.round_status for player in players]
    assert actual_result == expected_result

    # test score value
    actual_score_values = [player.score for player in players]
    assert actual_score_values == expected_score_results


def test_cumulative_score():
    """
    Create two players
    Give them results.
    :return:
    """
    player = Player(0, 'bill')
    player._results = 'p w n w'.split()
    expected_cumulative_scores = [0, 2, 2, 4]
    rounds = len(expected_cumulative_scores)
    actual_cumulative_score = [
        player.get_score(round_num)
        for round_num in range(1, rounds + 1)
    ]
    assert actual_cumulative_score == expected_cumulative_scores


def test_previous_score():
    player = Player(0)
    player._results = ['w']
    round = 1
    assert player.get_score(0) == 0  # previous score
    assert player.get_score(round-1) == 0  # ditto
    assert player.score == 2  # round 1 score
    assert player.get_score(1) == 2  # ditto

