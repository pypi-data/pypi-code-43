from decklist.deck import Card, Deck


class DeckParsingError(Exception):
    pass


def parse_deck_string(deckstr):
    deck = Deck()
    for line in deckstr.splitlines():
        lenline = len(line)
        i = 0
        num = ''
        while i < lenline:
            if line[i].isdigit():
                num += line[i]
                i += 1
            else:
                break
        if line[i] == 'x' or line[i] == 'X':
            i += 1
        if not line[i].isspace():
            raise DeckParsingError(f'Poorly formatted line {line}')
        name = line[i:].strip()
        deck.add_card(Card(name=name, num=int(num)))
    return deck


def parse_deck_file(deckfile):
    with open(deckfile, 'r') as deckf:
        decks = deckf.read()
    return parse_deck_string(decks)
