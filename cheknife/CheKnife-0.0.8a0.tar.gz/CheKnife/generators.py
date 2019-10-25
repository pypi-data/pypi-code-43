class DNIGenerator(object):
    letter_mapping = {
        0: 'T', 1: 'R', 2: 'W', 3: 'A', 4: 'G', 5: 'M', 6: 'Y', 7: 'F', 8: 'P', 9: 'D', 10: 'X', 11: 'B', 12: 'N',
        13: 'J', 14: 'Z', 15: 'S', 16: 'Q', 17: 'V', 18: 'H', 19: 'L', 20: 'C', 21: 'K', 22: 'E'
    }

    def __init__(self, start=0, end=99999999):
        self.start = start
        self.end = end + 1

    def __call__(self, *args, **kwargs):
        for number in range(self.start, self.end):
            yield '{:08d}{}'.format(number, self.letter(number))

    def letter(self, number):
        return self.letter_mapping[number % 23]


class NIEGenerator(DNIGenerator):
    nie_letters = {'X': 0, 'Y': 1, 'Z': 2}

    def __init__(self, start=0, end=9999999):
        super(NIEGenerator, self).__init__(start, end)

    def __call__(self, *args, **kwargs):
        for number in range(self.start, self.end):
            for nie_letter, letter_value in self.nie_letters.items():
                nie_letter_seed = self.nie_letter_number(letter_value, number)
                yield '{}{:07d}{}'.format(nie_letter, number, self.letter(nie_letter_seed))

    def nie_letter_number(self, letter_value, number):
        number = '{}{:07d}'.format(letter_value, number)
        return int(number)
