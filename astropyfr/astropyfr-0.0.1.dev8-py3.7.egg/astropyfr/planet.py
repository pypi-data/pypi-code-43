from flatlibfr import const
# from flatlib.object import (GenericObject, Object)
from astropyfr.position import position
from astropyfr.component.my_timedelta import my_timedelta, my_timedelta_deg, my_timedelta_min

class planet:
    def __init__(self, planet, asc):
        # self._planet = planet
        self.id = planet.id
        # self.id_house = house.id
        self.sign = planet.sign
        self.sign_pos = str(my_timedelta(0, planet.signlon * 3600))
        # self.signlon = house.signlon
        pos = position(asc)
        id_by_asc = pos.switch_current_sign_to_id(planet.sign)
        self.pos_circle_360 = pos.position_circle_360_object(id_by_asc, planet.signlon)
        self.svg = 'assets/svg/planet/' + planet.id + '.svg'
        self.svg_degre = 'assets/svg/degre_min/' + str(my_timedelta_deg(0, planet.signlon * 3600)) + '.svg'
        self.svg_min = 'assets/svg/degre_min/' + str(my_timedelta_min(0, planet.signlon * 3600)) + '.svg'
        self.movement = planet.movement()
        self.sw_movement_is_retrograde = planet.isRetrograde()
        # No retrograde in book for node moon
        if (planet.id == const.NORTH_NODE or planet.id == const.SOUTH_NODE):
            self.sw_movement_is_retrograde = False
        
        #self.sw_movement_is_direct = planet.isDirect()
        #self.sw_movement_is_stationary = planet.isStationary()
        # self.sw_movement_is_fast = planet.isFast()