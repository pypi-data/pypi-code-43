"""
    Export to json 
"""
import io
import json
from flatlibfr import const
from astro_py.angle import angle
from astro_py.house import house
from astro_py.zodiac import zodiac
from astro_py.planet import planet
from astro_py.text.zodiac_text import astro_py_text
# python >= 3.6
sw_astro_text = True
"""
try:
    from astro_py_text.astro_py_text import astro_py_text
except ModuleNotFoundError as err:
    sw_astro_text = False
    print(err)
    print("It's just a warning, the repository of astro_py_text is private")
"""     
class export:
    def __init__(self, angles, houses, planets):
        self.angles = self.set_angle(angles)
        self.houses = self.set_house(houses, angles[0])  # angles[0] = Ascendant
        self.zodiac = self.set_zodiac(angles[0]) # angles[0] = Ascendant
        self.planets = self.set_planet(planets, angles[0]) # angles[0] = Ascendant
        if (sw_astro_text):
            astro_text = astro_py_text(self.zodiac)
            self.zodiac_text = self.set_zodiac_text(astro_text)
        else:
            self.zodiac_text  = None
        
    def set_angle(self, angles):
        angle_array = []
        for i in angles:
            angle_array.append(angle(angle=i, asc=angles[0])) # angles[0] = Ascendant
        return angle_array
    
    def set_house(self, houses, asc):
        house_array = []
        for i in houses:
            house_array.append(house(house=i, asc=asc))
        return house_array
    
    def set_zodiac(self, asc):
        zodiac_array = []
        zodiac_array.append(zodiac(id=const.ID_ARIES, sign=const.ARIES, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_TAURUS, sign=const.TAURUS, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_GEMINI, sign=const.GEMINI, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_CANCER, sign=const.CANCER, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_LEO, sign=const.LEO, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_VIRGO, sign=const.VIRGO, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_LIBRA, sign=const.LIBRA, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_SCORPIO, sign=const.SCORPIO, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_SAGITTARIUS, sign=const.SAGITTARIUS, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_CAPRICORN, sign=const.CAPRICORN, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_AQUARIUS, sign=const.AQUARIUS, asc=asc))
        zodiac_array.append(zodiac(id=const.ID_PISCES, sign=const.PISCES, asc=asc))
        zodiac_array.sort(key=lambda x: x.id_by_asc)
        return zodiac_array

    def set_planet(self, planets, asc):
        planet_array = []
        for i in planets:
            planet_array.append(planet(planet=i, asc=asc))
        return planet_array

    def set_zodiac_text(self, astro_text):
        return astro_text.text_zodiac()

    def to_json(self):
        json_dumps = json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4, ensure_ascii=False)
        return json_dumps