"""Card and Deck classes"""

import collections
import random
import functools


@functools.total_ordering
class Card(collections.namedtuple('CardTuple', 'rank suit ranks suits')):
    """
    Card objects represent a single playing card.

    Compares to other Card objects. All arguments should be lower case.
    Capitalization is handled by repr and str dunder method. ranks and
    suits arguments should be sorted in ascending value.

    :param rank: string - card number or face value (e.g. '9' or 'jack')
    :param suit: string - card suit (e.g. 'diamonds' or 'clubs')
    :param ranks: list of strings - all avail card number and face values
    :param suits: list of strings - all avail card deck suits.
    """

    @property
    def indices(self):
        """
        :return: tuple integers, representing the value of this card
        """
        return self.ranks.index(self.rank), self.suits.index(self.suit)

    def __lt__(self, other):
        return self.indices < other.indices

    def __eq__(self, other):
        return self.indices == other.indices

    def __repr__(self):
        return f'Card({self.rank[0]}, {self.suit[0]})'

    def __str__(self):
        if self.rank[0] == 'p':
            return 'Penalty Card!'
        return f'{self.rank.title()} of {self.suit.title()}'


class CardDeck:
    """
    CardDeck objects represent a deck of Card objects.

    Choose shuffled or unshuffled.
    """

    def __init__(self, shuffle=True):
        ranks, suits = self.ranks_and_suits
        self.cards = [
            Card(rank, suit, ranks, suits)
            for rank in ranks
            for suit in suits
        ]
        if shuffle:
            random.shuffle(self)  # in-place shuffle

    @property
    def ranks_and_suits(self):
        """
        Tuples of lists: ranks and suits, each listed in ascending value.
        """
        ranks = 'penalty jack queen king ace'.split()
        ranks[1:1] = [str(val) for val in range(2, 11)]  # insert after penalty
        suits = 'clubs diamonds hearts spades'.split()
        return ranks, suits

    def draw_card(self):
        """
        Remove and return the top card from the deck.

        :return: Card object
        """
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]

    def __setitem__(self, key, value):
        self.cards[key] = value


if __name__ == '__main__':
    help(Card)
