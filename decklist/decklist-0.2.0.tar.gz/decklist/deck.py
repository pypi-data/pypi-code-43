class Card:
    def __init__(self, name, num, owned=0, expansion=None):
        self.name = name
        self.num = num
        self.owned = owned
        self.expansion = expansion


class Deck:
    def __init__(self, name=None, cards=None):
        self.name = name
        self.cards = {}
        if cards is None:
            cards = []
        for card in cards:
            self.add_card(card)

    def add_card(self, card):
        if card.name in self.cards:
            self.cards[card.name].num += card.num
            self.cards[card.name].owned += card.owned
        else:
            self.cards[card.name] = card

    def format_deck(self, include_sets=False):
        deckstr = ''
        for card in sorted(self.cards, key=str.lower):
            deckstr += f'{self.cards[card].num}x {self.cards[card].name}'
            if include_sets:
                deckstr += f' [{self.cards[card].expansion}]'
            deckstr += '\n'
        return deckstr.strip()

    def print_deck(self):
        print(self.format_deck())
