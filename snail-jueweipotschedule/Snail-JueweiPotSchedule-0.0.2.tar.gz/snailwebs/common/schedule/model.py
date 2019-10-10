import json
import os
import time
from snailwebs.common.schedule import *


MODEL_START_STATE = 0
MODEL_A1 = 1
MODEL_A2 = 2
MODEL_A3 = 3
MODEL_B = 4
MODEL_END_STATE = 5
MODEL_PROCESS_MIN = 6
MODEL_PROCESS_MAX = 7
MODEL_SCHEME = 8
MODEL_SCHEME_MARK_4 = 9
MODEL_SCHEME_MARK_5 = 10
MODEL_SCHEME_MARK_6 = 11
MODEL_SCHEME_MARK_7 = 12
MODEL_SCHEME_MARK_8 = 13
MODEL_END_MARK_0 = 14
MODEL_END_MARK_1 = 15
MODEL_END_MARK_2 = 16
MODEL_END_MARK_3 = 17
MODEL_END_MARK_4 = 18
MODEL_END_MARK_5 = 19
MODEL_END_MARK_6 = 20
MODEL_END_MARK_7 = 21
MODEL_END_MARK_8 = 22
MODEL_END_MARK_9 = 23
MODEL_WEIGHT = 24


class Model:
    """
    生成卤制排程模型 
    """
    
    def __init__(self, rounds=2):
        self.model = []
        self.rounds = rounds

    def generate(self):
        
        mm = []
        for i in range(0, len(default_model)):
            mm.append([0] + default_model[i])

        for i in range(self.rounds):
            for j in range(0, len(mm)):
                for j2 in range(0, len(default_model)):
                    m = mm[j] + [NEW] + default_model[j2]
                    mm.append(m)

        mmLEN = len(mm)

        print('当前模型数据的总量为: %s' % mmLEN)

        mm.append([0, STOP])

        for i in range(1, 9):
            mm.append([i, STOP])
            k = i + 1
            for j in range(1, mmLEN):

                if len(mm[j]) <= k:
                    continue

                if NEW == mm[j][k]:
                    continue

                if len(mm[j]) > 10:
                    if i == 6:
                        if (B == mm[j][k] and B == mm[j][k+1] and B == mm[j][k+2]) or (
                                A1 == mm[j][k] and A1 == mm[j][k+1] and A1 == mm[j][k+2]):
                            pass
                        else:
                            continue
                    elif i == 7:
                        if (B == mm[j][k] and B == mm[j][k + 1] and NEW == mm[j][k + 2]) or (
                                A1 == mm[j][k] and A1 == mm[j][k+1] and A1 == mm[j][k+2]):
                            pass
                        else:
                            continue
                    elif i == 8:
                        if (B == mm[j][k] and NEW == mm[j][k + 1]) or(
                                A1 == mm[j][k] and A1 == mm[j][k+1] and A1 == mm[j][k+2]):
                            pass
                        else:
                            continue

                m = [i] + mm[j][k:]

                # if m not in mm:
                mm.append(m)

        mmLEN = len(mm)

        print('当前模型数据的总量为: %s' % mmLEN)

        for i in range(0, mmLEN):
            size = len(mm[i])
            for j in range(1, size - 1):
                m = mm[i][0:size - j]

                if NEW == m[-1]:
                    continue

                # if m not in mm:
                mm.append(m)
            print('当前模型数据的总量为: %s' % len(mm))

        mmLEN = len(mm)

        print('当前模型数据的总量为: %s' % mmLEN)
        print('初始化完成。')

        # 处理模型数据
        print('开始处理模型数据...')
        stime = time.time()

        mkeys = {}
        for i in range(0, mmLEN):
            '''
            数据格式：[
                初始状态, A1, A2, A3, B, 结束状态, 最小工艺时间, 最大工艺时间,                                                     ( 0,  7)
                方案, 4H方案标志, 5H方案标志, 6H方案标志, 7H方案标志, 8H方案标志,                                                  ( 8, 13)
                第0圈标志, 第1圈标志, 第2圈标志, 第3圈标志, 第4圈标志, 第5圈标志, 第6圈标志, 第7圈标志, 第8圈标志, 第9圈标志,        (14, 23)
                权重(0-99)
            ]
            '''

            m = [0, 0, 0, 0, 0, 0, 0, 0, [], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 55]

            m[MODEL_START_STATE] = mm[i][0]
            m[MODEL_END_STATE] = mm[i][0]
            m[MODEL_PROCESS_MIN] = 0
            m[MODEL_PROCESS_MAX] = 0

            mkey = str(mm[i][0]) + ':'

            for j in range(1, len(mm[i])):
                if A1 == mm[i][j]:
                    m[MODEL_A1] += 1
                    m[MODEL_END_STATE] += 1
                    m[MODEL_PROCESS_MIN] += PROCESS_MIN_A1
                    m[MODEL_PROCESS_MAX] += PROCESS_MAX_A1

                    if 3 < m[MODEL_END_STATE]:
                        m[MODEL_WEIGHT] = 50

                elif A2 == mm[i][j]:
                    m[MODEL_A2] += 1
                    m[MODEL_END_STATE] += 1
                    m[MODEL_PROCESS_MIN] += PROCESS_MIN_A2
                    m[MODEL_PROCESS_MAX] += PROCESS_MAX_A2

                    if 4 > m[MODEL_END_STATE]:
                        m[MODEL_WEIGHT] = 50

                elif A3 == mm[i][j]:
                    m[MODEL_A3] += 1
                    m[MODEL_END_STATE] += 1
                    m[MODEL_PROCESS_MIN] += PROCESS_MIN_A3
                    m[MODEL_PROCESS_MAX] += PROCESS_MAX_A3
                elif B == mm[i][j]:
                    m[MODEL_B] += 1
                    m[MODEL_END_STATE] += 1
                    m[MODEL_PROCESS_MIN] += PROCESS_MIN_B
                    m[MODEL_PROCESS_MAX] += PROCESS_MAX_B
                elif NEW == mm[i][j]:
                    m[MODEL_END_STATE] = 0
                    m[MODEL_PROCESS_MIN] += PROCESS_NEW
                    m[MODEL_PROCESS_MAX] += PROCESS_NEW
                elif STOP == mm[i][j]:
                    m[MODEL_END_MARK_0] = 1
                    m[MODEL_END_MARK_0 + m[MODEL_START_STATE]] = 1

                m[MODEL_SCHEME].append(mm[i][j])
                mkey += '>' + mm[i][j]

            if mkey in mkeys:
                continue

            mkeys[mkey] = mkey

            if m[MODEL_START_STATE] >= 6 and mm[i][1] == A1:
                m[MODEL_END_STATE] -= m[MODEL_START_STATE]

            m[MODEL_END_MARK_0 + m[MODEL_END_STATE]] = 1

            if m[MODEL_END_STATE] >= 6:
                m[MODEL_END_MARK_0] = 1

                if m[MODEL_START_STATE] >= 6:
                    m[MODEL_WEIGHT] = 70
                else:
                    m[MODEL_WEIGHT] = 60

            if 240 > m[MODEL_PROCESS_MIN] or 270 > m[MODEL_PROCESS_MAX]:
                m[MODEL_SCHEME_MARK_8] = m[MODEL_SCHEME_MARK_7] = m[MODEL_SCHEME_MARK_6] = m[MODEL_SCHEME_MARK_5] = m[MODEL_SCHEME_MARK_4] = 1
            elif 300 > m[MODEL_PROCESS_MIN] or 330 > m[MODEL_PROCESS_MAX]:
                m[MODEL_SCHEME_MARK_8] = m[MODEL_SCHEME_MARK_7] = m[MODEL_SCHEME_MARK_6] = m[MODEL_SCHEME_MARK_5] = 1
            elif 360 > m[MODEL_PROCESS_MIN] or 390 > m[MODEL_PROCESS_MAX]:
                m[MODEL_SCHEME_MARK_8] = m[MODEL_SCHEME_MARK_7] = m[MODEL_SCHEME_MARK_6] = 1
            elif 420 > m[MODEL_PROCESS_MIN] or 450 > m[MODEL_PROCESS_MAX]:
                m[MODEL_SCHEME_MARK_8] = m[MODEL_SCHEME_MARK_7] = 1
            else:
                m[MODEL_SCHEME_MARK_8] = 1

            self.model.append(m)

            if i % 1000 == 0 and 30 < int(time.time() - stime):
                print('处理模型数据：%.2f%%' % (i/mmLEN*100))
                stime = time.time()

        print('处理模型数据：100%')
        print('生成模型数据完成。SIZE: %s' % (len(self.model)))

    def save(self):
        f = None
        try:
            f = open(os.path.dirname(__file__) + '/../../../model.json', mode='w', encoding='utf-8')
            f.write(json.dumps(self.model))
            print('保存成功。')
        finally:
            if f:
                f.close()

    def loads(self):
        f = None
        try:
            f = open(os.path.dirname(__file__) + '/../../../model.json', mode='r', encoding='utf-8')
            self.model = json.loads(f.read())
            print('加载成功。')
        finally:
            if f:
                f.close()

    def getModel(self):
        return self.model

    def print_model(self, index=0):
        i = 0
        for model in self.model:
            if index == model[MODEL_START_STATE]:
                print('初始状态为%s圈-%s: %s' % (index, i, model))
                i += 1






