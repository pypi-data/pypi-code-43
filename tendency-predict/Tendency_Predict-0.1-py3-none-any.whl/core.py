import numpy as np

np.set_printoptions(linewidth=1100)


class Tendency_Calculate():
    '''
    【执行流程与参数说明】\n
    ①加载趋势计算参数文件
            e.g.：smoothParam, windowSize = TC.Load_Tendency_Predict_Params(Address_Tendency_Predict_Calculate_Params)\n
            argv：Address_Tendency_Predict_Calculate_Params: 文件位置，{'Tendency_Predict_Calculate_Params':{'windowSize':5, 'smoothParam':0.9}}\n
    ②初始化趋势计算模型
            e.g.：lineRecord, X, S1, S2, S3, P = TC.Vars_Initiate(lineRecordShape)\n
            argv：使用lineRecordShape = (10-(windowSize-1), M)\n
            argv：M = np.shape(line)[1]，line的特征维度数量\n
    ③暂存输入数据
            e.g.：lineRecord = TC.Line_Record(line, lineRecord, lineRecordShape)\n
            argv：line：需要进行趋势计算的数据，line为形如[[48.6 48.3 64.5 63.6 53.4 49.9 70.1 72.1]]的mat\n
            argv：lineRecord: 数据DataTable\n
            argv：lineRecordShape: lineRecord的尺寸\n
    ④趋势计算
            e.g.：X, S1, S2, S3, P = TC.Tendency_Predict(smoothParam, windowSize, lineRecord, X, S1, S2, S3, P)\n
            argv：smoothParam：取自参数文件平滑系数\n
            argv：windowSize：取自参数文件平滑窗口尺寸\n
    ⑤其它
            X、S1、S2、S3: 需要暂存，无需计划释放\n
            P: 无需暂存，无需计划释放，P[-1， ：]为当期输入line的下期预测值\n
    【模型方法说明】\n
    * 每次输入data后计算出的P[-1, *]实质上是在对下一次输入的data进行预测\n
    * 输入的data数量为n时，输出的P[-1, *]的数量也为n\n
    * 当P=[].append(P[-1, *])时，同位置的P为data的预测，预测数据来源为上一期的data\n
    * 关于暂存，lineRecord， S1, S2, S3针对不同的预测对象测点均需要暂存，无需主动清空
    '''

    # ===== 加载趋势预测模型参数 ===== #
    @staticmethod
    def Load_Tendency_Predict_Params(Address_Tendency_Predict_Calculate_Params):
        '''
        ①加载趋势计算参数文件\n
            e.g.：smoothParam, windowSize = TC.Load_Tendency_Predict_Params(Address_Tendency_Predict_Calculate_Params)\n
            argv：Address_Tendency_Predict_Calculate_Params: 文件位置，{'Tendency_Predict_Calculate_Params':{'windowSize':5, 'smoothParam':0.9}}
        '''
        with open(Address_Tendency_Predict_Calculate_Params) as params:
            params = eval(params.read())['Tendency_Predict_Calculate_Params']
            smoothParam, windowSize = params['smoothParam'], params['windowSize']
        return smoothParam, windowSize

    # ===== 变量初始化 ===== #
    @staticmethod
    def Vars_Initiate(lineRecordShape):
        '''
        ②初始化趋势计算模型
            e.g.：lineRecord, X, S1, S2, S3, P = TC.Vars_Initiate(lineRecordShape)\n
            argv：使用lineRecordShape = (10-(windowSize-1), M)\n
            argv：M = np.shape(line)[1]，line的特征维度数量
        '''
        lineRecord = np.zeros(lineRecordShape, dtype=float)
        X = np.zeros(lineRecordShape, dtype=float)
        S1 = np.zeros((2, lineRecordShape[1]), dtype=float)
        S2 = np.zeros((2, lineRecordShape[1]), dtype=float)
        S3 = np.zeros((2, lineRecordShape[1]), dtype=float)
        P = np.zeros((2, lineRecordShape[1]), dtype=float)
        return lineRecord, X, S1, S2, S3, P

    # ===== 数据记录 ===== #
    @staticmethod
    def Line_Record(line, lineRecord, lineRecordShape):
        '''
        ③暂存输入数据
            e.g.：lineRecord = TC.Line_Record(line, lineRecord, lineRecordShape)\n
            argv：line：需要进行趋势计算的数据，line为形如[[48.6 48.3 64.5 63.6 53.4 49.9 70.1 72.1]]的mat\n
            argv：lineRecord: 数据DataTable\n
            argv：lineRecordShape: lineRecord的尺寸
        '''
        if (lineRecord == np.zeros_like(lineRecord)).all():
            lineRecord = np.reshape(np.repeat(line, np.shape(lineRecord)[0], 0), (-1, 1))
        else:
            line = np.mat(line)
            lineRecord = np.concatenate((lineRecord, line), 0)
        lineRecord = lineRecord[-lineRecordShape[0]:, :]
        return lineRecord

    # ===== 趋势计算 ===== #
    @staticmethod
    def Tendency_Predict(smoothParam, windowSize, lineRecord, X, S1, S2, S3, P):
        '''
        ④趋势计算
            e.g.：X, S1, S2, S3, P = TC.Tendency_Predict(smoothParam, windowSize, lineRecord, X, S1, S2, S3, P)\n
            argv：smoothParam：取自参数文件平滑系数\n
            argv：windowSize：取自参数文件平滑窗口尺寸
            $ X 通过lineRecord计算得出，不需暂存
        '''
        # ===== 平滑处理 ==== #
        for i in range(np.shape(lineRecord)[0]):
            if i + windowSize <= np.shape(lineRecord)[0]:
                X[i, :] = np.mean(lineRecord[i:i + windowSize, :], axis=0)
        X = X[0: np.shape(lineRecord)[0] - (windowSize - 1), :]
        # ===== 检查S1 S2 S3 是否更新 ==== #
        if (S1 == np.zeros_like(S1)).all():
            S1[0, :] = np.average(X, axis=0)
            S2[0, :] = np.average(X, axis=0)
            S3[0, :] = np.average(X, axis=0)
        else:
            S1 = np.concatenate((S1, np.zeros((1, np.shape(S1)[1]))))[-2:, :]
            S2 = np.concatenate((S2, np.zeros((1, np.shape(S2)[1]))))[-2:, :]
            S3 = np.concatenate((S3, np.zeros((1, np.shape(S3)[1]))))[-2:, :]
        # ===== 计算S1 S2 S3 ==== #
        S_1 = lambda a, X_t, S1_t_1: a * X_t + (1 - a) * S1_t_1
        S_2 = lambda a, S1_t, S2_t_1: a * S1_t + (1 - a) * S2_t_1
        S_3 = lambda a, S2_t, S3_t_1: a * S2_t + (1 - a) * S3_t_1
        for i in range(np.shape(S1)[1]):
            S1[-1, i] = S_1(smoothParam, X[-1, i], S1[0, i])
            S2[-1, i] = S_2(smoothParam, S1[-1, i], S2[0, i])
            S3[-1, i] = S_3(smoothParam, S2[-1, i], S3[0, i])
        # ===== 计算At Bt Ct ==== #
        A_t = lambda S1_t, S2_t, S3_t: 3 * S1_t - 3 * S2_t + S3_t
        B_t = lambda a, S1_t, S2_t, S3_t: a / (2 * (1 - a) ** 2) * (
                (6 - 5 * a) * S1_t - 2 * (5 - 4 * a) * S2_t + (4 - 3 * a) * S3_t)
        C_t = lambda a, S1_t, S2_t, S3_t: (a ** 2 / 2 / (1 - a) ** 2) * (S1_t - 2 * S2_t + S3_t)
        At = np.zeros((1, np.shape(lineRecord)[1]))
        Bt = np.zeros((1, np.shape(lineRecord)[1]))
        Ct = np.zeros((1, np.shape(lineRecord)[1]))
        for i in range(np.shape(S1)[1]):
            At[0, i] = A_t(S1[-1, i], S2[-1, i], S3[-1, i])
            Bt[0, i] = B_t(smoothParam, S1[-1, i], S2[-1, i], S3[-1, i])
            Ct[0, i] = C_t(smoothParam, S1[-1, i], S2[-1, i], S3[-1, i])
        # ===== 计算P ==== #
        P_T = lambda at, bt, ct, T: at + bt * T + ct * T ** 2
        cacheP = []
        for i in range(np.shape(S1)[1]):
            cacheP.append(P_T(At[0, i], Bt[0, i], Ct[0, i], 1))
        P = np.concatenate((P, np.mat(cacheP)), axis=0)
        P = P[-2:, :]
        return X, S1, S2, S3, P
