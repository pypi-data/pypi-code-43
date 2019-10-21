from astro_py.zodiac import zodiac
from flatlib import const

def FileCheck(fn):
    try:
        open(fn, "r")
        return 1
    except IOError:
        # print("Error: File " + fn + " does not appear to exist. (text are in a private repository)")
        return 0

class astro_py_text:
    def __init__(self, zodiac): #angles, houses, planets):
        self.zodiac = zodiac
    
    def text_zodiac(self):
        zodiac_text_array = []
        for i in self.zodiac:
            zt = zodiac_text(i)
            zodiac_text_array.append(zt)
        return zodiac_text_array
    
class zodiac_text:
    def __init__(self, zodiac):
        self.sign = zodiac.sign
        self.content = self.switch_zodiac(zodiac.id)
        
    def switch_zodiac(self, id):
        switcher = {
            const.ID_ARIES: self.text_belier(),
            const.ID_TAURUS: self.text_autre(),
            const.ID_GEMINI: self.text_autre(),
            const.ID_CANCER: self.text_autre(),
            const.ID_LEO: self.text_autre(),
            const.ID_VIRGO: self.text_autre(),
            const.ID_LIBRA: self.text_autre(),
            const.ID_SCORPIO: self.text_autre(),
            const.ID_SAGITTARIUS: self.text_autre(),
            const.ID_CAPRICORN: self.text_autre(),
            const.ID_AQUARIUS: self.text_autre(),
            const.ID_PISCES: self.text_autre(),
        }
        return switcher.get(id, '?')
    
    def text_belier(self):
        content = ''
        # Titre
        if(FileCheck('assets/zodiac_01_belier.dat')):
            f = open('assets/zodiac_01_belier.dat', 'r')
            content += f.read()
            f.close()
        # Livre KLEA
        if(FileCheck('assets/zodiac_01_belier_klea.dat')):
            f = open('assets/zodiac_01_belier_klea.dat', 'r')
            content += f.read()
            f.close()
        if(FileCheck('assets/zodiac_01_belier_klea_definition.dat')):
            f = open('assets/zodiac_01_belier_klea_definition.dat', 'r')
            content += f.read()
            f.close()
        return content
        
    def text_autre(self):
        return ''