import pytest
from card_game.game import Game


@pytest.mark.parametrize('params', [  # players, player count, raise error
    (2, 2, False),
    ('dick jane'.split(), 2, False),
    ('simple string', None, True),
])
def test_game_init(params):
    players, expected_player_count, expected_raise_error = params
    try:
        game = Game(players=players, manual_draw=False)
        actual_player_count = len(game.players)
        assert actual_player_count == expected_player_count
        actual_raise_error = False
    except TypeError:
        actual_raise_error = True
    assert actual_raise_error == expected_raise_error


def test_play_first_round():
    game = Game(2)
    game.play_a_round(1)


def test_game_winner():
    player_statuses = [
        ['n']*5 + ['w']*11,
        ['w']*10 + ['n']*6,
    ]
    game = Game(2)
    for index, player in enumerate(game.players):
        player._results = player_statuses[index]

    expected_winner_index = 0
    actual_winner_index = game.check_for_winner().index
    assert actual_winner_index == expected_winner_index
