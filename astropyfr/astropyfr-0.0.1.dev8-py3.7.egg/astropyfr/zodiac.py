from flatlibfr import const
from astropyfr.position import position

class zodiac:
    """ This class represents the zodiac """

    def __init__(self, id, sign, asc):
        """ Creates an zodiac class """
        self.id = id
        self.sign = sign
        self.symbol = self.switch_symbol(sign)
        self.element = self.switch_element(sign)
        self.svg = 'assets/svg/zodiac/' + sign + '.svg'
        # self.asc = asc
        pos = position(asc)
        self.id_by_asc = pos.switch_asc(id)
        self.pos_circle_360 = pos.position_circle_360_zodiac(id)

    def switch_symbol(self, sign):
        """ Font icon of the sign """
        switcher = {
            const.ARIES: '♈',
            const.TAURUS: '♉',
            const.GEMINI: '♊',
            const.CANCER: '♋',
            const.LEO: '♌',
            const.VIRGO: '♍',
            const.LIBRA: '♎',
            const.SCORPIO: '♏',
            const.SAGITTARIUS: '♐',
            const.CAPRICORN: '♑',
            const.AQUARIUS: '♒',
            const.PISCES: '♑'
        }
        return switcher.get(sign, '?')
    
    def switch_element(self, sign):
        """ Element of zodiac """
        switcher = {
            const.ARIES: 'Feu',
            const.TAURUS: 'Terre',
            const.GEMINI: 'Air',
            const.CANCER: 'Eau',
            const.LEO: 'Feu',
            const.VIRGO: 'Terre',
            const.LIBRA: 'Air',
            const.SCORPIO: 'Eau',
            const.SAGITTARIUS: 'Feu',
            const.CAPRICORN: 'Terre',
            const.AQUARIUS: 'Air',
            const.PISCES: 'Eau'
        }
        return switcher.get(sign, '?')