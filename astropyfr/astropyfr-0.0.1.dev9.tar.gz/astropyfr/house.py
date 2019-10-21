from flatlibfr import const
from astropyfr.position import position
from astropyfr.component.my_timedelta import my_timedelta

class house:
    def __init__(self, house, asc):
        #self._house = house
        self.id = self.switch_house(house_id=house.id)
        # self.id_house = house.id
        self.sign = house.sign
        self.sign_pos = str(my_timedelta(0, house.signlon * 3600))
        # self.signlon = house.signlon
        pos = position(asc)
        id_by_asc = pos.switch_current_sign_to_id(house.sign)
        self.pos_circle_360 = pos.position_circle_360_object(id_by_asc, house.signlon)
        self.svg = 'assets/svg/house/' + str(self.id) + '.svg'

    def switch_house(self, house_id):
        """ Switch case for give the id of house """
        switcher = {
            const.HOUSE1: 1,
            const.HOUSE2: 2,
            const.HOUSE3: 3,
            const.HOUSE4: 4,
            const.HOUSE5: 5,
            const.HOUSE6: 6,
            const.HOUSE7: 7,
            const.HOUSE8: 8,
            const.HOUSE9: 9,
            const.HOUSE10: 10,
            const.HOUSE11: 11,
            const.HOUSE12: 12,
        }
        return switcher.get(house_id, '?')