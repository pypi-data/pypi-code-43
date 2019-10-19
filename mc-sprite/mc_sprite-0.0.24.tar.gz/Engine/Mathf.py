import math
from Timer.Time import Time
class Mathf(object):
    @staticmethod
    def Lerp(a: float, b: float, t: float):
        if t <= 0.0:
            return a;
        elif t >= 1.0:
            return b;
        return t * b + (1.0 - t) * a
    @staticmethod
    def PingPong(t: float, length: int):
        if int(t)%2==0:
            return t % length
        else:
            return length-(t % length)
        pass
    @staticmethod
    def Clamps(value: float, min: float, max: float):
        while value>=min and value<=max:
            if value < min:
                value += min
            elif value > max:
                value -= max
        return value
        pass
    @staticmethod
    def TupSub(tup1: tuple,tup2: tuple):
        #print(tup1,tup2)
        return(tup1[0]-tup2[0],tup1[1]-tup2[1])
    @staticmethod
    def MySort(A,B):
        if A>B:
            return 1
        elif A<B:
            return -1
        else:
            return 0
