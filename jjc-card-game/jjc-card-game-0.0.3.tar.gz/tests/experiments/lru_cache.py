import functools


class Doubler:

    @functools.lru_cache()
    def double(self, num=None):
        print('func call', num)
        if num is None:
            return 0
        return num * 2


doubler = Doubler()
doubler.double()
doubler.double(2)
doubler.double(3)
doubler.double(2)  # Note how this lru cache kicks in
doubler.double()  # Here too

doub = Doubler()
doub.double(2)  # This instance has its own cache. Perfect
doub.double(3)