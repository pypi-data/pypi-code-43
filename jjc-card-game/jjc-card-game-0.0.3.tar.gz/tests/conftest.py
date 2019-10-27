# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
import pytest

# --- Intra-Package Imports ---------------------------------------------------
from card_game.cards import CardDeck
from card_game.game import Game


def get_cards(card_indices):
    deck = CardDeck(shuffle=False)
    return [deck[i] for i in card_indices]


@pytest.fixture
def fixture_get_cards():
    return get_cards


def get_players(players, card_indices=None):
    players = Game(players).players
    if card_indices:
        cards = get_cards(card_indices)
        for i, player in enumerate(players):
            player.card = cards[i]
    return players


@pytest.fixture
def fixture_get_players():
    return get_players
