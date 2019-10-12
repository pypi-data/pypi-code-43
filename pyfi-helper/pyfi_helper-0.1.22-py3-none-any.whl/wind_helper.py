# encoding: utf-8
"""
提供WindPy接口的pandas封装
"""
from math import isnan
from datetime import timedelta
# app
from WindPy import w
import pandas as pd
from pyfi.mapper import label, da_mapper, mapper
from pyfi.data_agent import *
from pyfi.common import nearest


class WindHelper(object):
    """
    WindPy20170904更新
    在本次修改后, 下面函数结果中的时间Times将只包含日期date: 
    wsd, tdays, tdayscount, tdaysoffset, wset, weqs, wpd, htocode, edb
    常用字段：
    close
    settle
    volume
    """
    # 常见edb代码映射表
    """
    ip=工业增加值：当月同比
    cpi=CPI:当月同比(月）
    cpif=CPI食品：当月同比
    cpinf=CPI非食品：当月同比
    """
    mapper = mapper
    label = label
    da_mapper = da_mapper

    @classmethod
    def check_begin_and_end_date(cls):
        # TODO: 把时间校验模块化
        pass

    @classmethod
    def translate(cls, code):
        """
        将list中的code进行映射
        :param code:
        :return:
        """
        if type(code) == list:
            return [cls.mapper[x] if x in cls.mapper else x for x in code]
        else:
            if code in cls.mapper:
                return cls.mapper[code]
            else:
                return code

    @classmethod
    def edbm(cls, codes, begin_date, end_date, options="fill=perious", adjust=False, shift=0, fill=False, debug=True):
        """多代码单维时间序列
        :param shift:
        :param fill:
        :param adjust: 是否对日期进行调整，td表示最近的交易日期代替月末数据
        :param codes:
        :param begin_date:
        :param end_date:
        :param options:
        :return:
        """
        if debug is True:
            print("edbm开始提取数据..." + str(codes))
        if begin_date is None:
            raise Exception("codes:" + str(codes) + "的begindate是空的！")
        if type(begin_date) is str:
            begin_date = datetime.strptime(begin_date, '%Y-%m-%d')
        if type(end_date) is str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if begin_date > end_date:
            print("结束时间小于开始时间，你在逗我么，骚年！")
            return None
        if not w.isconnected():
            w.start()
        if type(codes) is not list:
            codes = codes.split(",")  # 全部转换为list格式
        final_codes = []  # 因子名称列表
        final_data_mapper = {}  # 预处理函数字典
        for x in codes:
            if x in cls.da_mapper:
                final_data_mapper[x] = cls.da_mapper[x]
            else:
                final_codes.append(cls.mapper[x] if x in cls.mapper else x)
        try:
            df = pd.DataFrame()
            if len(final_codes) > 0:
                if not w.isconnected:
                    w.start()
                windData = w.edb(final_codes, begin_date, end_date, options)
                if hasattr(windData, "ErrorCodes") and windData.ErrorCode != 0:
                    raise (Exception(str(windData)))
                if len(windData.Data) == 0:
                    return None
                if len(windData.Data[0]) == 0:
                    return None
                if "Internet Timeout" in windData.Data[0]:
                    raise Exception("wind APi连接不上:" + windData.Data[0])
                dataDict = {}
                cols = []
                for i in range(len(windData.Data)):
                    col = windData.Codes[i]
                    if col in cls.mapper.values():
                        col = list(cls.mapper.keys())[list(cls.mapper.values()).index(col)]
                    cols.append(col)
                for i in range(len(windData.Data)):
                    # col = windData.Codes[i]
                    # if col in cls.mapper.values():
                    #     col = list(cls.mapper.keys())[list(cls.mapper.values()).index(col)]
                    dataDict[cols[i]] = windData.Data[i]
                df = df.join(pd.DataFrame(dataDict, index=windData.Times), how="outer")
                df.index = pd.to_datetime(df.index)
                df.index.name = "trade_date"
                df = df.loc[:, cols]  # 调整顺序
            # 自定义指标,直接通过其他封装函数获取
            if len(final_data_mapper) > 0:
                da_dfs = [(final_data_mapper[x])(begin_date, end_date) for x in final_data_mapper]
                da_df = da_dfs[0]
                for i in range(1, len(da_dfs)):
                    da_df = da_df.join(da_dfs[i], how="outer")
                df = df.join(da_df, how="outer")
            # 二次调整
            if fill:
                df = cls.fill(df, end_date)  # 对残缺的月份进行补全， 并用上一个数据进行补全
            if adjust:
                df = cls.monthly_data_with_td(df)
            if shift != 0:
                df = cls.monthly_data_with_signal(df, shift)
            return df
        except BaseException as e:
            print(format(e))
            raise



    @classmethod
    def wset(cls, *args, **kwargs):
        if not w.isconnected():
            w.start()
        return w.wset(*args, **kwargs)

    @classmethod
    def wsd(cls, code, paras, begin_date, end_date, options="credibility=1", adjust=False, shift=0, debug=True):
        """单代码多维日期序列
        或者多代码单维日期序列
        注意：wind并不支持多代码多维的数据提取
        :param adjust:
        :param shift:
        :return:
        :param code: (list) 一次只能一个品种
        :param paras: (list) fields
        :param begin_date: (datetime or str)如 '20150101'
        :param end_date: （datetime or str) 如 '20150101'
        :param options: （string） xx=xx;yy=yy 不支持大小写
        :return: pandas.DataFrame
        """
        if debug is True:
            print("wsd开始提取数据..." + str(code))
        if begin_date is None:
            raise Exception("codes:" + str(code) + "的begindate是空的！")
        if type(begin_date) is str:
            begin_date = datetime.strptime(begin_date, '%Y-%m-%d')
        if type(end_date) is str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if begin_date > end_date:
            print("结束时间小于开始时间，你在逗我么，骚年！")
            return None
        # code = cls.mapper[code] if code in cls.mapper else code
        try:
            if not w.isconnected():
                w.start()
                
            # 将list转换为string
            if type(code) is str:
                code = code.split(",")
            # 校验，防止codes和paras同时为长度大于1的list
            if type(code) == list and type(paras) == list:
                if len(code) > 1 and len(paras) > 1:
                    raise Exception(u"wsd不能提取多代码多维度数据")
            if type(code) == list and len(code) == 1:
                code = code[0]
            code = cls.translate(code=code)
            options = options
            wind_data = w.wsd(code, paras, begin_date, end_date, options)
            if hasattr(wind_data, "ErrorCodes") and wind_data.ErrorCode != 0:
                print("wsd: wind 抛出异常！")
                raise (Exception(str(wind_data)))
            if wind_data is None:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if len(wind_data.Data) == 0:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if len(wind_data.Data[0]) == 0:
                raise Exception(u"wsd调用wind服务端异常，数据为空")
            if "CWSDService: invalid windcodes." in wind_data.Data[0]:
                raise Exception(wind_data.Data[0])
            if "CWSDService: No data." in wind_data.Data[0]:
                return None
            dataDict = {}
            if not hasattr(code, "__iter__") or type(code) is str:
                for i in range(len(wind_data.Data)):  # 单代码则按照因子索引
                    dataDict[wind_data.Fields[i].lower()] = wind_data.Data[i] # wind经常会把field改成大写
                    df = pd.DataFrame(dataDict, index=wind_data.Times)
            else:  # 多代码的情况下
                if begin_date == end_date:
                    df = pd.DataFrame(wind_data.Data, columns=code, index=wind_data.Times)  # 当只有一个日期时，返回的数据结构发生变化
                else:
                    for i in range(len(code)):
                        dataDict[code[i]] = wind_data.Data[i]
                        df = pd.DataFrame(dataDict, index=wind_data.Times)
                        df = df.reindex(columns=code)
            # 将date类型转换为datetime类型
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"

            # 二次调整
            if adjust:
                df = cls.monthly_data_with_td(df)
            if shift != 0:
                df = cls.monthly_data_with_signal(df, shift)
            return df
        except Exception as e:
            print(format(e))
            raise

    @classmethod
    def wss(cls, codes, paras):
        """多代码多维信息序列
        :param codes:(list) or (str)
        :param paras:(list) or (str)
        :return:(DataFrame);
        """

        try:
            if not w.isconnected():
                w.start()
            if type(codes) is not list:
                codes = codes.split(",")  # 全部转换为list格式
            codes = [cls.mapper[x] if x in cls.mapper else x for x in codes]
            if type(paras) is not list:
                paras = paras.split(",")
            paras.insert(0, "windcode")
            wind_data = w.wss(codes, paras, options=None)
            if hasattr(wind_data, "ErrorCodes") and wind_data.ErrorCode != 0:
                raise (Exception(str(wind_data)))
            if len(wind_data.Data) == 0:
                return None
            if len(wind_data.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(wind_data.Data)):
                dataDict[wind_data.Fields[i].lower()] = wind_data.Data[i]
            df = pd.DataFrame(dataDict)
            df = df[paras]
            df.rename(columns={"windcode": "code"}, inplace=True)

            return df
        except BaseException as e:
            print(format(e))
            raise

    @classmethod
    def edb(cls, codes, begin_date, end_date, options="fill=perious", adjust=False, shift=0, fill=False, debug=True):
        """多代码单维时间序列
        :param shift:
        :param fill:
        :param adjust: 是否对日期进行调整，td表示最近的交易日期代替月末数据
        :param codes:
        :param begin_date:
        :param end_date:
        :param options:
        :return:
        """
        if debug is True:
            print("edb开始提取数据..." + str(codes))
        if begin_date is None:
            raise Exception("codes:" + str(codes) + "的begindate是空的！")
        if type(begin_date) is str:
            begin_date = datetime.strptime(begin_date, '%Y-%m-%d')
        if type(end_date) is str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if begin_date > end_date:
            print("结束时间小于开始时间，你在逗我么，骚年！")
            return None
        if not w.isconnected():
            w.start()
        if type(codes) is not list:
            codes = codes.split(",")  # 全部转换为list格式
        final_codes = codes  # 因子名称列表
        # final_data_mapper = {}  # 预处理函数字典
        # for x in codes:
        #     if x in cls.da_mapper:
        #         final_data_mapper[x] = cls.da_mapper[x]
        #     else:
        #         final_codes.append(cls.mapper[x] if x in cls.mapper else x)
        try:
            df = pd.DataFrame()
            if len(final_codes) > 0:
                if not w.isconnected:
                    w.start()
                windData = w.edb(final_codes, begin_date, end_date, options)
                if hasattr(windData, "ErrorCodes") and windData.ErrorCode != 0:
                    raise (Exception(str(windData)))
                if len(windData.Data) == 0:
                    return None
                if len(windData.Data[0]) == 0:
                    return None
                if "Internet Timeout" in windData.Data[0]:
                    raise Exception("wind APi连接不上:" + windData.Data[0])
                dataDict = {}
                cols = []
                for i in range(len(windData.Data)):
                    col = windData.Codes[i]
                    # if col in cls.mapper.values():
                    #     col = list(cls.mapper.keys())[list(cls.mapper.values()).index(col)]
                    cols.append(col)
                    dataDict[cols[i]] = windData.Data[i]
                df = df.join(pd.DataFrame(dataDict, index=windData.Times), how="outer")
                df.index = pd.to_datetime(df.index)
                df.index.name = "trade_date"
                df = df.loc[:, cols]  # 调整顺序
            # 自定义指标,直接通过其他封装函数获取
            # if len(final_data_mapper) > 0:
            #     da_dfs = [(final_data_mapper[x])(begin_date, end_date) for x in final_data_mapper]
            #     da_df = da_dfs[0]
            #     for i in range(1, len(da_dfs)):
            #         da_df = da_df.join(da_dfs[i], how="outer")
            #     df = df.join(da_df, how="outer")
            # 二次调整
            if fill:
                df = cls.fill(df, end_date)  # 对残缺的月份进行补全， 并用上一个数据进行补全
            if adjust:
                df = cls.monthly_data_with_td(df)
            if shift != 0:
                df = cls.monthly_data_with_signal(df, shift)
            return df
        except BaseException as e:
            print(format(e))
            raise

    @classmethod
    def wsi(cls, code, fields, begin_date, end_date, option="", num_retries=2):
        """单代码多维"""
        try:
            if type(begin_date) in (datetime, pd._libs.tslib.Timestamp):
                begin_date = begin_date.strftime("%Y%m%d")
            if type(end_date) in (datetime, pd._libs.tslib.Timestamp):
                end_date = end_date.strftime("%Y%m%d")
            if type(fields) is list:
                fields = ",".join(fields)
            if type(code) is list:
                code = ",".join(code)
            w.start()
            result = w.wsi(code, fields, begin_date, end_date, "", usedf=True)
            if result[0] == u'CWSSService: invalid indicators.' and len(result) == 0:
                raise Exception("CWSSService: invalid indicators.")
            return result[1]
        except Exception as e:
            if num_retries > 0:
                num_retries -= 1
                cls.wsi(code, fields, begin_date, end_date, option=option, num_retries=num_retries)

    @staticmethod
    def getMultiTimeSeriesDataFrame(codeList, beginDate, endDate, para, period="",
                                    tradingCalendar="", priceAdj="", credibility=0):
        """
        para只能是一个参数
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param credibility: (int)
           :param codeList: (list)
           :param beginDate: (date or datetime)
           :param endDate: (date or datetime)
           :param para: (string)只能是一个字符参数
           :param period: (int) 频率
           :param tradingCalendar: (string)   交易日历，选择可以选择银行间:NIB,不选择，则默认交易所日历
           :param priceAdj: (string) 价格是否调整,F:前复权，B:后复权
           :return: (DataFrame)
        """
        try:
            w.start()
            codeListStr = ",".join(codeList)
            period = ("Period=" + period) if period == "W" else ""
            tradingCalendar = ("TradingCalendar=" + tradingCalendar) if tradingCalendar != "" else ""
            priceAdj = ("priceAdj=" + priceAdj) if priceAdj != "" else ""
            credibility = ("credibility=" + str(credibility)) if credibility != 0 else ""
            windData = w.wsd(codeListStr,
                             para,
                             beginDate.strftime("%Y-%m-%d"),
                             endDate.strftime("%Y-%m-%d"),
                             period,
                             tradingCalendar,
                             priceAdj, credibility)
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Codes[i].lower() + "_" + para] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getTimeSeriesDataFrame(code, beginDate, endDate, paraList, period="",
                               tradingCalendar="", priceAdj="", credibility=0):
        """
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param credibility: (int)
           :param code: (string)
           :param beginDate: (date or datetime)
           :param endDate: (date or datetime)
           :param paraList: (list)
           :param period: (str) W or D 频率
           :param tradingCalendar: (string)   交易日历，选择可以选择银行间:NIB,不选择，则默认交易所日历
           :param priceAdj: (string) 价格是否调整,F:前复权，B:后复权
           :return: (DataFrame)
        """
        try:
            w.start()
            para = ",".join(paraList)
            period = ("Period=" + period) if period == "W" else ""
            tradingCalendar = ("TradingCalendar=" + tradingCalendar) if tradingCalendar != "" else ""
            priceAdj = ("priceAdj=" + priceAdj) if priceAdj != "" else ""
            credibility = ("credibility=" + str(credibility)) if credibility != 0 else ""
            windData = w.wsd(code,
                             para,
                             beginDate.strftime("%Y-%m-%d"),
                             endDate.strftime("%Y-%m-%d"),
                             tradingCalendar,
                             priceAdj, credibility)
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getMinTimeSeriesDataFrame(code, beginDate, endDate, paraList, bar_size=1):
        """
        获取分钟级别数据
        get time series from windPy, each code represents one capture
         月度合约: trade_hiscode
           :param bar_size: (int)  The frequency of the data
           :param code: string
           :param beginDate: date or datetime
           :param endDate: date or datetime
           :param paraList: list
           :return: DataFrame
        """
        try:
            w.start()
            para = ",".join(paraList)
            bar_size = "" + str(bar_size) if bar_size is not None else ""
            windData = w.wsi(code,
                             para,
                             beginDate.strftime("%Y-%m-%d %H:%M:%S"),
                             endDate.strftime("%Y-%m-%d %H:%M:%S"), "")
            if len(windData.Data) == 0:
                raise BaseException
            if len(windData.Data[0]) == 0:
                raise BaseException
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            if df.index[0].to_pydatetime().microsecond != 0:
                df.index -= timedelta(microseconds=df.index[0].to_pydatetime().microsecond)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getInfoDataFrame(code, paraList):
        """
        get info of one product by code
        :return: DataFrame
        :param code:
        :param paraList:
        :return:  DataFrame;
        """
        try:
            w.start()
            para = ",".join(paraList)
            windData = w.wss(code,
                             para)
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Fields[i].lower()] = windData.Data[i]
            df = pd.DataFrame(dataDict)
            df = df[paraList]
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def getEDBTimeSeriesDataFrame(codeList, beginDate, endDate, fillChoice="Previous"):
        """
        宏观数据提取
        get edb time series from windPy, each code represents one capture
        : Param fillChoice: (string) previous或者None，空值数据是否需要被前一日的数据取代
        """
        codeListStr = ",".join(codeList)
        try:
            w.start()
            if fillChoice == "Previous":
                windData = w.edb(codeListStr,
                                 beginDate.strftime("%Y-%m-%d"),
                                 endDate.strftime("%Y-%m-%d"),
                                 "Fill=" + fillChoice)
            else:
                windData = w.edb(codeListStr,
                                 beginDate.strftime("%Y-%m-%d"),
                                 endDate.strftime("%Y-%m-%d"))
            if len(windData.Data) == 0:
                return None
            if len(windData.Data[0]) == 0:
                return None
            dataDict = {}
            for i in range(len(windData.Data)):
                dataDict[windData.Codes[i]] = windData.Data[i]
            df = pd.DataFrame(dataDict, index=windData.Times)
            df.index = pd.to_datetime(df.index)
            df.index.name = "trade_date"
            return df
        except BaseException as e:
            print(format(e))
            raise

    @staticmethod
    def t_days_offset(offset=0, cur_date=datetime.now()):
        try:
            w.start()
            result = w.tdaysoffset(offset, cur_date, "").Data[0][0]
            # result = WindHelper.wsd(code="000001.SZ", paras=["close"], begin_date=datetime.now() - timedelta(days=10), end_date=datetime.now())
            # result = result.index[-1].to_pydatetime()
            return result
        except IndexError as e:
            print(format(e))
            raise

    @staticmethod
    def tdays_count(begin_date, end_date):
        w.start()
        result = w.tdayscount(begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "").Data[0][0]
        return result

    @classmethod
    def all_tf_codes(cls, begin_date=None, end_date=None, contract_type="T"):
        """
        获取指定时间段内所有国债期货的合约
        :return type: list
        """
        if begin_date is None and contract_type == "T":
            begin_date = datetime(2015, 3, 20)
        elif begin_date is None and contract_type == "TF":
            begin_date = datetime(2013, 9, 6)
        elif begin_date is None and contract_type == "TS":
            begin_date = datetime(2018, 8, 17)
        if end_date is None:
            end_date = datetime.now()
        w.start()
        near_code = contract_type.upper() + "00.CFE"
        far_code = contract_type.upper() + "01.CFE"
        farfar_code = contract_type.upper() + "02.CFE"
        para = "trade_hiscode"
        near_df = cls.wsd(code=near_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 国债期货下季列表
        far_df = cls.wsd(code=far_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 国债期货隔季合约
        farfar_df = cls.wsd(code=farfar_code, paras=para, begin_date=begin_date, end_date=end_date).dropna()
        # 获取国债期货时间序列基础表：
        # 日期，当季合约，当季结算价，持仓量，下季合约，下季结算价，持仓量，隔季合约，隔季结算价，持仓量
        base_df = pd.DataFrame(near_df).append(far_df).append(farfar_df)
        if len(base_df) == 0:
            return None
        contract_code_list = base_df["trade_hiscode"].unique().tolist()
        return list(sorted(contract_code_list))

    @classmethod
    def tdays(cls, begin_date, end_date, tradingCalendar=""):
        """生成时间序列List"""
        w.start()
        return w.tdays(begin_date, end_date, tradingCalendar).Data[0]

    @classmethod
    def tf_dbs(cls, code, market="IB"):
        w.start()
        para = "windcode=" + code
        data = w.wset("conversionfactor", para).Data
        bondCodeList = data[0]
        cfList = data[1]
        dlvBdCodeDict = {}
        for i in range(len(bondCodeList)):
            bondCode = bondCodeList[i]
            if market in bondCode:
                dlvBdCodeDict[bondCode] = cfList[i]
        return dlvBdCodeDict

    @classmethod
    def get_end_date(cls):
        """确定开始时间，计算最新的已经结算的交易日"""
        # 确定结束时间
        # 结束时间为该合约的最后交易日和当前日期的最小值
        last_trade_date = cls.t_days_offset(offset=0, cur_date=datetime.now())
        # 确定结束时间
        if datetime.now().hour >= 19:  # 以晚上19点为界限
            end_date = last_trade_date
        elif datetime.now().date() > last_trade_date.date():  # 当天不是交易日
            end_date = last_trade_date
        else:  # 既非节假日，且当然的数据也没有生成
            end_date = cls.t_days_offset(offset=-1, cur_date=datetime.now())  # datetime类型
        return end_date

    @classmethod
    def get_dv01(cls, codes):
        """获取个券或者组合的dv01"""
        pass

    @classmethod
    def monthly_data_with_td(cls, df):
        """
        将月度宏观数据时间点和交易数据相对应
        :param df:
        :return:
        """
        begin_date = df.index[0]
        end_date = df.index[-1]
        items = cls.tdays(begin_date=begin_date, end_date=end_date)
        ds = [nearest(items, d) for d in df.index.to_pydatetime()]
        df.index = pd.DatetimeIndex(ds)
        return df

    @classmethod
    def monthly_data_with_signal(cls, df, shift):
        """
        将月度交易数据时间点和交易信号相对应
        :param shift:
        :param df:
        :return:
        """
        cls.monthly_data_with_td(df)
        return df.shift(shift)

    @classmethod
    def ffill(cls, df):
        return df.resample("M").last().ffill().dropna()

    @classmethod
    def fill(cls, df, end_date):
        df = df.resample("M").last().ffill().dropna()
        date_idx = pd.date_range(start=df.index[0], end=end_date)
        return pd.DataFrame(df, index=date_idx).ffill().dropna()
