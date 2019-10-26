import pytest
from card_game.game import Game


@pytest.mark.parametrize('player_count', [2, 3, 4])
def test_smoke_test(player_count):
    game = Game(player_count)
    game.play()
    print()
    print(game.check_for_winner())
    assert game.check_for_winner() is not None
