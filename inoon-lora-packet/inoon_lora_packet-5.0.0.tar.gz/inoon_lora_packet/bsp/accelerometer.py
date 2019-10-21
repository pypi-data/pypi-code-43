class BMA250E():
    mg_per_step = {
        1: 3.91,
        2: 7.81,
        3: 15.63,
        4: 31.25,
    }

    @classmethod
    def gravity(cls, sensitivity, raw_value):
        return round(cls.mg_per_step[sensitivity] * raw_value / 1000, 5)


class BMA280():
    mg_per_step = {
        1: 0.244,
        2: 0.488,
        3: 0.977,
        4: 1.953,
    }

    @classmethod
    def gravity(cls, sensitivity, raw_value):
        return round(cls.mg_per_step[sensitivity] * raw_value / 1000, 5)
