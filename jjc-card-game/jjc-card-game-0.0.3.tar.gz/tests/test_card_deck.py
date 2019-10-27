import pytest
import random
from card_game.cards import Card, CardDeck


def test_multi_param_lt_compare():
    smaller = (10, 2)
    larger = (20, 1)
    assert smaller < larger


def test_best_card(fixture_get_cards):
    cards = fixture_get_cards([1, 20, 10])
    print(cards)
    print(max(cards))


def test_compare_two_equal_cards():
    ranks, suits = CardDeck(shuffle=False).ranks_and_suits

    # Two lists containing same cards sorted compare equal
    deck1 = [Card(ranks[i], suits[i], ranks, suits) for i in range(4)]
    deck2 = list(deck1)
    print('deck:', deck1)
    assert deck1 == deck2

    # Two list containing same cards in different order compare unequal
    random.shuffle(deck2)
    print('orig deck', deck1)
    print('shuffled deck:', deck2)
    assert deck1 != deck2
    print("are the decks the same?", deck1 == deck2)

    # Sort the random cards, then compare again. Should compare equal
    deck2.sort()
    print('sorted deck:', deck2)
    assert deck1 == deck2


# @pytest.mark.parametrize("shuffle", [True, False])
# def test_card_deck(shuffle):
#     deck = CardDeck(shuffle)
#     assert len(deck) == 56
#     actual_cards = tuple(deck.cards)
#     sorted_cards = tuple(sorted(deck))
#     print('actual', type(actual_cards), actual_cards)
#     print('sorted', type(sorted_cards), sorted_cards)
#     assert (sorted_cards == deck.cards) != shuffle


def test_prop_ranks_and_methods():
    ranks, suits = CardDeck().ranks_and_suits
    print()
    print(ranks)
    print(suits)
    assert ranks == 'penalty 2 3 4 5 6 7 8 9 10 jack queen king ace'.split()
    assert suits == ['clubs', 'diamonds', 'hearts', 'spades']


# def test_compare_cards(ranks, suits):
#     ranks, suits = CardDeck().ranks_and_suits
#     card = Card(ranks[1], suits[1], ranks, suits)
#     # high_card = Card(ranks[3], suits[0], ranks, suits)
#     print()
#     print(card, card.indices())


# @pytest.mark.parametrize("ranks,suits", [
#     list(CardDeck().ranks_and_suits),
#     ['p 2 3 k'.split(), ['lower suit', 'higher suit']],
# ])
# def test_compare_cards(ranks, suits):
#     # ranks = 'p 2 3 k'.split()
#     # suits = ['lower suit', 'higher suit']
#     small_card = Card(ranks[1], suits[1], ranks, suits)
#     high_card = Card(ranks[3], suits[0], ranks, suits)
#     print()
#     print('small card:', small_card)
#     print('high card:', high_card)
#     assert small_card == small_card
#     assert small_card != high_card
#     # assert small_card < high_card
#     assert high_card > small_card


def test_shuffled_lists():
    nums = list(range(5))
    nums2 = list(nums)
    assert nums is not nums2
    assert nums == nums2

    random.shuffle(nums)
    assert nums != nums2

    nums.sort()
    assert nums == nums2
