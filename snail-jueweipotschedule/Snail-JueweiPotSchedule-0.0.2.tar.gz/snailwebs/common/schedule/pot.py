import random
import copy
from snailwebs.common.schedule import *
from snailwebs.common.schedule.model import Model
from ortools.linear_solver import pywraplp


# 卤锅圈次数量[0..8]
BOILER_STATE_LEN = 9
PRODUCT_TYPE_COUNT = 4
# 出锅间距
OUT_BOILER_INTERVAL = 5


class Schedule:
    """
    大件班排程
    """

    def __init__(self, types=[4, 5]):
        self.schemesMark = types[1]
        self.schemesMaxTime = self.schemesMark * 60
        self.boilerSStates = None
        self.boilerEStateCount = None
        self.batchDatas = [0, 0, 0, 0]
        self.result = None
        self.realitySchemesData = []
        self.productScheduleData = None
        self.productData = None

        model = Model()
        model.loads()
        m = model.getModel()

        self.models = []

        for i in range(0, len(types)):
            model = []
            for j in range(0, len(m)):
                if m[j][5 + types[i]]:
                    model.append(m[j])
            self.models.append(model)
            print('Model COUNT: %s' % (len(model)))

        print('初始化完成。')

    def get_product_data(self):
        return self.productData

    def set_boiler_s_states(self, state=[]):
        self.boilerSStates = state

    def get_boiler_s_states(self):
        return self.boilerSStates

    def set_boiler_e_state_count(self, counts=[]):
        self.boilerEStateCount = counts

    def get_boiler_e_state_count(self):
        return self.boilerEStateCount

    def chooseSchemes(self, batchs=[[0,0,0,0],[0,0,0,0]]):

        batchCount = len(batchs)

        if(batchCount < 2):
            return

        for b in batchs:
            if PRODUCT_TYPE_COUNT != len(b):
                return

        batchs = copy.deepcopy(batchs)

        # 生成卤锅方案数据
        for i in range(0, batchCount):
            schemes = []
            for j in range(0, len(self.boilerSStates)):
                for k in range(0, len(self.models[i])):
                    if self.boilerSStates[j] == self.models[i][k][0]:
                        schemes.append([j] + self.models[i][k])
            self.realitySchemesData.append(schemes)

        result = None

        for i in range(0, batchCount):
            result = self.__computeSchemes(batchs[i], self.realitySchemesData[i], i)

            if i < batchCount - 1:

                result = result['schemesData']
                for j in range(0, len(result)):
                    for k in range(len(self.realitySchemesData[i + 1])):
                        if STOP == result[j][9][-1]:
                            continue

                        if len(self.realitySchemesData[i + 1][k][9]) >= len(result[j][9]):

                            isStartWith = True

                            for n in range(len(result[j][9])):
                                if self.realitySchemesData[i + 1][k][9][n] != result[j][9][n]:
                                    isStartWith = False
                                    break

                            if isStartWith:
                                self.realitySchemesData[i + 1][k][25] = 90

                for j in range(0, len(batchs[i])):
                    self.batchDatas[j] = batchs[i+1][j] = batchs[i][j] + batchs[i+1][j]

        self.result = result
        return self.result

    def __computeSchemes(self, productDatas, realitySchemeData, batchIndex):

        realitySchemeCount = len(realitySchemeData)
        boilerCount = len(self.boilerSStates)

        self.__disorganize(realitySchemeData)

        X = [[]] * realitySchemeCount
        # 产能软性约束的正负误差项
        Y = [[]] * (2 * len(productDatas))
        # 留锅软性约束的正负误差项
        Y2 = [[]] * 2 * BOILER_STATE_LEN
        # 权重软性约束的正负误差项
        Y3 = None

        solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        objective = solver.Objective()

        for i in range(0, realitySchemeCount):
            X[i] = solver.IntVar(0.0, 1, ('x' + str(i)))

        for i in range(0, len(Y)):
            Y[i] = solver.NumVar(0.0, solver.infinity(), ('y' + str(i)))
            objective.SetCoefficient(Y[i], 1)

        for i in range(0, len(Y2)):
            Y2[i] = solver.NumVar(0.0, solver.infinity(), ('yy' + str(i)))
            objective.SetCoefficient(Y2[i], 1)

        Y3 = solver.NumVar(0.0, solver.infinity(), ('yyy' + str(i)))
        objective.SetCoefficient(Y3, 1)

        # 设置产能的约束
        for i in range(0, len(productDatas)):
            constraint = solver.Constraint(productDatas[i], productDatas[i])

            for j in range(0, realitySchemeCount):
                constraint.SetCoefficient(X[j], realitySchemeData[j][i + 2])

            constraint.SetCoefficient(Y[i], 1)
            constraint.SetCoefficient(Y[i + 1], -1)

        # 设置卤锅预留的约束
        if batchIndex > 0:
            for i in range(BOILER_STATE_LEN):
                if 0 >= self.boilerEStateCount[i]:
                    continue

                constraint = solver.Constraint(self.boilerEStateCount[i], self.boilerEStateCount[i])

                for j in range(0, realitySchemeCount):
                    constraint.SetCoefficient(X[j], realitySchemeData[j][i + 15])

                constraint.SetCoefficient(Y2[i], 1)
                constraint.SetCoefficient(Y2[i + 1], -1)

        # 设置每口卤锅基于初始状态只能选择一种方案的约束
        for i in range(0, boilerCount):
            constraint = solver.Constraint(1, 1)

            for j in range(0, realitySchemeCount):
                if i == realitySchemeData[j][0]:
                    constraint.SetCoefficient(X[j], 1)

        # 设置权重的约束
        constraint = solver.Constraint((boilerCount * 55 + boilerCount * 99) / 2, boilerCount * 99)

        for i in range(0, realitySchemeCount):
            constraint.SetCoefficient(X[i], realitySchemeData[i][25])

        constraint.SetCoefficient(Y3, 1)

        objective.SetMinimization()

        result_status = solver.Solve()
        assert result_status == pywraplp.Solver.OPTIMAL

        result = {
            'solver': {
                'variables': solver.NumVariables(),
                'constraints': solver.NumConstraints(),
                'value': solver.Objective().Value()
            },
            'schemesData': []
        }

        for i in range(0, realitySchemeCount):
            if X[i].solution_value() > 0:
                result['schemesData'].append(realitySchemeData[i])

        return result

    def __disorganize(self, realitySchemeData):

        count = len(realitySchemeData) - 1

        for i in range(0, 100):
            l = random.randint(0, count)
            r = random.randint(0, count)
            tem = realitySchemeData[l]
            realitySchemeData[l] = realitySchemeData[r]
            realitySchemeData[r] = tem

    def schedule(self, batchOrders=[[],[]]):

        # 第一步：按分类统计数据及整理
        batchs = [[0, 0, 0, 0], [0, 0, 0, 0]]

        pTypeOrders = {}

        for i in range(len(batchOrders)):
            for order in batchOrders[i]:
                for j in range(len(SETTING['product'])):
                    product = copy.deepcopy(SETTING['product'][j])
                    product['batchIndex'] = i + 1

                    if order['id'] == product['id']:
                        if A1 == product['type']:
                            batchs[i][0] += order['count']
                        if A2 == product['type']:
                            batchs[i][1] += order['count']
                        if A3 == product['type']:
                            batchs[i][2] += order['count']
                        if B == product['type']:
                            batchs[i][3] += order['count']

                        if product['type'] in pTypeOrders:
                            pTypeOrders[product['type']].append({'id': order['id'], 'count': order['count'], 'product': product})
                        else:
                            pTypeOrders[product['type']] = [{'id': order['id'], 'count': order['count'], 'product': product}]

        self.productData = copy.deepcopy(pTypeOrders)

        # 第二步：选择方案
        self.chooseSchemes(batchs)

        schemesData = self.result['schemesData']

        # 第三步：按方案进行排程
        self.productScheduleData = [None] * len(schemesData)

        PRODUCT_NEW = {'id': 'NEW', 'name': '熬制卤水', 'shortName': '熬卤水', 'type': NEW, 'processTime': PROCESS_NEW, 'sort': 0, 'batchIndex': 0}

        maxLen = 0

        for scheme in schemesData:
            if len(scheme[9]) > maxLen:
                maxLen = len(scheme[9])

        for i in range(maxLen):
            for j in range(len(schemesData)):

                schemes = schemesData[j]

                if not self.productScheduleData[j]:
                    self.productScheduleData[j] = {'schemes': schemes, 'totalTime': 0, 'eIndex': schemes[6], 'sTime': 0, 'markTime': 0, 'schedule': []}

                schedule = self.productScheduleData[j]['schedule']

                if i >= len(schemes[9]):
                    continue

                ptype = schemes[9][i]

                isValid = False
                if NEW == ptype:
                    schedule.append(PRODUCT_NEW)
                    self.productScheduleData[j]['totalTime'] += PRODUCT_NEW['processTime']
                    isValid = True
                elif ptype in pTypeOrders:
                    for pTypeOrder in pTypeOrders[ptype]:
                        if pTypeOrder['count'] > 0:
                            schedule.append(pTypeOrder['product'])
                            self.productScheduleData[j]['totalTime'] += pTypeOrder['product']['processTime']
                            pTypeOrder['count'] -= 1
                            isValid = True
                            break

                if not isValid:
                    processTime = 0
                    if A1 == ptype:
                        processTime = PROCESS_MAX_A1
                    elif A2 == ptype:
                        processTime = PROCESS_MAX_A2
                    elif A3 == ptype:
                        processTime = PROCESS_MAX_A3
                    elif B == ptype:
                        processTime = PROCESS_MAX_B

                    schedule.append({'id': None, 'name': ptype, 'shortName': ptype, 'type': ptype, 'processTime': processTime, 'sort': 0})
                    self.productScheduleData[j]['totalTime'] += processTime


        # 第四步：优化排产
        # 处理多余A2产品
        if A2 in pTypeOrders:
            # 在方案中多余的A3中生产超出方案的A2产品
            for pTypeOrder in pTypeOrders[A2]:
                if pTypeOrder['count'] > 0:
                    for productSchedule in self.productScheduleData:
                        for i in range(len(productSchedule['schedule'])):
                            if A3 == productSchedule['schedule'][i]['name']:
                                productSchedule['schedule'][i] = pTypeOrder['product']
                                productSchedule['totalTime'] += pTypeOrder['product']['processTime']
                                pTypeOrder['count'] -= 1
                                break
            # 尽量在短线方案后生产超出方案的产品
            for i in range(self.batchDatas[1]):  # 循环最大次量数
                for pTypeOrder in pTypeOrders[A2]:
                    if pTypeOrder['count'] > 0:
                        for round in [1, 2]:  # 进行两轮优化
                            for productSchedule in self.productScheduleData:
                                # 排程中间存在空，则不适合在其后排产超出方案的产品
                                hasNone = False

                                for product in productSchedule['schedule']:
                                    if not product['id']:
                                        hasNone = True

                                if hasNone:
                                    continue

                                if 1 == round and productSchedule['totalTime'] > self.schemesMaxTime * 0.5:
                                    continue

                                if 3 <= productSchedule['eIndex'] and 6 > productSchedule['eIndex']:
                                    productSchedule['schedule'].append(pTypeOrder['product'])
                                    pTypeOrder['count'] -= 1
                                    productSchedule['eIndex'] += 1

        # 处理多余A3产品
        if A3 in pTypeOrders:
            # 在方案中多余的A2中生产超出方案的A3产品
            for pTypeOrder in pTypeOrders[A3]:
                if pTypeOrder['count'] > 0:
                    for productSchedule in self.productScheduleData:
                        for i in range(len(productSchedule['schedule'])):
                            if A2 == productSchedule['schedule'][i]['name']:
                                productSchedule['schedule'][i] = pTypeOrder['product']
                                productSchedule['totalTime'] += pTypeOrder['product']['processTime']
                                pTypeOrder['count'] -= 1
                                break
            for i in range(self.batchDatas[2]):
                for pTypeOrder in pTypeOrders[A3]:
                    if pTypeOrder['count'] > 0:
                        for round in [1, 2]:  # 进行两轮优化
                            for productSchedule in self.productScheduleData:
                                hasNone = False

                                for product in productSchedule['schedule']:
                                    if not product['id']:
                                        hasNone = True

                                if hasNone:
                                    continue

                                if 1 == round and productSchedule['totalTime'] > self.schemesMaxTime * 0.5:
                                    continue

                                if 3 <= productSchedule['eIndex'] and 6 > productSchedule['eIndex']:
                                    productSchedule['schedule'].append(pTypeOrder['product'])
                                    pTypeOrder['count'] -= 1
                                    productSchedule['eIndex'] += 1

        # 处理多余B产品
        if B in pTypeOrders:
            for i in range(self.batchDatas[3]):
                for pTypeOrder in pTypeOrders[B]:
                    if pTypeOrder['count'] > 0:
                        for round in [1, 2]:  # 进行两轮优化
                            for productSchedule in self.productScheduleData:
                                hasNone = False

                                for product in productSchedule['schedule']:
                                    if not product['id']:
                                        hasNone = True

                                if hasNone:
                                    continue

                                if 1 == round and productSchedule['totalTime'] > self.schemesMaxTime * 0.5:
                                    continue

                                if 6 <= productSchedule['eIndex'] and 9 > productSchedule['eIndex']:
                                    productSchedule['schedule'].append(pTypeOrder['product'])
                                    productSchedule['totalTime'] += pTypeOrder['product']['processTime']
                                    pTypeOrder['count'] -= 1
                                    productSchedule['eIndex'] += 1

        # 处理多余A1产品
        if A1 in pTypeOrders:
            for i in range(self.batchDatas[0]):
                for j in [3, 9, 0, 8, 7, 6]:
                    for pTypeOrder in pTypeOrders[A1]:
                        if pTypeOrder['count'] > 0:

                            isFinished = False

                            for round in [1, 2]:  # 进行两轮优化
                                for productSchedule in self.productScheduleData:
                                    hasNone = False

                                    for product in productSchedule['schedule']:
                                        if not product['id']:
                                            hasNone = True

                                    if hasNone:
                                        continue

                                    if 1 == round and productSchedule['totalTime'] > self.schemesMaxTime * 0.5:
                                        continue

                                    if 3 == j:
                                        pass
                                    elif j == productSchedule['eIndex']:
                                        productSchedule['schedule'].append(PRODUCT_NEW)
                                        productSchedule['totalTime'] += PRODUCT_NEW['processTime']
                                        productSchedule['eIndex'] = 0
                                    else:
                                        continue

                                    while 3 > productSchedule['eIndex']:
                                        productSchedule['schedule'].append(pTypeOrder['product'])
                                        productSchedule['totalTime'] += pTypeOrder['product']['processTime']
                                        pTypeOrder['count'] -= 1
                                        productSchedule['eIndex'] += 1

                                        if pTypeOrder['count'] <= 0:
                                            isFinished = True
                                            break

                                    if isFinished:
                                        break
                                if isFinished:
                                    break
                            if isFinished:
                                break

        # 处理待排产
        for productSchedule in self.productScheduleData:
            # 处理尾部
            pLen = len(productSchedule['schedule'])
            for i in range(1, pLen):
                if not productSchedule['schedule'][pLen-i]['id']:
                    productSchedule['schedule'].pop()
                elif NEW == productSchedule['schedule'][pLen-i]['type']:
                    productSchedule['schedule'].pop()
                else:
                    break

            # 处理中间的B类
            pLen = len(productSchedule['schedule'])
            for i in range(1, pLen):
                if not productSchedule['schedule'][pLen-i]['id'] and B == productSchedule['schedule'][pLen-i]['type']:
                    productSchedule['schedule'].pop(pLen-i)


        # 第四步：重新计算结束状态
        for productSchedule in self.productScheduleData:
            sState = productSchedule['schemes'][1]
            for product in productSchedule['schedule']:
                if NEW == product['type']:
                    sState = 0
                else:
                    sState += 1
            productSchedule['eIndex'] = sState

        return self.productScheduleData

    def get_schedule(self):
        return self.productScheduleData

    def print_schedule(self):
        print('Number of variables =', self.result['solver']['variables'])
        print('Number of constraints =', self.result['solver']['constraints'])
        print('Optimal objective value = %d' % self.result['solver']['value'])

        print('BOILER START STATE: ', str(self.boilerSStates))
        print('BOILER END STATE COUNT: ', str(self.boilerEStateCount))
        print('BATCH DATA: ', str(self.batchDatas))

        plen = len(self.productScheduleData)
        for i in range(plen):
            for j in range(plen):
                if i == self.productScheduleData[j]['schemes'][0]:
                    pname = []
                    for product in self.productScheduleData[j]['schedule']:
                        pname.append(product['shortName'])
                    print('第%s口锅\t初始状态：%s\t排程: %s\t\t【方案原数据：%s】' % (self.productScheduleData[j]['schemes'][0], self.productScheduleData[j]['schemes'][1], '>'.join(pname), self.productScheduleData[j]))

    def desperse(self):

        schLen = len(self.productScheduleData)

        # 第一步：排序
        for i in range(schLen):
            for j in range(i+1, schLen):
                if self.productScheduleData[i]['totalTime'] < self.productScheduleData[j]['totalTime']:
                    self.productScheduleData[i], self.productScheduleData[j] = self.productScheduleData[j], self.productScheduleData[i]

            self.productScheduleData[i]['markTime'] = self.productScheduleData[i]['schedule'][0]['processTime']

        # 第二步：调整间距
        for i in range(1, schLen):
            """ 分两批增加间距
            if(i == int(schLen / 2)):
                continue
            """
            distance = self.productScheduleData[i]['markTime'] - self.productScheduleData[i-1]['markTime']
            if distance < OUT_BOILER_INTERVAL:
                self.productScheduleData[i]['markTime'] += (OUT_BOILER_INTERVAL - distance)
                self.productScheduleData[i]['sTime'] = self.productScheduleData[i]['markTime'] - self.productScheduleData[i]['schedule'][0]['processTime']
                if self.productScheduleData[i]['sTime'] > OUT_BOILER_INTERVAL * schLen:
                    self.productScheduleData[i]['sTime'] -= OUT_BOILER_INTERVAL * schLen

    def get_model(self):
        return self.models

    def print_model(self):
        for i in range(len(self.models)):
            for j in range(len(self.models[i])):
                print('MODEL-%s-%s: %s' % (i, j, self.models[i][j]))

    def get_schemes(self):
        return self.realitySchemesData

    def print_schemes(self):
        for i in range(len(self.realitySchemesData)):
            for j in range(len(self.realitySchemesData[i])):
                print('SCHEME-%s-%s: %s' % (i, j, self.realitySchemesData[i][j]))

    def verify(self):
        for productSchedule in self.productScheduleData:
            for product in productSchedule['schedule']:
                if not product['id']:
                    return False
        return True

    def print_result(self):
        print('Number of variables =', self.result['solver']['variables'])
        print('Number of constraints =', self.result['solver']['constraints'])
        print('Optimal objective value = %d' % self.result['solver']['value'])

        print('BOILER START STATE: ', str(self.boilerSStates))
        print('BOILER END STATE COUNT: ', str(self.boilerEStateCount))
        print('BATCH DATA: ', str(self.batchDatas))

        schemeData = self.result['schemesData']

        batchDatas = [0, 0, 0, 0]
        for i in range(len(schemeData)):
            batchDatas[0] += schemeData[i][2]
            batchDatas[1] += schemeData[i][3]
            batchDatas[2] += schemeData[i][4]
            batchDatas[3] += schemeData[i][5]

        print('REALITY DATA: ', str(batchDatas))

        for i in range(len(schemeData)):
            for j in range(len(schemeData)):
                if i == schemeData[j][0]:
                    print("第%s口锅选择方案:%s\t\t【方案原数据：%s】" % (schemeData[j][0]+1, '>'.join(schemeData[j][9]), schemeData[j]))




