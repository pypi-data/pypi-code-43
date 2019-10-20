from random import randint
class Circle:
    def getCorners(self):
        return [] if randint(0,1) == 0 else [1]