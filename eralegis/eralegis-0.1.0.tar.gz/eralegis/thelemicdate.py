import time
from datetime import date

from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos


def now():
    """ Função não recebe parametros
    :return: a data thelemica atual
    """
    # Era Vulgar Year
    ev_year = int(date.today().strftime('%Y'))

    # Whole Years since March Equinox 1904
    ev_years_total = ev_year - 1904

    # New Aeon "generation" of 22 years
    ciclo_i = ev_years_total // 22

    # // Years in the current cycle
    ciclo_ii = ev_year - 1904 - (ciclo_i * 22)

    numerals = ['0', 'i', 'ii', 'iii', 'iv',
                'v', 'vi', 'vii', 'viii', 'ix',
                'x', 'xi', 'xii', 'xiii', 'xiv',
                'xv', 'xvi', 'xvii', 'xviii', 'xix',
                'xx', 'xxi', 'xxii']

    signs = {'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
             'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
             'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒',
             'Pisces': '♓'}

    dies = ['Lunae', 'Martis', 'Mercurii', 'Jovis',
            'Veneris', 'Saturnii', 'Solis']

    # New Aeon year
    na_year = numerals[ciclo_ii].upper() + ':' + numerals[ciclo_i]

    ev_weekday = date.today().weekday()
    ev_today = str(date.today().strftime('%Y/%m/%d'))
    ev_time = str(time.strftime('%H:%M'))

    na_date = Datetime(ev_today, ev_time, '-03:00')
    pos = GeoPos('23s39', '46w32')
    chart = Chart(na_date, pos)

    sun = chart.getObject(const.SUN)
    solis = str(sun).split(' ')
    solis_sign = solis[1]
    solis_arc = solis[2].split(':')[0].replace('+', '')

    moon = chart.get(const.MOON)
    luna = str(moon).split(' ')
    luna_sign = luna[1]
    luna_arc = luna[2].split(':')[0].replace('+', '')

    return (f'☉ in {solis_arc}º {signs[solis_sign]} '
            f'☽ in {luna_arc}º {signs[luna_sign]} '
            f'Dies {dies[ev_weekday]} '
            f'Anno {na_year} æræ novæ')


if __name__ == '__main__':
    hoje = now()
    print(hoje)
