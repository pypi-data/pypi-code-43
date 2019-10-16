import decklist

import unittest

basic_deck = """1x Archon of Valor's Reach
2x Bayou
2x Birchlore Rangers
1x Cavern of Souls
2x Craterhoof Behemoth
2x Dryad Arbor
1x Elvish Mystic
4x Elvish Visionary
2x Forest
1x Fyndhorn Elves
4x Gaea's Cradle
4x Glimpse of Nature
4x Green Sun's Zenith
4x Heritage Druid
1x Llanowar Elves
3x Natural Order
4x Nettle Sentinel
1x Pendelhaven
4x Quirion Ranger
1x Reclamation Sage
1x Savannah
1x Scavenging Ooze
3x Windswept Heath
4x Wirewood Symbiote
3x Wooded Foothills"""

class TestParse(unittest.TestCase):

    def test_basic(self):
        deck = decklist.parse_deck_string(basic_deck)
        self.assertEqual(deck.format_deck(), basic_deck)


if __name__ == '__main__':
    unittest.main()

