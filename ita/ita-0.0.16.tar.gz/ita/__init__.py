# -*- encoding: utf-8 -*-

from . import array
from . import plot
from . import bench
from . import excheck

def lifegame_glider():
    return [[0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,0],
            [0,0,0,0,1,0,0,0],
            [0,0,0,0,0,1,0,0],
            [0,0,0,0,0,0,0,0]]

def lifegame_acorn():
     # Corderman's Acorn
    image = array.make2d(60,80)
    x = 60
    y = 30
    for i in [[0,1],[1,3],[2,0],[2,1],[2,4],[2,5],[2,6]]:
        image[y + i[0]][x + i[1]] = 1
    return image

import random as rnd

# 身長体重データ疑似生成用
def gen_hw_data():
    s = rnd.randint(0,1)
    h = int(rnd.gauss(155+s*18, 10))
    t = rnd.randint(0,1)
    wd = (h/100) ** 2 * (19+3*t)
    w = int(wd + rnd.betavariate(2,10) * 200 - 15)
    return (h,w)

# バネの延びデータ疑似生成用
def gen_spring_data():
    w = rnd.randint(0,200)
    l = int(2 * w * rnd.gauss(1, 0.1))
    return (w,l)


