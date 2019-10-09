import os
import json

A1 = 'A1'
A2 = 'A2'
A3 = 'A3'
B = 'B'
NEW = '新'
STOP = '停'

default_model = [
    [A1, A1, A1, A2, A2, A3, B, B, B],
    [A1, A1, A1, A2, A2, A2, B, B, B],
    [A1, A1, A1, A2, A3, A3, B, B, B],
    [A1, A1, A1, A3, A3, A3, B, B, B],
    [A1, A1, A1, A2, A2, A3, B, B],
    [A1, A1, A1, A2, A2, A2, B, B],
    [A1, A1, A1, A2, A3, A3, B, B],
    [A1, A1, A1, A3, A3, A3, B, B],
    [A1, A1, A1, A2, A2, A3, B],
    [A1, A1, A1, A2, A2, A2, B],
    [A1, A1, A1, A2, A3, A3, B],
    [A1, A1, A1, A3, A3, A3, B],
    [A1, A1, A1, A2, A2, A3],
    [A1, A1, A1, A2, A2, A2],
    [A1, A1, A1, A2, A3, A3],
    [A1, A1, A1, A3, A3, A3]
]

PROCESS_MAX_A1 = 65
PROCESS_MIN_A1 = 65
PROCESS_MAX_A2 = 53
PROCESS_MIN_A2 = 48
PROCESS_MAX_A3 = 58
PROCESS_MIN_A3 = 58
PROCESS_MAX_B = 38
PROCESS_MIN_B = 30
PROCESS_NEW = 30
PROCESS_START = 15

# 读配置文件
SETTING = None
try:
    f = open(os.path.dirname(__file__) + '/../../../setting.json', mode='r', encoding='utf-8')
    SETTING = json.loads(f.read())

    for product in SETTING['product']:

        ptype = product['type']
        processTime = int(product['processTime'])

        if A1 == ptype:
            if PROCESS_MAX_A1 < processTime:
                PROCESS_MAX_A1 = processTime

            if PROCESS_MIN_A1 > processTime:
                PROCESS_MIN_A1 = processTime

        elif A2 == ptype:
            if PROCESS_MAX_A2 < processTime:
                PROCESS_MAX_A2 = processTime

            if PROCESS_MIN_A2 > processTime:
                PROCESS_MIN_A2 = processTime

        elif A3 == ptype:
            if PROCESS_MAX_A3 < processTime:
                PROCESS_MAX_A3 = processTime

            if PROCESS_MIN_A3 > processTime:
                PROCESS_MIN_A3 = processTime

        elif B == ptype:
            if PROCESS_MAX_B < processTime:
                PROCESS_MAX_B = processTime

            if PROCESS_MIN_B > processTime:
                PROCESS_MIN_B = processTime
finally:
    if f:
        f.close()

__all__ = ['A1', 'A2', 'A3', 'B', 'STOP', 'NEW',
           'SETTING',
           'PROCESS_MAX_A1', 'PROCESS_MAX_A2', 'PROCESS_MAX_A3', 'PROCESS_MAX_B', 'PROCESS_MIN_A1',
           'PROCESS_MIN_A2', 'PROCESS_MIN_A3', 'PROCESS_MIN_B', 'PROCESS_NEW', 'PROCESS_START',
           'default_model']







