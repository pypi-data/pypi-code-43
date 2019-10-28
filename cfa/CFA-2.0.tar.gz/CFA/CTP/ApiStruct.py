# encoding=utf-8
from ctypes import *
from AlgoPlus.utils.base_field import BaseField


class DisseminationField(BaseField):
    """信息分发"""
    _fields_ = [
        ('SequenceSeries', c_short)  # ///序列系列号
        , ('SequenceNo', c_int)  # 序列号
    ]

    def __init__(self, SequenceSeries=0, SequenceNo=0):
        super(DisseminationField, self).__init__()
        self.SequenceSeries = int(SequenceSeries)
        self.SequenceNo = int(SequenceNo)


class ReqUserLoginField(BaseField):
    """用户登录请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('Password', c_char * 41)  # 密码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('OneTimePassword', c_char * 41)  # 动态密码
        , ('ClientIPAddress', c_char * 16)  # 终端IP地址
        , ('LoginRemark', c_char * 36)  # 登录备注
        , ('ClientIPPort', c_int)  # 终端IP端口
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID='', Password='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', MacAddress='', OneTimePassword='', ClientIPAddress='', LoginRemark='',
                 ClientIPPort=0):
        super(ReqUserLoginField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.Password = self._to_bytes(Password)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.MacAddress = self._to_bytes(MacAddress)
        self.OneTimePassword = self._to_bytes(OneTimePassword)
        self.ClientIPAddress = self._to_bytes(ClientIPAddress)
        self.LoginRemark = self._to_bytes(LoginRemark)
        self.ClientIPPort = int(ClientIPPort)


class RspUserLoginField(BaseField):
    """用户登录应答"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('LoginTime', c_char * 9)  # 登录成功时间
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('SystemName', c_char * 41)  # 交易系统名称
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('MaxOrderRef', c_char * 13)  # 最大报单引用
        , ('SHFETime', c_char * 9)  # 上期所时间
        , ('DCETime', c_char * 9)  # 大商所时间
        , ('CZCETime', c_char * 9)  # 郑商所时间
        , ('FFEXTime', c_char * 9)  # 中金所时间
        , ('INETime', c_char * 9)  # 能源中心时间
    ]

    def __init__(self, TradingDay='', LoginTime='', BrokerID='', UserID='', SystemName='', FrontID=0, SessionID=0, MaxOrderRef='', SHFETime='', DCETime='', CZCETime='', FFEXTime='', INETime=''):
        super(RspUserLoginField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.LoginTime = self._to_bytes(LoginTime)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.SystemName = self._to_bytes(SystemName)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.MaxOrderRef = self._to_bytes(MaxOrderRef)
        self.SHFETime = self._to_bytes(SHFETime)
        self.DCETime = self._to_bytes(DCETime)
        self.CZCETime = self._to_bytes(CZCETime)
        self.FFEXTime = self._to_bytes(FFEXTime)
        self.INETime = self._to_bytes(INETime)


class UserLogoutField(BaseField):
    """用户登出请求"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(UserLogoutField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class ForceUserLogoutField(BaseField):
    """强制交易员退出"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(ForceUserLogoutField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class ReqAuthenticateField(BaseField):
    """客户端认证请求"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('AuthCode', c_char * 17)  # 认证码
        , ('AppID', c_char * 33)  # App代码
    ]

    def __init__(self, BrokerID='', UserID='', UserProductInfo='', AuthCode='', AppID=''):
        super(ReqAuthenticateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.AuthCode = self._to_bytes(AuthCode)
        self.AppID = self._to_bytes(AppID)


class RspAuthenticateField(BaseField):
    """客户端认证响应"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('AppID', c_char * 33)  # App代码
        , ('AppType', c_char * 1)  # App类型
    ]

    def __init__(self, BrokerID='', UserID='', UserProductInfo='', AppID='', AppType=''):
        super(RspAuthenticateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.AppID = self._to_bytes(AppID)
        self.AppType = self._to_bytes(AppType)


class AuthenticationInfoField(BaseField):
    """客户端认证信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('AuthInfo', c_char * 129)  # 认证信息
        , ('IsResult', c_int)  # 是否为认证结果
        , ('AppID', c_char * 33)  # App代码
        , ('AppType', c_char * 1)  # App类型
    ]

    def __init__(self, BrokerID='', UserID='', UserProductInfo='', AuthInfo='', IsResult=0, AppID='', AppType=''):
        super(AuthenticationInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.AuthInfo = self._to_bytes(AuthInfo)
        self.IsResult = int(IsResult)
        self.AppID = self._to_bytes(AppID)
        self.AppType = self._to_bytes(AppType)


class RspUserLogin2Field(BaseField):
    """用户登录应答2"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('LoginTime', c_char * 9)  # 登录成功时间
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('SystemName', c_char * 41)  # 交易系统名称
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('MaxOrderRef', c_char * 13)  # 最大报单引用
        , ('SHFETime', c_char * 9)  # 上期所时间
        , ('DCETime', c_char * 9)  # 大商所时间
        , ('CZCETime', c_char * 9)  # 郑商所时间
        , ('FFEXTime', c_char * 9)  # 中金所时间
        , ('INETime', c_char * 9)  # 能源中心时间
        , ('RandomString', c_char * 17)  # 随机串
    ]

    def __init__(self, TradingDay='', LoginTime='', BrokerID='', UserID='', SystemName='', FrontID=0, SessionID=0, MaxOrderRef='', SHFETime='', DCETime='', CZCETime='', FFEXTime='', INETime='', RandomString=''):
        super(RspUserLogin2Field, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.LoginTime = self._to_bytes(LoginTime)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.SystemName = self._to_bytes(SystemName)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.MaxOrderRef = self._to_bytes(MaxOrderRef)
        self.SHFETime = self._to_bytes(SHFETime)
        self.DCETime = self._to_bytes(DCETime)
        self.CZCETime = self._to_bytes(CZCETime)
        self.FFEXTime = self._to_bytes(FFEXTime)
        self.INETime = self._to_bytes(INETime)
        self.RandomString = self._to_bytes(RandomString)


class TransferHeaderField(BaseField):
    """银期转帐报文头"""
    _fields_ = [
        ('Version', c_char * 4)  # ///版本号，常量，1.0
        , ('TradeCode', c_char * 7)  # 交易代码，必填
        , ('TradeDate', c_char * 9)  # 交易日期，必填，格式：yyyymmdd
        , ('TradeTime', c_char * 9)  # 交易时间，必填，格式：hhmmss
        , ('TradeSerial', c_char * 9)  # 发起方流水号，N/A
        , ('FutureID', c_char * 11)  # 期货公司代码，必填
        , ('BankID', c_char * 4)  # 银行代码，根据查询银行得到，必填
        , ('BankBrchID', c_char * 5)  # 银行分中心代码，根据查询银行得到，必填
        , ('OperNo', c_char * 17)  # 操作员，N/A
        , ('DeviceID', c_char * 3)  # 交易设备类型，N/A
        , ('RecordNum', c_char * 7)  # 记录数，N/A
        , ('SessionID', c_int)  # 会话编号，N/A
        , ('RequestID', c_int)  # 请求编号，N/A
    ]

    def __init__(self, Version='', TradeCode='', TradeDate='', TradeTime='', TradeSerial='', FutureID='', BankID='', BankBrchID='', OperNo='', DeviceID='', RecordNum='', SessionID=0, RequestID=0):
        super(TransferHeaderField, self).__init__()

        self.Version = self._to_bytes(Version)
        self.TradeCode = self._to_bytes(TradeCode)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.TradeSerial = self._to_bytes(TradeSerial)
        self.FutureID = self._to_bytes(FutureID)
        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)
        self.OperNo = self._to_bytes(OperNo)
        self.DeviceID = self._to_bytes(DeviceID)
        self.RecordNum = self._to_bytes(RecordNum)
        self.SessionID = int(SessionID)
        self.RequestID = int(RequestID)


class TransferBankToFutureReqField(BaseField):
    """银行资金转期货请求，TradeCode=202001"""
    _fields_ = [
        ('FutureAccount', c_char * 13)  # ///期货资金账户
        , ('FuturePwdFlag', c_char * 1)  # 密码标志
        , ('FutureAccPwd', c_char * 17)  # 密码
        , ('TradeAmt', c_double)  # 转账金额
        , ('CustFee', c_double)  # 客户手续费
        , ('CurrencyCode', c_char * 4)  # 币种：RMB-人民币 USD-美圆 HKD-港元
    ]

    def __init__(self, FutureAccount='', FuturePwdFlag='', FutureAccPwd='', TradeAmt=0.0, CustFee=0.0, CurrencyCode=''):
        super(TransferBankToFutureReqField, self).__init__()

        self.FutureAccount = self._to_bytes(FutureAccount)
        self.FuturePwdFlag = self._to_bytes(FuturePwdFlag)
        self.FutureAccPwd = self._to_bytes(FutureAccPwd)
        self.TradeAmt = float(TradeAmt)
        self.CustFee = float(CustFee)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferBankToFutureRspField(BaseField):
    """银行资金转期货请求响应"""
    _fields_ = [
        ('RetCode', c_char * 5)  # ///响应代码
        , ('RetInfo', c_char * 129)  # 响应信息
        , ('FutureAccount', c_char * 13)  # 资金账户
        , ('TradeAmt', c_double)  # 转帐金额
        , ('CustFee', c_double)  # 应收客户手续费
        , ('CurrencyCode', c_char * 4)  # 币种
    ]

    def __init__(self, RetCode='', RetInfo='', FutureAccount='', TradeAmt=0.0, CustFee=0.0, CurrencyCode=''):
        super(TransferBankToFutureRspField, self).__init__()

        self.RetCode = self._to_bytes(RetCode)
        self.RetInfo = self._to_bytes(RetInfo)
        self.FutureAccount = self._to_bytes(FutureAccount)
        self.TradeAmt = float(TradeAmt)
        self.CustFee = float(CustFee)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferFutureToBankReqField(BaseField):
    """期货资金转银行请求，TradeCode=202002"""
    _fields_ = [
        ('FutureAccount', c_char * 13)  # ///期货资金账户
        , ('FuturePwdFlag', c_char * 1)  # 密码标志
        , ('FutureAccPwd', c_char * 17)  # 密码
        , ('TradeAmt', c_double)  # 转账金额
        , ('CustFee', c_double)  # 客户手续费
        , ('CurrencyCode', c_char * 4)  # 币种：RMB-人民币 USD-美圆 HKD-港元
    ]

    def __init__(self, FutureAccount='', FuturePwdFlag='', FutureAccPwd='', TradeAmt=0.0, CustFee=0.0, CurrencyCode=''):
        super(TransferFutureToBankReqField, self).__init__()

        self.FutureAccount = self._to_bytes(FutureAccount)
        self.FuturePwdFlag = self._to_bytes(FuturePwdFlag)
        self.FutureAccPwd = self._to_bytes(FutureAccPwd)
        self.TradeAmt = float(TradeAmt)
        self.CustFee = float(CustFee)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferFutureToBankRspField(BaseField):
    """期货资金转银行请求响应"""
    _fields_ = [
        ('RetCode', c_char * 5)  # ///响应代码
        , ('RetInfo', c_char * 129)  # 响应信息
        , ('FutureAccount', c_char * 13)  # 资金账户
        , ('TradeAmt', c_double)  # 转帐金额
        , ('CustFee', c_double)  # 应收客户手续费
        , ('CurrencyCode', c_char * 4)  # 币种
    ]

    def __init__(self, RetCode='', RetInfo='', FutureAccount='', TradeAmt=0.0, CustFee=0.0, CurrencyCode=''):
        super(TransferFutureToBankRspField, self).__init__()

        self.RetCode = self._to_bytes(RetCode)
        self.RetInfo = self._to_bytes(RetInfo)
        self.FutureAccount = self._to_bytes(FutureAccount)
        self.TradeAmt = float(TradeAmt)
        self.CustFee = float(CustFee)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferQryBankReqField(BaseField):
    """查询银行资金请求，TradeCode=204002"""
    _fields_ = [
        ('FutureAccount', c_char * 13)  # ///期货资金账户
        , ('FuturePwdFlag', c_char * 1)  # 密码标志
        , ('FutureAccPwd', c_char * 17)  # 密码
        , ('CurrencyCode', c_char * 4)  # 币种：RMB-人民币 USD-美圆 HKD-港元
    ]

    def __init__(self, FutureAccount='', FuturePwdFlag='', FutureAccPwd='', CurrencyCode=''):
        super(TransferQryBankReqField, self).__init__()

        self.FutureAccount = self._to_bytes(FutureAccount)
        self.FuturePwdFlag = self._to_bytes(FuturePwdFlag)
        self.FutureAccPwd = self._to_bytes(FutureAccPwd)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferQryBankRspField(BaseField):
    """查询银行资金请求响应"""
    _fields_ = [
        ('RetCode', c_char * 5)  # ///响应代码
        , ('RetInfo', c_char * 129)  # 响应信息
        , ('FutureAccount', c_char * 13)  # 资金账户
        , ('TradeAmt', c_double)  # 银行余额
        , ('UseAmt', c_double)  # 银行可用余额
        , ('FetchAmt', c_double)  # 银行可取余额
        , ('CurrencyCode', c_char * 4)  # 币种
    ]

    def __init__(self, RetCode='', RetInfo='', FutureAccount='', TradeAmt=0.0, UseAmt=0.0, FetchAmt=0.0, CurrencyCode=''):
        super(TransferQryBankRspField, self).__init__()

        self.RetCode = self._to_bytes(RetCode)
        self.RetInfo = self._to_bytes(RetInfo)
        self.FutureAccount = self._to_bytes(FutureAccount)
        self.TradeAmt = float(TradeAmt)
        self.UseAmt = float(UseAmt)
        self.FetchAmt = float(FetchAmt)
        self.CurrencyCode = self._to_bytes(CurrencyCode)


class TransferQryDetailReqField(BaseField):
    """查询银行交易明细请求，TradeCode=204999"""
    _fields_ = [
        ('FutureAccount', c_char * 13)  # ///期货资金账户
    ]

    def __init__(self, FutureAccount=''):
        super(TransferQryDetailReqField, self).__init__()

        self.FutureAccount = self._to_bytes(FutureAccount)


class TransferQryDetailRspField(BaseField):
    """查询银行交易明细请求响应"""
    _fields_ = [
        ('TradeDate', c_char * 9)  # ///交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('TradeCode', c_char * 7)  # 交易代码
        , ('FutureSerial', c_int)  # 期货流水号
        , ('FutureID', c_char * 11)  # 期货公司代码
        , ('FutureAccount', c_char * 22)  # 资金帐号
        , ('BankSerial', c_int)  # 银行流水号
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBrchID', c_char * 5)  # 银行分中心代码
        , ('BankAccount', c_char * 41)  # 银行账号
        , ('CertCode', c_char * 21)  # 证件号码
        , ('CurrencyCode', c_char * 4)  # 货币代码
        , ('TxAmount', c_double)  # 发生金额
        , ('Flag', c_char * 1)  # 有效标志
    ]

    def __init__(self, TradeDate='', TradeTime='', TradeCode='', FutureSerial=0, FutureID='', FutureAccount='', BankSerial=0, BankID='', BankBrchID='', BankAccount='', CertCode='', CurrencyCode='', TxAmount=0.0, Flag=''):
        super(TransferQryDetailRspField, self).__init__()

        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.TradeCode = self._to_bytes(TradeCode)
        self.FutureSerial = int(FutureSerial)
        self.FutureID = self._to_bytes(FutureID)
        self.FutureAccount = self._to_bytes(FutureAccount)
        self.BankSerial = int(BankSerial)
        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)
        self.BankAccount = self._to_bytes(BankAccount)
        self.CertCode = self._to_bytes(CertCode)
        self.CurrencyCode = self._to_bytes(CurrencyCode)
        self.TxAmount = float(TxAmount)
        self.Flag = self._to_bytes(Flag)


class RspInfoField(BaseField):
    """响应信息"""
    _fields_ = [
        ('ErrorID', c_int)  # ///错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, ErrorID=0, ErrorMsg=''):
        super(RspInfoField, self).__init__()

        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class ExchangeField(BaseField):
    """交易所"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ExchangeName', c_char * 61)  # 交易所名称
        , ('ExchangeProperty', c_char * 1)  # 交易所属性
    ]

    def __init__(self, ExchangeID='', ExchangeName='', ExchangeProperty=''):
        super(ExchangeField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeName = self._to_bytes(ExchangeName)
        self.ExchangeProperty = self._to_bytes(ExchangeProperty)


class ProductField(BaseField):
    """产品"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('ProductName', c_char * 21)  # 产品名称
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ProductClass', c_char * 1)  # 产品类型
        , ('VolumeMultiple', c_int)  # 合约数量乘数
        , ('PriceTick', c_double)  # 最小变动价位
        , ('MaxMarketOrderVolume', c_int)  # 市价单最大下单量
        , ('MinMarketOrderVolume', c_int)  # 市价单最小下单量
        , ('MaxLimitOrderVolume', c_int)  # 限价单最大下单量
        , ('MinLimitOrderVolume', c_int)  # 限价单最小下单量
        , ('PositionType', c_char * 1)  # 持仓类型
        , ('PositionDateType', c_char * 1)  # 持仓日期类型
        , ('CloseDealType', c_char * 1)  # 平仓处理类型
        , ('TradeCurrencyID', c_char * 4)  # 交易币种类型
        , ('MortgageFundUseRange', c_char * 1)  # 质押资金可用范围
        , ('ExchangeProductID', c_char * 31)  # 交易所产品代码
        , ('UnderlyingMultiple', c_double)  # 合约基础商品乘数
    ]

    def __init__(self, ProductID='', ProductName='', ExchangeID='', ProductClass='', VolumeMultiple=0, PriceTick=0.0, MaxMarketOrderVolume=0, MinMarketOrderVolume=0, MaxLimitOrderVolume=0, MinLimitOrderVolume=0,
                 PositionType='', PositionDateType='', CloseDealType='', TradeCurrencyID='', MortgageFundUseRange='', ExchangeProductID='', UnderlyingMultiple=0.0):
        super(ProductField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.ProductName = self._to_bytes(ProductName)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ProductClass = self._to_bytes(ProductClass)
        self.VolumeMultiple = int(VolumeMultiple)
        self.PriceTick = float(PriceTick)
        self.MaxMarketOrderVolume = int(MaxMarketOrderVolume)
        self.MinMarketOrderVolume = int(MinMarketOrderVolume)
        self.MaxLimitOrderVolume = int(MaxLimitOrderVolume)
        self.MinLimitOrderVolume = int(MinLimitOrderVolume)
        self.PositionType = self._to_bytes(PositionType)
        self.PositionDateType = self._to_bytes(PositionDateType)
        self.CloseDealType = self._to_bytes(CloseDealType)
        self.TradeCurrencyID = self._to_bytes(TradeCurrencyID)
        self.MortgageFundUseRange = self._to_bytes(MortgageFundUseRange)
        self.ExchangeProductID = self._to_bytes(ExchangeProductID)
        self.UnderlyingMultiple = float(UnderlyingMultiple)


class InstrumentField(BaseField):
    """合约"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InstrumentName', c_char * 21)  # 合约名称
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ProductID', c_char * 31)  # 产品代码
        , ('ProductClass', c_char * 1)  # 产品类型
        , ('DeliveryYear', c_int)  # 交割年份
        , ('DeliveryMonth', c_int)  # 交割月
        , ('MaxMarketOrderVolume', c_int)  # 市价单最大下单量
        , ('MinMarketOrderVolume', c_int)  # 市价单最小下单量
        , ('MaxLimitOrderVolume', c_int)  # 限价单最大下单量
        , ('MinLimitOrderVolume', c_int)  # 限价单最小下单量
        , ('VolumeMultiple', c_int)  # 合约数量乘数
        , ('PriceTick', c_double)  # 最小变动价位
        , ('CreateDate', c_char * 9)  # 创建日
        , ('OpenDate', c_char * 9)  # 上市日
        , ('ExpireDate', c_char * 9)  # 到期日
        , ('StartDelivDate', c_char * 9)  # 开始交割日
        , ('EndDelivDate', c_char * 9)  # 结束交割日
        , ('InstLifePhase', c_char * 1)  # 合约生命周期状态
        , ('IsTrading', c_int)  # 当前是否交易
        , ('PositionType', c_char * 1)  # 持仓类型
        , ('PositionDateType', c_char * 1)  # 持仓日期类型
        , ('LongMarginRatio', c_double)  # 多头保证金率
        , ('ShortMarginRatio', c_double)  # 空头保证金率
        , ('MaxMarginSideAlgorithm', c_char * 1)  # 是否使用大额单边保证金算法
        , ('UnderlyingInstrID', c_char * 31)  # 基础商品代码
        , ('StrikePrice', c_double)  # 执行价
        , ('OptionsType', c_char * 1)  # 期权类型
        , ('UnderlyingMultiple', c_double)  # 合约基础商品乘数
        , ('CombinationType', c_char * 1)  # 组合类型
    ]

    def __init__(self, InstrumentID='', ExchangeID='', InstrumentName='', ExchangeInstID='', ProductID='', ProductClass='', DeliveryYear=0, DeliveryMonth=0, MaxMarketOrderVolume=0, MinMarketOrderVolume=0,
                 MaxLimitOrderVolume=0, MinLimitOrderVolume=0, VolumeMultiple=0, PriceTick=0.0, CreateDate='', OpenDate='', ExpireDate='', StartDelivDate='', EndDelivDate='', InstLifePhase='', IsTrading=0, PositionType='',
                 PositionDateType='', LongMarginRatio=0.0, ShortMarginRatio=0.0, MaxMarginSideAlgorithm='', UnderlyingInstrID='', StrikePrice=0.0, OptionsType='', UnderlyingMultiple=0.0, CombinationType=''):
        super(InstrumentField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InstrumentName = self._to_bytes(InstrumentName)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ProductID = self._to_bytes(ProductID)
        self.ProductClass = self._to_bytes(ProductClass)
        self.DeliveryYear = int(DeliveryYear)
        self.DeliveryMonth = int(DeliveryMonth)
        self.MaxMarketOrderVolume = int(MaxMarketOrderVolume)
        self.MinMarketOrderVolume = int(MinMarketOrderVolume)
        self.MaxLimitOrderVolume = int(MaxLimitOrderVolume)
        self.MinLimitOrderVolume = int(MinLimitOrderVolume)
        self.VolumeMultiple = int(VolumeMultiple)
        self.PriceTick = float(PriceTick)
        self.CreateDate = self._to_bytes(CreateDate)
        self.OpenDate = self._to_bytes(OpenDate)
        self.ExpireDate = self._to_bytes(ExpireDate)
        self.StartDelivDate = self._to_bytes(StartDelivDate)
        self.EndDelivDate = self._to_bytes(EndDelivDate)
        self.InstLifePhase = self._to_bytes(InstLifePhase)
        self.IsTrading = int(IsTrading)
        self.PositionType = self._to_bytes(PositionType)
        self.PositionDateType = self._to_bytes(PositionDateType)
        self.LongMarginRatio = float(LongMarginRatio)
        self.ShortMarginRatio = float(ShortMarginRatio)
        self.MaxMarginSideAlgorithm = self._to_bytes(MaxMarginSideAlgorithm)
        self.UnderlyingInstrID = self._to_bytes(UnderlyingInstrID)
        self.StrikePrice = float(StrikePrice)
        self.OptionsType = self._to_bytes(OptionsType)
        self.UnderlyingMultiple = float(UnderlyingMultiple)
        self.CombinationType = self._to_bytes(CombinationType)


class BrokerField(BaseField):
    """经纪公司"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('BrokerAbbr', c_char * 9)  # 经纪公司简称
        , ('BrokerName', c_char * 81)  # 经纪公司名称
        , ('IsActive', c_int)  # 是否活跃
    ]

    def __init__(self, BrokerID='', BrokerAbbr='', BrokerName='', IsActive=0):
        super(BrokerField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerAbbr = self._to_bytes(BrokerAbbr)
        self.BrokerName = self._to_bytes(BrokerName)
        self.IsActive = int(IsActive)


class TraderField(BaseField):
    """交易所交易员"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('Password', c_char * 41)  # 密码
        , ('InstallCount', c_int)  # 安装数量
        , ('BrokerID', c_char * 11)  # 经纪公司代码
    ]

    def __init__(self, ExchangeID='', TraderID='', ParticipantID='', Password='', InstallCount=0, BrokerID=''):
        super(TraderField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.Password = self._to_bytes(Password)
        self.InstallCount = int(InstallCount)
        self.BrokerID = self._to_bytes(BrokerID)


class InvestorField(BaseField):
    """投资者"""
    _fields_ = [
        ('InvestorID', c_char * 13)  # ///投资者代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorGroupID', c_char * 13)  # 投资者分组代码
        , ('InvestorName', c_char * 81)  # 投资者名称
        , ('IdentifiedCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('IsActive', c_int)  # 是否活跃
        , ('Telephone', c_char * 41)  # 联系电话
        , ('Address', c_char * 101)  # 通讯地址
        , ('OpenDate', c_char * 9)  # 开户日期
        , ('Mobile', c_char * 41)  # 手机
        , ('CommModelID', c_char * 13)  # 手续费率模板代码
        , ('MarginModelID', c_char * 13)  # 保证金率模板代码
    ]

    def __init__(self, InvestorID='', BrokerID='', InvestorGroupID='', InvestorName='', IdentifiedCardType='', IdentifiedCardNo='', IsActive=0, Telephone='', Address='', OpenDate='', Mobile='', CommModelID='',
                 MarginModelID=''):
        super(InvestorField, self).__init__()

        self.InvestorID = self._to_bytes(InvestorID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorGroupID = self._to_bytes(InvestorGroupID)
        self.InvestorName = self._to_bytes(InvestorName)
        self.IdentifiedCardType = self._to_bytes(IdentifiedCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.IsActive = int(IsActive)
        self.Telephone = self._to_bytes(Telephone)
        self.Address = self._to_bytes(Address)
        self.OpenDate = self._to_bytes(OpenDate)
        self.Mobile = self._to_bytes(Mobile)
        self.CommModelID = self._to_bytes(CommModelID)
        self.MarginModelID = self._to_bytes(MarginModelID)


class TradingCodeField(BaseField):
    """交易编码"""
    _fields_ = [
        ('InvestorID', c_char * 13)  # ///投资者代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('IsActive', c_int)  # 是否活跃
        , ('ClientIDType', c_char * 1)  # 交易编码类型
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('BizType', c_char * 1)  # 业务类型
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InvestorID='', BrokerID='', ExchangeID='', ClientID='', IsActive=0, ClientIDType='', BranchID='', BizType='', InvestUnitID=''):
        super(TradingCodeField, self).__init__()

        self.InvestorID = self._to_bytes(InvestorID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ClientID = self._to_bytes(ClientID)
        self.IsActive = int(IsActive)
        self.ClientIDType = self._to_bytes(ClientIDType)
        self.BranchID = self._to_bytes(BranchID)
        self.BizType = self._to_bytes(BizType)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class PartBrokerField(BaseField):
    """会员编码和经纪公司编码对照表"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('IsActive', c_int)  # 是否活跃
    ]

    def __init__(self, BrokerID='', ExchangeID='', ParticipantID='', IsActive=0):
        super(PartBrokerField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.IsActive = int(IsActive)


class SuperUserField(BaseField):
    """管理用户"""
    _fields_ = [
        ('UserID', c_char * 16)  # ///用户代码
        , ('UserName', c_char * 81)  # 用户名称
        , ('Password', c_char * 41)  # 密码
        , ('IsActive', c_int)  # 是否活跃
    ]

    def __init__(self, UserID='', UserName='', Password='', IsActive=0):
        super(SuperUserField, self).__init__()

        self.UserID = self._to_bytes(UserID)
        self.UserName = self._to_bytes(UserName)
        self.Password = self._to_bytes(Password)
        self.IsActive = int(IsActive)


class SuperUserFunctionField(BaseField):
    """管理用户功能权限"""
    _fields_ = [
        ('UserID', c_char * 16)  # ///用户代码
        , ('FunctionCode', c_char * 1)  # 功能代码
    ]

    def __init__(self, UserID='', FunctionCode=''):
        super(SuperUserFunctionField, self).__init__()

        self.UserID = self._to_bytes(UserID)
        self.FunctionCode = self._to_bytes(FunctionCode)


class InvestorGroupField(BaseField):
    """投资者组"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorGroupID', c_char * 13)  # 投资者分组代码
        , ('InvestorGroupName', c_char * 41)  # 投资者分组名称
    ]

    def __init__(self, BrokerID='', InvestorGroupID='', InvestorGroupName=''):
        super(InvestorGroupField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorGroupID = self._to_bytes(InvestorGroupID)
        self.InvestorGroupName = self._to_bytes(InvestorGroupName)


class TradingAccountField(BaseField):
    """资金账户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('PreMortgage', c_double)  # 上次质押金额
        , ('PreCredit', c_double)  # 上次信用额度
        , ('PreDeposit', c_double)  # 上次存款额
        , ('PreBalance', c_double)  # 上次结算准备金
        , ('PreMargin', c_double)  # 上次占用的保证金
        , ('InterestBase', c_double)  # 利息基数
        , ('Interest', c_double)  # 利息收入
        , ('Deposit', c_double)  # 入金金额
        , ('Withdraw', c_double)  # 出金金额
        , ('FrozenMargin', c_double)  # 冻结的保证金
        , ('FrozenCash', c_double)  # 冻结的资金
        , ('FrozenCommission', c_double)  # 冻结的手续费
        , ('CurrMargin', c_double)  # 当前保证金总额
        , ('CashIn', c_double)  # 资金差额
        , ('Commission', c_double)  # 手续费
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('PositionProfit', c_double)  # 持仓盈亏
        , ('Balance', c_double)  # 期货结算准备金
        , ('Available', c_double)  # 可用资金
        , ('WithdrawQuota', c_double)  # 可取资金
        , ('Reserve', c_double)  # 基本准备金
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('Credit', c_double)  # 信用额度
        , ('Mortgage', c_double)  # 质押金额
        , ('ExchangeMargin', c_double)  # 交易所保证金
        , ('DeliveryMargin', c_double)  # 投资者交割保证金
        , ('ExchangeDeliveryMargin', c_double)  # 交易所交割保证金
        , ('ReserveBalance', c_double)  # 保底期货结算准备金
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('PreFundMortgageIn', c_double)  # 上次货币质入金额
        , ('PreFundMortgageOut', c_double)  # 上次货币质出金额
        , ('FundMortgageIn', c_double)  # 货币质入金额
        , ('FundMortgageOut', c_double)  # 货币质出金额
        , ('FundMortgageAvailable', c_double)  # 货币质押余额
        , ('MortgageableFund', c_double)  # 可质押货币金额
        , ('SpecProductMargin', c_double)  # 特殊产品占用保证金
        , ('SpecProductFrozenMargin', c_double)  # 特殊产品冻结保证金
        , ('SpecProductCommission', c_double)  # 特殊产品手续费
        , ('SpecProductFrozenCommission', c_double)  # 特殊产品冻结手续费
        , ('SpecProductPositionProfit', c_double)  # 特殊产品持仓盈亏
        , ('SpecProductCloseProfit', c_double)  # 特殊产品平仓盈亏
        , ('SpecProductPositionProfitByAlg', c_double)  # 根据持仓盈亏算法计算的特殊产品持仓盈亏
        , ('SpecProductExchangeMargin', c_double)  # 特殊产品交易所保证金
        , ('BizType', c_char * 1)  # 业务类型
        , ('FrozenSwap', c_double)  # 延时换汇冻结金额
        , ('RemainSwap', c_double)  # 剩余换汇额度
    ]

    def __init__(self, BrokerID='', AccountID='', PreMortgage=0.0, PreCredit=0.0, PreDeposit=0.0, PreBalance=0.0, PreMargin=0.0, InterestBase=0.0, Interest=0.0, Deposit=0.0, Withdraw=0.0, FrozenMargin=0.0, FrozenCash=0.0,
                 FrozenCommission=0.0, CurrMargin=0.0, CashIn=0.0, Commission=0.0, CloseProfit=0.0, PositionProfit=0.0, Balance=0.0, Available=0.0, WithdrawQuota=0.0, Reserve=0.0, TradingDay='', SettlementID=0, Credit=0.0,
                 Mortgage=0.0, ExchangeMargin=0.0, DeliveryMargin=0.0, ExchangeDeliveryMargin=0.0, ReserveBalance=0.0, CurrencyID='', PreFundMortgageIn=0.0, PreFundMortgageOut=0.0, FundMortgageIn=0.0, FundMortgageOut=0.0,
                 FundMortgageAvailable=0.0, MortgageableFund=0.0, SpecProductMargin=0.0, SpecProductFrozenMargin=0.0, SpecProductCommission=0.0, SpecProductFrozenCommission=0.0, SpecProductPositionProfit=0.0,
                 SpecProductCloseProfit=0.0, SpecProductPositionProfitByAlg=0.0, SpecProductExchangeMargin=0.0, BizType='', FrozenSwap=0.0, RemainSwap=0.0):
        super(TradingAccountField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.PreMortgage = float(PreMortgage)
        self.PreCredit = float(PreCredit)
        self.PreDeposit = float(PreDeposit)
        self.PreBalance = float(PreBalance)
        self.PreMargin = float(PreMargin)
        self.InterestBase = float(InterestBase)
        self.Interest = float(Interest)
        self.Deposit = float(Deposit)
        self.Withdraw = float(Withdraw)
        self.FrozenMargin = float(FrozenMargin)
        self.FrozenCash = float(FrozenCash)
        self.FrozenCommission = float(FrozenCommission)
        self.CurrMargin = float(CurrMargin)
        self.CashIn = float(CashIn)
        self.Commission = float(Commission)
        self.CloseProfit = float(CloseProfit)
        self.PositionProfit = float(PositionProfit)
        self.Balance = float(Balance)
        self.Available = float(Available)
        self.WithdrawQuota = float(WithdrawQuota)
        self.Reserve = float(Reserve)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.Credit = float(Credit)
        self.Mortgage = float(Mortgage)
        self.ExchangeMargin = float(ExchangeMargin)
        self.DeliveryMargin = float(DeliveryMargin)
        self.ExchangeDeliveryMargin = float(ExchangeDeliveryMargin)
        self.ReserveBalance = float(ReserveBalance)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.PreFundMortgageIn = float(PreFundMortgageIn)
        self.PreFundMortgageOut = float(PreFundMortgageOut)
        self.FundMortgageIn = float(FundMortgageIn)
        self.FundMortgageOut = float(FundMortgageOut)
        self.FundMortgageAvailable = float(FundMortgageAvailable)
        self.MortgageableFund = float(MortgageableFund)
        self.SpecProductMargin = float(SpecProductMargin)
        self.SpecProductFrozenMargin = float(SpecProductFrozenMargin)
        self.SpecProductCommission = float(SpecProductCommission)
        self.SpecProductFrozenCommission = float(SpecProductFrozenCommission)
        self.SpecProductPositionProfit = float(SpecProductPositionProfit)
        self.SpecProductCloseProfit = float(SpecProductCloseProfit)
        self.SpecProductPositionProfitByAlg = float(SpecProductPositionProfitByAlg)
        self.SpecProductExchangeMargin = float(SpecProductExchangeMargin)
        self.BizType = self._to_bytes(BizType)
        self.FrozenSwap = float(FrozenSwap)
        self.RemainSwap = float(RemainSwap)


class InvestorPositionField(BaseField):
    """投资者持仓"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('PosiDirection', c_char * 1)  # 持仓多空方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('PositionDate', c_char * 1)  # 持仓日期
        , ('YdPosition', c_int)  # 上日持仓
        , ('Position', c_int)  # 今日持仓
        , ('LongFrozen', c_int)  # 多头冻结
        , ('ShortFrozen', c_int)  # 空头冻结
        , ('LongFrozenAmount', c_double)  # 开仓冻结金额
        , ('ShortFrozenAmount', c_double)  # 开仓冻结金额
        , ('OpenVolume', c_int)  # 开仓量
        , ('CloseVolume', c_int)  # 平仓量
        , ('OpenAmount', c_double)  # 开仓金额
        , ('CloseAmount', c_double)  # 平仓金额
        , ('PositionCost', c_double)  # 持仓成本
        , ('PreMargin', c_double)  # 上次占用的保证金
        , ('UseMargin', c_double)  # 占用的保证金
        , ('FrozenMargin', c_double)  # 冻结的保证金
        , ('FrozenCash', c_double)  # 冻结的资金
        , ('FrozenCommission', c_double)  # 冻结的手续费
        , ('CashIn', c_double)  # 资金差额
        , ('Commission', c_double)  # 手续费
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('PositionProfit', c_double)  # 持仓盈亏
        , ('PreSettlementPrice', c_double)  # 上次结算价
        , ('SettlementPrice', c_double)  # 本次结算价
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OpenCost', c_double)  # 开仓成本
        , ('ExchangeMargin', c_double)  # 交易所保证金
        , ('CombPosition', c_int)  # 组合成交形成的持仓
        , ('CombLongFrozen', c_int)  # 组合多头冻结
        , ('CombShortFrozen', c_int)  # 组合空头冻结
        , ('CloseProfitByDate', c_double)  # 逐日盯市平仓盈亏
        , ('CloseProfitByTrade', c_double)  # 逐笔对冲平仓盈亏
        , ('TodayPosition', c_int)  # 今日持仓
        , ('MarginRateByMoney', c_double)  # 保证金率
        , ('MarginRateByVolume', c_double)  # 保证金率(按手数)
        , ('StrikeFrozen', c_int)  # 执行冻结
        , ('StrikeFrozenAmount', c_double)  # 执行冻结金额
        , ('AbandonFrozen', c_int)  # 放弃执行冻结
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('YdStrikeFrozen', c_int)  # 执行冻结的昨仓
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('PositionCostOffset', c_double)  # 大商所持仓成本差值，只有大商所使用
    ]

    def __init__(self, InstrumentID='', BrokerID='', InvestorID='', PosiDirection='', HedgeFlag='', PositionDate='', YdPosition=0, Position=0, LongFrozen=0, ShortFrozen=0, LongFrozenAmount=0.0, ShortFrozenAmount=0.0,
                 OpenVolume=0, CloseVolume=0, OpenAmount=0.0, CloseAmount=0.0, PositionCost=0.0, PreMargin=0.0, UseMargin=0.0, FrozenMargin=0.0, FrozenCash=0.0, FrozenCommission=0.0, CashIn=0.0, Commission=0.0,
                 CloseProfit=0.0, PositionProfit=0.0, PreSettlementPrice=0.0, SettlementPrice=0.0, TradingDay='', SettlementID=0, OpenCost=0.0, ExchangeMargin=0.0, CombPosition=0, CombLongFrozen=0, CombShortFrozen=0,
                 CloseProfitByDate=0.0, CloseProfitByTrade=0.0, TodayPosition=0, MarginRateByMoney=0.0, MarginRateByVolume=0.0, StrikeFrozen=0, StrikeFrozenAmount=0.0, AbandonFrozen=0, ExchangeID='', YdStrikeFrozen=0,
                 InvestUnitID='', PositionCostOffset=0.0):
        super(InvestorPositionField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.PositionDate = self._to_bytes(PositionDate)
        self.YdPosition = int(YdPosition)
        self.Position = int(Position)
        self.LongFrozen = int(LongFrozen)
        self.ShortFrozen = int(ShortFrozen)
        self.LongFrozenAmount = float(LongFrozenAmount)
        self.ShortFrozenAmount = float(ShortFrozenAmount)
        self.OpenVolume = int(OpenVolume)
        self.CloseVolume = int(CloseVolume)
        self.OpenAmount = float(OpenAmount)
        self.CloseAmount = float(CloseAmount)
        self.PositionCost = float(PositionCost)
        self.PreMargin = float(PreMargin)
        self.UseMargin = float(UseMargin)
        self.FrozenMargin = float(FrozenMargin)
        self.FrozenCash = float(FrozenCash)
        self.FrozenCommission = float(FrozenCommission)
        self.CashIn = float(CashIn)
        self.Commission = float(Commission)
        self.CloseProfit = float(CloseProfit)
        self.PositionProfit = float(PositionProfit)
        self.PreSettlementPrice = float(PreSettlementPrice)
        self.SettlementPrice = float(SettlementPrice)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OpenCost = float(OpenCost)
        self.ExchangeMargin = float(ExchangeMargin)
        self.CombPosition = int(CombPosition)
        self.CombLongFrozen = int(CombLongFrozen)
        self.CombShortFrozen = int(CombShortFrozen)
        self.CloseProfitByDate = float(CloseProfitByDate)
        self.CloseProfitByTrade = float(CloseProfitByTrade)
        self.TodayPosition = int(TodayPosition)
        self.MarginRateByMoney = float(MarginRateByMoney)
        self.MarginRateByVolume = float(MarginRateByVolume)
        self.StrikeFrozen = int(StrikeFrozen)
        self.StrikeFrozenAmount = float(StrikeFrozenAmount)
        self.AbandonFrozen = int(AbandonFrozen)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.YdStrikeFrozen = int(YdStrikeFrozen)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.PositionCostOffset = float(PositionCostOffset)


class InstrumentMarginRateField(BaseField):
    """合约保证金率"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 空头保证金费
        , ('IsRelative', c_int)  # 是否相对交易所收取
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0,
                 IsRelative=0, ExchangeID='', InvestUnitID=''):
        super(InstrumentMarginRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)
        self.IsRelative = int(IsRelative)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class InstrumentCommissionRateField(BaseField):
    """合约手续费率"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OpenRatioByMoney', c_double)  # 开仓手续费率
        , ('OpenRatioByVolume', c_double)  # 开仓手续费
        , ('CloseRatioByMoney', c_double)  # 平仓手续费率
        , ('CloseRatioByVolume', c_double)  # 平仓手续费
        , ('CloseTodayRatioByMoney', c_double)  # 平今手续费率
        , ('CloseTodayRatioByVolume', c_double)  # 平今手续费
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('BizType', c_char * 1)  # 业务类型
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', OpenRatioByMoney=0.0, OpenRatioByVolume=0.0, CloseRatioByMoney=0.0, CloseRatioByVolume=0.0, CloseTodayRatioByMoney=0.0,
                 CloseTodayRatioByVolume=0.0, ExchangeID='', BizType='', InvestUnitID=''):
        super(InstrumentCommissionRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OpenRatioByMoney = float(OpenRatioByMoney)
        self.OpenRatioByVolume = float(OpenRatioByVolume)
        self.CloseRatioByMoney = float(CloseRatioByMoney)
        self.CloseRatioByVolume = float(CloseRatioByVolume)
        self.CloseTodayRatioByMoney = float(CloseTodayRatioByMoney)
        self.CloseTodayRatioByVolume = float(CloseTodayRatioByVolume)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.BizType = self._to_bytes(BizType)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class DepthMarketDataField(BaseField):
    """深度行情"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('LastPrice', c_double)  # 最新价
        , ('PreSettlementPrice', c_double)  # 上次结算价
        , ('PreClosePrice', c_double)  # 昨收盘
        , ('PreOpenInterest', c_double)  # 昨持仓量
        , ('OpenPrice', c_double)  # 今开盘
        , ('HighestPrice', c_double)  # 最高价
        , ('LowestPrice', c_double)  # 最低价
        , ('Volume', c_int)  # 数量
        , ('Turnover', c_double)  # 成交金额
        , ('OpenInterest', c_double)  # 持仓量
        , ('ClosePrice', c_double)  # 今收盘
        , ('SettlementPrice', c_double)  # 本次结算价
        , ('UpperLimitPrice', c_double)  # 涨停板价
        , ('LowerLimitPrice', c_double)  # 跌停板价
        , ('PreDelta', c_double)  # 昨虚实度
        , ('CurrDelta', c_double)  # 今虚实度
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('UpdateMillisec', c_int)  # 最后修改毫秒
        , ('BidPrice1', c_double)  # 申买价一
        , ('BidVolume1', c_int)  # 申买量一
        , ('AskPrice1', c_double)  # 申卖价一
        , ('AskVolume1', c_int)  # 申卖量一
        , ('BidPrice2', c_double)  # 申买价二
        , ('BidVolume2', c_int)  # 申买量二
        , ('AskPrice2', c_double)  # 申卖价二
        , ('AskVolume2', c_int)  # 申卖量二
        , ('BidPrice3', c_double)  # 申买价三
        , ('BidVolume3', c_int)  # 申买量三
        , ('AskPrice3', c_double)  # 申卖价三
        , ('AskVolume3', c_int)  # 申卖量三
        , ('BidPrice4', c_double)  # 申买价四
        , ('BidVolume4', c_int)  # 申买量四
        , ('AskPrice4', c_double)  # 申卖价四
        , ('AskVolume4', c_int)  # 申卖量四
        , ('BidPrice5', c_double)  # 申买价五
        , ('BidVolume5', c_int)  # 申买量五
        , ('AskPrice5', c_double)  # 申卖价五
        , ('AskVolume5', c_int)  # 申卖量五
        , ('AveragePrice', c_double)  # 当日均价
        , ('ActionDay', c_char * 9)  # 业务日期
    ]

    def __init__(self, TradingDay='', InstrumentID='', ExchangeID='', ExchangeInstID='', LastPrice=0.0, PreSettlementPrice=0.0, PreClosePrice=0.0, PreOpenInterest=0.0, OpenPrice=0.0, HighestPrice=0.0, LowestPrice=0.0,
                 Volume=0, Turnover=0.0, OpenInterest=0.0, ClosePrice=0.0, SettlementPrice=0.0, UpperLimitPrice=0.0, LowerLimitPrice=0.0, PreDelta=0.0, CurrDelta=0.0, UpdateTime='', UpdateMillisec=0, BidPrice1=0.0,
                 BidVolume1=0, AskPrice1=0.0, AskVolume1=0, BidPrice2=0.0, BidVolume2=0, AskPrice2=0.0, AskVolume2=0, BidPrice3=0.0, BidVolume3=0, AskPrice3=0.0, AskVolume3=0, BidPrice4=0.0, BidVolume4=0, AskPrice4=0.0,
                 AskVolume4=0, BidPrice5=0.0, BidVolume5=0, AskPrice5=0.0, AskVolume5=0, AveragePrice=0.0, ActionDay=''):
        super(DepthMarketDataField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.LastPrice = float(LastPrice)
        self.PreSettlementPrice = float(PreSettlementPrice)
        self.PreClosePrice = float(PreClosePrice)
        self.PreOpenInterest = float(PreOpenInterest)
        self.OpenPrice = float(OpenPrice)
        self.HighestPrice = float(HighestPrice)
        self.LowestPrice = float(LowestPrice)
        self.Volume = int(Volume)
        self.Turnover = float(Turnover)
        self.OpenInterest = float(OpenInterest)
        self.ClosePrice = float(ClosePrice)
        self.SettlementPrice = float(SettlementPrice)
        self.UpperLimitPrice = float(UpperLimitPrice)
        self.LowerLimitPrice = float(LowerLimitPrice)
        self.PreDelta = float(PreDelta)
        self.CurrDelta = float(CurrDelta)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.UpdateMillisec = int(UpdateMillisec)
        self.BidPrice1 = float(BidPrice1)
        self.BidVolume1 = int(BidVolume1)
        self.AskPrice1 = float(AskPrice1)
        self.AskVolume1 = int(AskVolume1)
        self.BidPrice2 = float(BidPrice2)
        self.BidVolume2 = int(BidVolume2)
        self.AskPrice2 = float(AskPrice2)
        self.AskVolume2 = int(AskVolume2)
        self.BidPrice3 = float(BidPrice3)
        self.BidVolume3 = int(BidVolume3)
        self.AskPrice3 = float(AskPrice3)
        self.AskVolume3 = int(AskVolume3)
        self.BidPrice4 = float(BidPrice4)
        self.BidVolume4 = int(BidVolume4)
        self.AskPrice4 = float(AskPrice4)
        self.AskVolume4 = int(AskVolume4)
        self.BidPrice5 = float(BidPrice5)
        self.BidVolume5 = int(BidVolume5)
        self.AskPrice5 = float(AskPrice5)
        self.AskVolume5 = int(AskVolume5)
        self.AveragePrice = float(AveragePrice)
        self.ActionDay = self._to_bytes(ActionDay)


class InstrumentTradingRightField(BaseField):
    """投资者合约交易权限"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('TradingRight', c_char * 1)  # 交易权限
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', TradingRight=''):
        super(InstrumentTradingRightField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.TradingRight = self._to_bytes(TradingRight)


class BrokerUserField(BaseField):
    """经纪公司用户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserName', c_char * 81)  # 用户名称
        , ('UserType', c_char * 1)  # 用户类型
        , ('IsActive', c_int)  # 是否活跃
        , ('IsUsingOTP', c_int)  # 是否使用令牌
        , ('IsAuthForce', c_int)  # 是否强制终端认证
    ]

    def __init__(self, BrokerID='', UserID='', UserName='', UserType='', IsActive=0, IsUsingOTP=0, IsAuthForce=0):
        super(BrokerUserField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserName = self._to_bytes(UserName)
        self.UserType = self._to_bytes(UserType)
        self.IsActive = int(IsActive)
        self.IsUsingOTP = int(IsUsingOTP)
        self.IsAuthForce = int(IsAuthForce)


class BrokerUserPasswordField(BaseField):
    """经纪公司用户口令"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('Password', c_char * 41)  # 密码
        , ('LastUpdateTime', c_char * 17)  # 上次修改时间
        , ('LastLoginTime', c_char * 17)  # 上次登陆时间
        , ('ExpireDate', c_char * 9)  # 密码过期时间
        , ('WeakExpireDate', c_char * 9)  # 弱密码过期时间
    ]

    def __init__(self, BrokerID='', UserID='', Password='', LastUpdateTime='', LastLoginTime='', ExpireDate='', WeakExpireDate=''):
        super(BrokerUserPasswordField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.Password = self._to_bytes(Password)
        self.LastUpdateTime = self._to_bytes(LastUpdateTime)
        self.LastLoginTime = self._to_bytes(LastLoginTime)
        self.ExpireDate = self._to_bytes(ExpireDate)
        self.WeakExpireDate = self._to_bytes(WeakExpireDate)


class BrokerUserFunctionField(BaseField):
    """经纪公司用户功能权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('BrokerFunctionCode', c_char * 1)  # 经纪公司功能代码
    ]

    def __init__(self, BrokerID='', UserID='', BrokerFunctionCode=''):
        super(BrokerUserFunctionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.BrokerFunctionCode = self._to_bytes(BrokerFunctionCode)


class TraderOfferField(BaseField):
    """交易所交易员报盘机"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('Password', c_char * 41)  # 密码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('TraderConnectStatus', c_char * 1)  # 交易所交易员连接状态
        , ('ConnectRequestDate', c_char * 9)  # 发出连接请求的日期
        , ('ConnectRequestTime', c_char * 9)  # 发出连接请求的时间
        , ('LastReportDate', c_char * 9)  # 上次报告日期
        , ('LastReportTime', c_char * 9)  # 上次报告时间
        , ('ConnectDate', c_char * 9)  # 完成连接日期
        , ('ConnectTime', c_char * 9)  # 完成连接时间
        , ('StartDate', c_char * 9)  # 启动日期
        , ('StartTime', c_char * 9)  # 启动时间
        , ('TradingDay', c_char * 9)  # 交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('MaxTradeID', c_char * 21)  # 本席位最大成交编号
        , ('MaxOrderMessageReference', c_char * 7)  # 本席位最大报单备拷
    ]

    def __init__(self, ExchangeID='', TraderID='', ParticipantID='', Password='', InstallID=0, OrderLocalID='', TraderConnectStatus='', ConnectRequestDate='', ConnectRequestTime='', LastReportDate='', LastReportTime='',
                 ConnectDate='', ConnectTime='', StartDate='', StartTime='', TradingDay='', BrokerID='', MaxTradeID='', MaxOrderMessageReference=''):
        super(TraderOfferField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.TraderConnectStatus = self._to_bytes(TraderConnectStatus)
        self.ConnectRequestDate = self._to_bytes(ConnectRequestDate)
        self.ConnectRequestTime = self._to_bytes(ConnectRequestTime)
        self.LastReportDate = self._to_bytes(LastReportDate)
        self.LastReportTime = self._to_bytes(LastReportTime)
        self.ConnectDate = self._to_bytes(ConnectDate)
        self.ConnectTime = self._to_bytes(ConnectTime)
        self.StartDate = self._to_bytes(StartDate)
        self.StartTime = self._to_bytes(StartTime)
        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.MaxTradeID = self._to_bytes(MaxTradeID)
        self.MaxOrderMessageReference = self._to_bytes(MaxOrderMessageReference)


class SettlementInfoField(BaseField):
    """投资者结算结果"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('SequenceNo', c_int)  # 序号
        , ('Content', c_char * 501)  # 消息正文
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, TradingDay='', SettlementID=0, BrokerID='', InvestorID='', SequenceNo=0, Content='', AccountID='', CurrencyID=''):
        super(SettlementInfoField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.SequenceNo = int(SequenceNo)
        self.Content = self._to_bytes(Content)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class InstrumentMarginRateAdjustField(BaseField):
    """合约保证金率调整"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 空头保证金费
        , ('IsRelative', c_int)  # 是否相对交易所收取
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0,
                 IsRelative=0):
        super(InstrumentMarginRateAdjustField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)
        self.IsRelative = int(IsRelative)


class ExchangeMarginRateField(BaseField):
    """交易所保证金率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 空头保证金费
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InstrumentID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0, ExchangeID=''):
        super(ExchangeMarginRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ExchangeMarginRateAdjustField(BaseField):
    """交易所保证金率调整"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 跟随交易所投资者多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 跟随交易所投资者多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 跟随交易所投资者空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 跟随交易所投资者空头保证金费
        , ('ExchLongMarginRatioByMoney', c_double)  # 交易所多头保证金率
        , ('ExchLongMarginRatioByVolume', c_double)  # 交易所多头保证金费
        , ('ExchShortMarginRatioByMoney', c_double)  # 交易所空头保证金率
        , ('ExchShortMarginRatioByVolume', c_double)  # 交易所空头保证金费
        , ('NoLongMarginRatioByMoney', c_double)  # 不跟随交易所投资者多头保证金率
        , ('NoLongMarginRatioByVolume', c_double)  # 不跟随交易所投资者多头保证金费
        , ('NoShortMarginRatioByMoney', c_double)  # 不跟随交易所投资者空头保证金率
        , ('NoShortMarginRatioByVolume', c_double)  # 不跟随交易所投资者空头保证金费
    ]

    def __init__(self, BrokerID='', InstrumentID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0, ExchLongMarginRatioByMoney=0.0,
                 ExchLongMarginRatioByVolume=0.0, ExchShortMarginRatioByMoney=0.0, ExchShortMarginRatioByVolume=0.0, NoLongMarginRatioByMoney=0.0, NoLongMarginRatioByVolume=0.0, NoShortMarginRatioByMoney=0.0,
                 NoShortMarginRatioByVolume=0.0):
        super(ExchangeMarginRateAdjustField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)
        self.ExchLongMarginRatioByMoney = float(ExchLongMarginRatioByMoney)
        self.ExchLongMarginRatioByVolume = float(ExchLongMarginRatioByVolume)
        self.ExchShortMarginRatioByMoney = float(ExchShortMarginRatioByMoney)
        self.ExchShortMarginRatioByVolume = float(ExchShortMarginRatioByVolume)
        self.NoLongMarginRatioByMoney = float(NoLongMarginRatioByMoney)
        self.NoLongMarginRatioByVolume = float(NoLongMarginRatioByVolume)
        self.NoShortMarginRatioByMoney = float(NoShortMarginRatioByMoney)
        self.NoShortMarginRatioByVolume = float(NoShortMarginRatioByVolume)


class ExchangeRateField(BaseField):
    """汇率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('FromCurrencyID', c_char * 4)  # 源币种
        , ('FromCurrencyUnit', c_double)  # 源币种单位数量
        , ('ToCurrencyID', c_char * 4)  # 目标币种
        , ('ExchangeRate', c_double)  # 汇率
    ]

    def __init__(self, BrokerID='', FromCurrencyID='', FromCurrencyUnit=0.0, ToCurrencyID='', ExchangeRate=0.0):
        super(ExchangeRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.FromCurrencyID = self._to_bytes(FromCurrencyID)
        self.FromCurrencyUnit = float(FromCurrencyUnit)
        self.ToCurrencyID = self._to_bytes(ToCurrencyID)
        self.ExchangeRate = float(ExchangeRate)


class SettlementRefField(BaseField):
    """结算引用"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('SettlementID', c_int)  # 结算编号
    ]

    def __init__(self, TradingDay='', SettlementID=0):
        super(SettlementRefField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)


class CurrentTimeField(BaseField):
    """当前时间"""
    _fields_ = [
        ('CurrDate', c_char * 9)  # ///当前日期
        , ('CurrTime', c_char * 9)  # 当前时间
        , ('CurrMillisec', c_int)  # 当前时间（毫秒）
        , ('ActionDay', c_char * 9)  # 业务日期
    ]

    def __init__(self, CurrDate='', CurrTime='', CurrMillisec=0, ActionDay=''):
        super(CurrentTimeField, self).__init__()

        self.CurrDate = self._to_bytes(CurrDate)
        self.CurrTime = self._to_bytes(CurrTime)
        self.CurrMillisec = int(CurrMillisec)
        self.ActionDay = self._to_bytes(ActionDay)


class CommPhaseField(BaseField):
    """通讯阶段"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('CommPhaseNo', c_short)  # 通讯时段编号
        , ('SystemID', c_char * 21)  # 系统编号
    ]

    def __init__(self, TradingDay='', CommPhaseNo=0, SystemID=''):
        super(CommPhaseField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.CommPhaseNo = int(CommPhaseNo)
        self.SystemID = self._to_bytes(SystemID)


class LoginInfoField(BaseField):
    """登录信息"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('LoginDate', c_char * 9)  # 登录日期
        , ('LoginTime', c_char * 9)  # 登录时间
        , ('IPAddress', c_char * 16)  # IP地址
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('SystemName', c_char * 41)  # 系统名称
        , ('PasswordDeprecated', c_char * 41)  # 密码,已弃用
        , ('MaxOrderRef', c_char * 13)  # 最大报单引用
        , ('SHFETime', c_char * 9)  # 上期所时间
        , ('DCETime', c_char * 9)  # 大商所时间
        , ('CZCETime', c_char * 9)  # 郑商所时间
        , ('FFEXTime', c_char * 9)  # 中金所时间
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('OneTimePassword', c_char * 41)  # 动态密码
        , ('INETime', c_char * 9)  # 能源中心时间
        , ('IsQryControl', c_int)  # 查询时是否需要流控
        , ('LoginRemark', c_char * 36)  # 登录备注
        , ('Password', c_char * 41)  # 密码
    ]

    def __init__(self, FrontID=0, SessionID=0, BrokerID='', UserID='', LoginDate='', LoginTime='', IPAddress='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', SystemName='', PasswordDeprecated='',
                 MaxOrderRef='', SHFETime='', DCETime='', CZCETime='', FFEXTime='', MacAddress='', OneTimePassword='', INETime='', IsQryControl=0, LoginRemark='', Password=''):
        super(LoginInfoField, self).__init__()

        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.LoginDate = self._to_bytes(LoginDate)
        self.LoginTime = self._to_bytes(LoginTime)
        self.IPAddress = self._to_bytes(IPAddress)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.SystemName = self._to_bytes(SystemName)
        self.PasswordDeprecated = self._to_bytes(PasswordDeprecated)
        self.MaxOrderRef = self._to_bytes(MaxOrderRef)
        self.SHFETime = self._to_bytes(SHFETime)
        self.DCETime = self._to_bytes(DCETime)
        self.CZCETime = self._to_bytes(CZCETime)
        self.FFEXTime = self._to_bytes(FFEXTime)
        self.MacAddress = self._to_bytes(MacAddress)
        self.OneTimePassword = self._to_bytes(OneTimePassword)
        self.INETime = self._to_bytes(INETime)
        self.IsQryControl = int(IsQryControl)
        self.LoginRemark = self._to_bytes(LoginRemark)
        self.Password = self._to_bytes(Password)


class LogoutAllField(BaseField):
    """登录信息"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('SystemName', c_char * 41)  # 系统名称
    ]

    def __init__(self, FrontID=0, SessionID=0, SystemName=''):
        super(LogoutAllField, self).__init__()
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.SystemName = self._to_bytes(SystemName)


class FrontStatusField(BaseField):
    """前置状态"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
        , ('LastReportDate', c_char * 9)  # 上次报告日期
        , ('LastReportTime', c_char * 9)  # 上次报告时间
        , ('IsActive', c_int)  # 是否活跃
    ]

    def __init__(self, FrontID=0, LastReportDate='', LastReportTime='', IsActive=0):
        super(FrontStatusField, self).__init__()

        self.FrontID = int(FrontID)
        self.LastReportDate = self._to_bytes(LastReportDate)
        self.LastReportTime = self._to_bytes(LastReportTime)
        self.IsActive = int(IsActive)


class UserPasswordUpdateField(BaseField):
    """用户口令变更"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('OldPassword', c_char * 41)  # 原来的口令
        , ('NewPassword', c_char * 41)  # 新的口令
    ]

    def __init__(self, BrokerID='', UserID='', OldPassword='', NewPassword=''):
        super(UserPasswordUpdateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.OldPassword = self._to_bytes(OldPassword)
        self.NewPassword = self._to_bytes(NewPassword)


class InputOrderField(BaseField):
    """输入报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('OrderPriceType', c_char * 1)  # 报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('UserForceClose', c_int)  # 用户强评标志
        , ('IsSwapOrder', c_int)  # 互换单标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='',
                 GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='', StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, UserForceClose=0, IsSwapOrder=0, ExchangeID='',
                 InvestUnitID='', AccountID='', CurrencyID='', ClientID='', IPAddress='', MacAddress=''):
        super(InputOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.UserForceClose = int(UserForceClose)
        self.IsSwapOrder = int(IsSwapOrder)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class OrderField(BaseField):
    """报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('OrderPriceType', c_char * 1)  # 报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 报单提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('OrderSource', c_char * 1)  # 报单来源
        , ('OrderStatus', c_char * 1)  # 报单状态
        , ('OrderType', c_char * 1)  # 报单类型
        , ('VolumeTraded', c_int)  # 今成交数量
        , ('VolumeTotal', c_int)  # 剩余数量
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 委托时间
        , ('ActiveTime', c_char * 9)  # 激活时间
        , ('SuspendTime', c_char * 9)  # 挂起时间
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ActiveTraderID', c_char * 21)  # 最后修改交易所交易员代码
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('UserForceClose', c_int)  # 用户强评标志
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerOrderSeq', c_int)  # 经纪公司报单编号
        , ('RelativeOrderSysID', c_char * 21)  # 相关报单
        , ('ZCETotalTradedVolume', c_int)  # 郑商所成交数量
        , ('IsSwapOrder', c_int)  # 互换单标志
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='',
                 GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='', StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, OrderLocalID='', ExchangeID='', ParticipantID='',
                 ClientID='', ExchangeInstID='', TraderID='', InstallID=0, OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, OrderSysID='', OrderSource='', OrderStatus='', OrderType='', VolumeTraded=0,
                 VolumeTotal=0, InsertDate='', InsertTime='', ActiveTime='', SuspendTime='', UpdateTime='', CancelTime='', ActiveTraderID='', ClearingPartID='', SequenceNo=0, FrontID=0, SessionID=0, UserProductInfo='',
                 StatusMsg='', UserForceClose=0, ActiveUserID='', BrokerOrderSeq=0, RelativeOrderSysID='', ZCETotalTradedVolume=0, IsSwapOrder=0, BranchID='', InvestUnitID='', AccountID='', CurrencyID='', IPAddress='',
                 MacAddress=''):
        super(OrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.OrderSource = self._to_bytes(OrderSource)
        self.OrderStatus = self._to_bytes(OrderStatus)
        self.OrderType = self._to_bytes(OrderType)
        self.VolumeTraded = int(VolumeTraded)
        self.VolumeTotal = int(VolumeTotal)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.ActiveTime = self._to_bytes(ActiveTime)
        self.SuspendTime = self._to_bytes(SuspendTime)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ActiveTraderID = self._to_bytes(ActiveTraderID)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.UserForceClose = int(UserForceClose)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerOrderSeq = int(BrokerOrderSeq)
        self.RelativeOrderSysID = self._to_bytes(RelativeOrderSysID)
        self.ZCETotalTradedVolume = int(ZCETotalTradedVolume)
        self.IsSwapOrder = int(IsSwapOrder)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExchangeOrderField(BaseField):
    """交易所报单"""
    _fields_ = [
        ('OrderPriceType', c_char * 1)  # ///报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 报单提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('OrderSource', c_char * 1)  # 报单来源
        , ('OrderStatus', c_char * 1)  # 报单状态
        , ('OrderType', c_char * 1)  # 报单类型
        , ('VolumeTraded', c_int)  # 今成交数量
        , ('VolumeTotal', c_int)  # 剩余数量
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 委托时间
        , ('ActiveTime', c_char * 9)  # 激活时间
        , ('SuspendTime', c_char * 9)  # 挂起时间
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ActiveTraderID', c_char * 21)  # 最后修改交易所交易员代码
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='', GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='',
                 StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, OrderLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0,
                 OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, OrderSysID='', OrderSource='', OrderStatus='', OrderType='', VolumeTraded=0, VolumeTotal=0, InsertDate='', InsertTime='',
                 ActiveTime='', SuspendTime='', UpdateTime='', CancelTime='', ActiveTraderID='', ClearingPartID='', SequenceNo=0, BranchID='', IPAddress='', MacAddress=''):
        super(ExchangeOrderField, self).__init__()

        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.OrderSource = self._to_bytes(OrderSource)
        self.OrderStatus = self._to_bytes(OrderStatus)
        self.OrderType = self._to_bytes(OrderType)
        self.VolumeTraded = int(VolumeTraded)
        self.VolumeTotal = int(VolumeTotal)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.ActiveTime = self._to_bytes(ActiveTime)
        self.SuspendTime = self._to_bytes(SuspendTime)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ActiveTraderID = self._to_bytes(ActiveTraderID)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExchangeOrderInsertErrorField(BaseField):
    """交易所报单插入失败"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, ExchangeID='', ParticipantID='', TraderID='', InstallID=0, OrderLocalID='', ErrorID=0, ErrorMsg=''):
        super(ExchangeOrderInsertErrorField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class InputOrderActionField(BaseField):
    """输入报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeChange', c_int)  # 数量变化
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, OrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OrderSysID='', ActionFlag='', LimitPrice=0.0, VolumeChange=0, UserID='',
                 InstrumentID='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(InputOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.OrderRef = self._to_bytes(OrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeChange = int(VolumeChange)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class OrderActionField(BaseField):
    """报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeChange', c_int)  # 数量变化
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, OrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OrderSysID='', ActionFlag='', LimitPrice=0.0, VolumeChange=0, ActionDate='',
                 ActionTime='', TraderID='', InstallID=0, OrderLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', StatusMsg='', InstrumentID='', BranchID='',
                 InvestUnitID='', IPAddress='', MacAddress=''):
        super(OrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.OrderRef = self._to_bytes(OrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeChange = int(VolumeChange)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExchangeOrderActionField(BaseField):
    """交易所报单操作"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeChange', c_int)  # 数量变化
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, ExchangeID='', OrderSysID='', ActionFlag='', LimitPrice=0.0, VolumeChange=0, ActionDate='', ActionTime='', TraderID='', InstallID=0, OrderLocalID='', ActionLocalID='', ParticipantID='', ClientID='',
                 BusinessUnit='', OrderActionStatus='', UserID='', BranchID='', IPAddress='', MacAddress=''):
        super(ExchangeOrderActionField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeChange = int(VolumeChange)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExchangeOrderActionErrorField(BaseField):
    """交易所报单操作失败"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, ExchangeID='', OrderSysID='', TraderID='', InstallID=0, OrderLocalID='', ActionLocalID='', ErrorID=0, ErrorMsg=''):
        super(ExchangeOrderActionErrorField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class ExchangeTradeField(BaseField):
    """交易所成交"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('TradeID', c_char * 21)  # 成交编号
        , ('Direction', c_char * 1)  # 买卖方向
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('TradingRole', c_char * 1)  # 交易角色
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('Price', c_double)  # 价格
        , ('Volume', c_int)  # 数量
        , ('TradeDate', c_char * 9)  # 成交时期
        , ('TradeTime', c_char * 9)  # 成交时间
        , ('TradeType', c_char * 1)  # 成交类型
        , ('PriceSource', c_char * 1)  # 成交价来源
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('SequenceNo', c_int)  # 序号
        , ('TradeSource', c_char * 1)  # 成交来源
    ]

    def __init__(self, ExchangeID='', TradeID='', Direction='', OrderSysID='', ParticipantID='', ClientID='', TradingRole='', ExchangeInstID='', OffsetFlag='', HedgeFlag='', Price=0.0, Volume=0, TradeDate='', TradeTime='',
                 TradeType='', PriceSource='', TraderID='', OrderLocalID='', ClearingPartID='', BusinessUnit='', SequenceNo=0, TradeSource=''):
        super(ExchangeTradeField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TradeID = self._to_bytes(TradeID)
        self.Direction = self._to_bytes(Direction)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.TradingRole = self._to_bytes(TradingRole)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.Price = float(Price)
        self.Volume = int(Volume)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.TradeType = self._to_bytes(TradeType)
        self.PriceSource = self._to_bytes(PriceSource)
        self.TraderID = self._to_bytes(TraderID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.SequenceNo = int(SequenceNo)
        self.TradeSource = self._to_bytes(TradeSource)


class TradeField(BaseField):
    """成交"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TradeID', c_char * 21)  # 成交编号
        , ('Direction', c_char * 1)  # 买卖方向
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('TradingRole', c_char * 1)  # 交易角色
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('Price', c_double)  # 价格
        , ('Volume', c_int)  # 数量
        , ('TradeDate', c_char * 9)  # 成交时期
        , ('TradeTime', c_char * 9)  # 成交时间
        , ('TradeType', c_char * 1)  # 成交类型
        , ('PriceSource', c_char * 1)  # 成交价来源
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('SequenceNo', c_int)  # 序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('BrokerOrderSeq', c_int)  # 经纪公司报单编号
        , ('TradeSource', c_char * 1)  # 成交来源
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', ExchangeID='', TradeID='', Direction='', OrderSysID='', ParticipantID='', ClientID='', TradingRole='', ExchangeInstID='',
                 OffsetFlag='', HedgeFlag='', Price=0.0, Volume=0, TradeDate='', TradeTime='', TradeType='', PriceSource='', TraderID='', OrderLocalID='', ClearingPartID='', BusinessUnit='', SequenceNo=0, TradingDay='',
                 SettlementID=0, BrokerOrderSeq=0, TradeSource='', InvestUnitID=''):
        super(TradeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TradeID = self._to_bytes(TradeID)
        self.Direction = self._to_bytes(Direction)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.TradingRole = self._to_bytes(TradingRole)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.Price = float(Price)
        self.Volume = int(Volume)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.TradeType = self._to_bytes(TradeType)
        self.PriceSource = self._to_bytes(PriceSource)
        self.TraderID = self._to_bytes(TraderID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.SequenceNo = int(SequenceNo)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.BrokerOrderSeq = int(BrokerOrderSeq)
        self.TradeSource = self._to_bytes(TradeSource)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class UserSessionField(BaseField):
    """用户会话"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('LoginDate', c_char * 9)  # 登录日期
        , ('LoginTime', c_char * 9)  # 登录时间
        , ('IPAddress', c_char * 16)  # IP地址
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('LoginRemark', c_char * 36)  # 登录备注
    ]

    def __init__(self, FrontID=0, SessionID=0, BrokerID='', UserID='', LoginDate='', LoginTime='', IPAddress='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', MacAddress='', LoginRemark=''):
        super(UserSessionField, self).__init__()

        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.LoginDate = self._to_bytes(LoginDate)
        self.LoginTime = self._to_bytes(LoginTime)
        self.IPAddress = self._to_bytes(IPAddress)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.MacAddress = self._to_bytes(MacAddress)
        self.LoginRemark = self._to_bytes(LoginRemark)


class QueryMaxOrderVolumeField(BaseField):
    """查询最大报单数量"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('MaxVolume', c_int)  # 最大允许报单数量
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', Direction='', OffsetFlag='', HedgeFlag='', MaxVolume=0, ExchangeID='', InvestUnitID=''):
        super(QueryMaxOrderVolumeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.Direction = self._to_bytes(Direction)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.MaxVolume = int(MaxVolume)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class SettlementInfoConfirmField(BaseField):
    """投资者结算结果确认信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ConfirmDate', c_char * 9)  # 确认日期
        , ('ConfirmTime', c_char * 9)  # 确认时间
        , ('SettlementID', c_int)  # 结算编号
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ConfirmDate='', ConfirmTime='', SettlementID=0, AccountID='', CurrencyID=''):
        super(SettlementInfoConfirmField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ConfirmDate = self._to_bytes(ConfirmDate)
        self.ConfirmTime = self._to_bytes(ConfirmTime)
        self.SettlementID = int(SettlementID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class SyncDepositField(BaseField):
    """出入金同步"""
    _fields_ = [
        ('DepositSeqNo', c_char * 15)  # ///出入金流水号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Deposit', c_double)  # 入金金额
        , ('IsForce', c_int)  # 是否强制进行
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, DepositSeqNo='', BrokerID='', InvestorID='', Deposit=0.0, IsForce=0, CurrencyID=''):
        super(SyncDepositField, self).__init__()

        self.DepositSeqNo = self._to_bytes(DepositSeqNo)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Deposit = float(Deposit)
        self.IsForce = int(IsForce)
        self.CurrencyID = self._to_bytes(CurrencyID)


class SyncFundMortgageField(BaseField):
    """货币质押同步"""
    _fields_ = [
        ('MortgageSeqNo', c_char * 15)  # ///货币质押流水号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('FromCurrencyID', c_char * 4)  # 源币种
        , ('MortgageAmount', c_double)  # 质押金额
        , ('ToCurrencyID', c_char * 4)  # 目标币种
    ]

    def __init__(self, MortgageSeqNo='', BrokerID='', InvestorID='', FromCurrencyID='', MortgageAmount=0.0, ToCurrencyID=''):
        super(SyncFundMortgageField, self).__init__()

        self.MortgageSeqNo = self._to_bytes(MortgageSeqNo)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.FromCurrencyID = self._to_bytes(FromCurrencyID)
        self.MortgageAmount = float(MortgageAmount)
        self.ToCurrencyID = self._to_bytes(ToCurrencyID)


class BrokerSyncField(BaseField):
    """经纪公司同步"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(BrokerSyncField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class SyncingInvestorField(BaseField):
    """正在同步中的投资者"""
    _fields_ = [
        ('InvestorID', c_char * 13)  # ///投资者代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorGroupID', c_char * 13)  # 投资者分组代码
        , ('InvestorName', c_char * 81)  # 投资者名称
        , ('IdentifiedCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('IsActive', c_int)  # 是否活跃
        , ('Telephone', c_char * 41)  # 联系电话
        , ('Address', c_char * 101)  # 通讯地址
        , ('OpenDate', c_char * 9)  # 开户日期
        , ('Mobile', c_char * 41)  # 手机
        , ('CommModelID', c_char * 13)  # 手续费率模板代码
        , ('MarginModelID', c_char * 13)  # 保证金率模板代码
    ]

    def __init__(self, InvestorID='', BrokerID='', InvestorGroupID='', InvestorName='', IdentifiedCardType='', IdentifiedCardNo='', IsActive=0, Telephone='', Address='', OpenDate='', Mobile='', CommModelID='',
                 MarginModelID=''):
        super(SyncingInvestorField, self).__init__()

        self.InvestorID = self._to_bytes(InvestorID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorGroupID = self._to_bytes(InvestorGroupID)
        self.InvestorName = self._to_bytes(InvestorName)
        self.IdentifiedCardType = self._to_bytes(IdentifiedCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.IsActive = int(IsActive)
        self.Telephone = self._to_bytes(Telephone)
        self.Address = self._to_bytes(Address)
        self.OpenDate = self._to_bytes(OpenDate)
        self.Mobile = self._to_bytes(Mobile)
        self.CommModelID = self._to_bytes(CommModelID)
        self.MarginModelID = self._to_bytes(MarginModelID)


class SyncingTradingCodeField(BaseField):
    """正在同步中的交易代码"""
    _fields_ = [
        ('InvestorID', c_char * 13)  # ///投资者代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('IsActive', c_int)  # 是否活跃
        , ('ClientIDType', c_char * 1)  # 交易编码类型
    ]

    def __init__(self, InvestorID='', BrokerID='', ExchangeID='', ClientID='', IsActive=0, ClientIDType=''):
        super(SyncingTradingCodeField, self).__init__()

        self.InvestorID = self._to_bytes(InvestorID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ClientID = self._to_bytes(ClientID)
        self.IsActive = int(IsActive)
        self.ClientIDType = self._to_bytes(ClientIDType)


class SyncingInvestorGroupField(BaseField):
    """正在同步中的投资者分组"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorGroupID', c_char * 13)  # 投资者分组代码
        , ('InvestorGroupName', c_char * 41)  # 投资者分组名称
    ]

    def __init__(self, BrokerID='', InvestorGroupID='', InvestorGroupName=''):
        super(SyncingInvestorGroupField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorGroupID = self._to_bytes(InvestorGroupID)
        self.InvestorGroupName = self._to_bytes(InvestorGroupName)


class SyncingTradingAccountField(BaseField):
    """正在同步中的交易账号"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('PreMortgage', c_double)  # 上次质押金额
        , ('PreCredit', c_double)  # 上次信用额度
        , ('PreDeposit', c_double)  # 上次存款额
        , ('PreBalance', c_double)  # 上次结算准备金
        , ('PreMargin', c_double)  # 上次占用的保证金
        , ('InterestBase', c_double)  # 利息基数
        , ('Interest', c_double)  # 利息收入
        , ('Deposit', c_double)  # 入金金额
        , ('Withdraw', c_double)  # 出金金额
        , ('FrozenMargin', c_double)  # 冻结的保证金
        , ('FrozenCash', c_double)  # 冻结的资金
        , ('FrozenCommission', c_double)  # 冻结的手续费
        , ('CurrMargin', c_double)  # 当前保证金总额
        , ('CashIn', c_double)  # 资金差额
        , ('Commission', c_double)  # 手续费
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('PositionProfit', c_double)  # 持仓盈亏
        , ('Balance', c_double)  # 期货结算准备金
        , ('Available', c_double)  # 可用资金
        , ('WithdrawQuota', c_double)  # 可取资金
        , ('Reserve', c_double)  # 基本准备金
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('Credit', c_double)  # 信用额度
        , ('Mortgage', c_double)  # 质押金额
        , ('ExchangeMargin', c_double)  # 交易所保证金
        , ('DeliveryMargin', c_double)  # 投资者交割保证金
        , ('ExchangeDeliveryMargin', c_double)  # 交易所交割保证金
        , ('ReserveBalance', c_double)  # 保底期货结算准备金
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('PreFundMortgageIn', c_double)  # 上次货币质入金额
        , ('PreFundMortgageOut', c_double)  # 上次货币质出金额
        , ('FundMortgageIn', c_double)  # 货币质入金额
        , ('FundMortgageOut', c_double)  # 货币质出金额
        , ('FundMortgageAvailable', c_double)  # 货币质押余额
        , ('MortgageableFund', c_double)  # 可质押货币金额
        , ('SpecProductMargin', c_double)  # 特殊产品占用保证金
        , ('SpecProductFrozenMargin', c_double)  # 特殊产品冻结保证金
        , ('SpecProductCommission', c_double)  # 特殊产品手续费
        , ('SpecProductFrozenCommission', c_double)  # 特殊产品冻结手续费
        , ('SpecProductPositionProfit', c_double)  # 特殊产品持仓盈亏
        , ('SpecProductCloseProfit', c_double)  # 特殊产品平仓盈亏
        , ('SpecProductPositionProfitByAlg', c_double)  # 根据持仓盈亏算法计算的特殊产品持仓盈亏
        , ('SpecProductExchangeMargin', c_double)  # 特殊产品交易所保证金
        , ('FrozenSwap', c_double)  # 延时换汇冻结金额
        , ('RemainSwap', c_double)  # 剩余换汇额度
    ]

    def __init__(self, BrokerID='', AccountID='', PreMortgage=0.0, PreCredit=0.0, PreDeposit=0.0, PreBalance=0.0, PreMargin=0.0, InterestBase=0.0, Interest=0.0, Deposit=0.0, Withdraw=0.0, FrozenMargin=0.0, FrozenCash=0.0,
                 FrozenCommission=0.0, CurrMargin=0.0, CashIn=0.0, Commission=0.0, CloseProfit=0.0, PositionProfit=0.0, Balance=0.0, Available=0.0, WithdrawQuota=0.0, Reserve=0.0, TradingDay='', SettlementID=0, Credit=0.0,
                 Mortgage=0.0, ExchangeMargin=0.0, DeliveryMargin=0.0, ExchangeDeliveryMargin=0.0, ReserveBalance=0.0, CurrencyID='', PreFundMortgageIn=0.0, PreFundMortgageOut=0.0, FundMortgageIn=0.0, FundMortgageOut=0.0,
                 FundMortgageAvailable=0.0, MortgageableFund=0.0, SpecProductMargin=0.0, SpecProductFrozenMargin=0.0, SpecProductCommission=0.0, SpecProductFrozenCommission=0.0, SpecProductPositionProfit=0.0,
                 SpecProductCloseProfit=0.0, SpecProductPositionProfitByAlg=0.0, SpecProductExchangeMargin=0.0, FrozenSwap=0.0, RemainSwap=0.0):
        super(SyncingTradingAccountField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.PreMortgage = float(PreMortgage)
        self.PreCredit = float(PreCredit)
        self.PreDeposit = float(PreDeposit)
        self.PreBalance = float(PreBalance)
        self.PreMargin = float(PreMargin)
        self.InterestBase = float(InterestBase)
        self.Interest = float(Interest)
        self.Deposit = float(Deposit)
        self.Withdraw = float(Withdraw)
        self.FrozenMargin = float(FrozenMargin)
        self.FrozenCash = float(FrozenCash)
        self.FrozenCommission = float(FrozenCommission)
        self.CurrMargin = float(CurrMargin)
        self.CashIn = float(CashIn)
        self.Commission = float(Commission)
        self.CloseProfit = float(CloseProfit)
        self.PositionProfit = float(PositionProfit)
        self.Balance = float(Balance)
        self.Available = float(Available)
        self.WithdrawQuota = float(WithdrawQuota)
        self.Reserve = float(Reserve)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.Credit = float(Credit)
        self.Mortgage = float(Mortgage)
        self.ExchangeMargin = float(ExchangeMargin)
        self.DeliveryMargin = float(DeliveryMargin)
        self.ExchangeDeliveryMargin = float(ExchangeDeliveryMargin)
        self.ReserveBalance = float(ReserveBalance)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.PreFundMortgageIn = float(PreFundMortgageIn)
        self.PreFundMortgageOut = float(PreFundMortgageOut)
        self.FundMortgageIn = float(FundMortgageIn)
        self.FundMortgageOut = float(FundMortgageOut)
        self.FundMortgageAvailable = float(FundMortgageAvailable)
        self.MortgageableFund = float(MortgageableFund)
        self.SpecProductMargin = float(SpecProductMargin)
        self.SpecProductFrozenMargin = float(SpecProductFrozenMargin)
        self.SpecProductCommission = float(SpecProductCommission)
        self.SpecProductFrozenCommission = float(SpecProductFrozenCommission)
        self.SpecProductPositionProfit = float(SpecProductPositionProfit)
        self.SpecProductCloseProfit = float(SpecProductCloseProfit)
        self.SpecProductPositionProfitByAlg = float(SpecProductPositionProfitByAlg)
        self.SpecProductExchangeMargin = float(SpecProductExchangeMargin)
        self.FrozenSwap = float(FrozenSwap)
        self.RemainSwap = float(RemainSwap)


class SyncingInvestorPositionField(BaseField):
    """正在同步中的投资者持仓"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('PosiDirection', c_char * 1)  # 持仓多空方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('PositionDate', c_char * 1)  # 持仓日期
        , ('YdPosition', c_int)  # 上日持仓
        , ('Position', c_int)  # 今日持仓
        , ('LongFrozen', c_int)  # 多头冻结
        , ('ShortFrozen', c_int)  # 空头冻结
        , ('LongFrozenAmount', c_double)  # 开仓冻结金额
        , ('ShortFrozenAmount', c_double)  # 开仓冻结金额
        , ('OpenVolume', c_int)  # 开仓量
        , ('CloseVolume', c_int)  # 平仓量
        , ('OpenAmount', c_double)  # 开仓金额
        , ('CloseAmount', c_double)  # 平仓金额
        , ('PositionCost', c_double)  # 持仓成本
        , ('PreMargin', c_double)  # 上次占用的保证金
        , ('UseMargin', c_double)  # 占用的保证金
        , ('FrozenMargin', c_double)  # 冻结的保证金
        , ('FrozenCash', c_double)  # 冻结的资金
        , ('FrozenCommission', c_double)  # 冻结的手续费
        , ('CashIn', c_double)  # 资金差额
        , ('Commission', c_double)  # 手续费
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('PositionProfit', c_double)  # 持仓盈亏
        , ('PreSettlementPrice', c_double)  # 上次结算价
        , ('SettlementPrice', c_double)  # 本次结算价
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OpenCost', c_double)  # 开仓成本
        , ('ExchangeMargin', c_double)  # 交易所保证金
        , ('CombPosition', c_int)  # 组合成交形成的持仓
        , ('CombLongFrozen', c_int)  # 组合多头冻结
        , ('CombShortFrozen', c_int)  # 组合空头冻结
        , ('CloseProfitByDate', c_double)  # 逐日盯市平仓盈亏
        , ('CloseProfitByTrade', c_double)  # 逐笔对冲平仓盈亏
        , ('TodayPosition', c_int)  # 今日持仓
        , ('MarginRateByMoney', c_double)  # 保证金率
        , ('MarginRateByVolume', c_double)  # 保证金率(按手数)
        , ('StrikeFrozen', c_int)  # 执行冻结
        , ('StrikeFrozenAmount', c_double)  # 执行冻结金额
        , ('AbandonFrozen', c_int)  # 放弃执行冻结
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('YdStrikeFrozen', c_int)  # 执行冻结的昨仓
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('PositionCostOffset', c_double)  # 大商所持仓成本差值，只有大商所使用
    ]

    def __init__(self, InstrumentID='', BrokerID='', InvestorID='', PosiDirection='', HedgeFlag='', PositionDate='', YdPosition=0, Position=0, LongFrozen=0, ShortFrozen=0, LongFrozenAmount=0.0, ShortFrozenAmount=0.0,
                 OpenVolume=0, CloseVolume=0, OpenAmount=0.0, CloseAmount=0.0, PositionCost=0.0, PreMargin=0.0, UseMargin=0.0, FrozenMargin=0.0, FrozenCash=0.0, FrozenCommission=0.0, CashIn=0.0, Commission=0.0,
                 CloseProfit=0.0, PositionProfit=0.0, PreSettlementPrice=0.0, SettlementPrice=0.0, TradingDay='', SettlementID=0, OpenCost=0.0, ExchangeMargin=0.0, CombPosition=0, CombLongFrozen=0, CombShortFrozen=0,
                 CloseProfitByDate=0.0, CloseProfitByTrade=0.0, TodayPosition=0, MarginRateByMoney=0.0, MarginRateByVolume=0.0, StrikeFrozen=0, StrikeFrozenAmount=0.0, AbandonFrozen=0, ExchangeID='', YdStrikeFrozen=0,
                 InvestUnitID='', PositionCostOffset=0.0):
        super(SyncingInvestorPositionField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.PositionDate = self._to_bytes(PositionDate)
        self.YdPosition = int(YdPosition)
        self.Position = int(Position)
        self.LongFrozen = int(LongFrozen)
        self.ShortFrozen = int(ShortFrozen)
        self.LongFrozenAmount = float(LongFrozenAmount)
        self.ShortFrozenAmount = float(ShortFrozenAmount)
        self.OpenVolume = int(OpenVolume)
        self.CloseVolume = int(CloseVolume)
        self.OpenAmount = float(OpenAmount)
        self.CloseAmount = float(CloseAmount)
        self.PositionCost = float(PositionCost)
        self.PreMargin = float(PreMargin)
        self.UseMargin = float(UseMargin)
        self.FrozenMargin = float(FrozenMargin)
        self.FrozenCash = float(FrozenCash)
        self.FrozenCommission = float(FrozenCommission)
        self.CashIn = float(CashIn)
        self.Commission = float(Commission)
        self.CloseProfit = float(CloseProfit)
        self.PositionProfit = float(PositionProfit)
        self.PreSettlementPrice = float(PreSettlementPrice)
        self.SettlementPrice = float(SettlementPrice)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OpenCost = float(OpenCost)
        self.ExchangeMargin = float(ExchangeMargin)
        self.CombPosition = int(CombPosition)
        self.CombLongFrozen = int(CombLongFrozen)
        self.CombShortFrozen = int(CombShortFrozen)
        self.CloseProfitByDate = float(CloseProfitByDate)
        self.CloseProfitByTrade = float(CloseProfitByTrade)
        self.TodayPosition = int(TodayPosition)
        self.MarginRateByMoney = float(MarginRateByMoney)
        self.MarginRateByVolume = float(MarginRateByVolume)
        self.StrikeFrozen = int(StrikeFrozen)
        self.StrikeFrozenAmount = float(StrikeFrozenAmount)
        self.AbandonFrozen = int(AbandonFrozen)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.YdStrikeFrozen = int(YdStrikeFrozen)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.PositionCostOffset = float(PositionCostOffset)


class SyncingInstrumentMarginRateField(BaseField):
    """正在同步中的合约保证金率"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 空头保证金费
        , ('IsRelative', c_int)  # 是否相对交易所收取
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0,
                 IsRelative=0):
        super(SyncingInstrumentMarginRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)
        self.IsRelative = int(IsRelative)


class SyncingInstrumentCommissionRateField(BaseField):
    """正在同步中的合约手续费率"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OpenRatioByMoney', c_double)  # 开仓手续费率
        , ('OpenRatioByVolume', c_double)  # 开仓手续费
        , ('CloseRatioByMoney', c_double)  # 平仓手续费率
        , ('CloseRatioByVolume', c_double)  # 平仓手续费
        , ('CloseTodayRatioByMoney', c_double)  # 平今手续费率
        , ('CloseTodayRatioByVolume', c_double)  # 平今手续费
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', OpenRatioByMoney=0.0, OpenRatioByVolume=0.0, CloseRatioByMoney=0.0, CloseRatioByVolume=0.0, CloseTodayRatioByMoney=0.0,
                 CloseTodayRatioByVolume=0.0):
        super(SyncingInstrumentCommissionRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OpenRatioByMoney = float(OpenRatioByMoney)
        self.OpenRatioByVolume = float(OpenRatioByVolume)
        self.CloseRatioByMoney = float(CloseRatioByMoney)
        self.CloseRatioByVolume = float(CloseRatioByVolume)
        self.CloseTodayRatioByMoney = float(CloseTodayRatioByMoney)
        self.CloseTodayRatioByVolume = float(CloseTodayRatioByVolume)


class SyncingInstrumentTradingRightField(BaseField):
    """正在同步中的合约交易权限"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('TradingRight', c_char * 1)  # 交易权限
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', TradingRight=''):
        super(SyncingInstrumentTradingRightField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.TradingRight = self._to_bytes(TradingRight)


class QryOrderField(BaseField):
    """查询报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', OrderSysID='', InsertTimeStart='', InsertTimeEnd='', InvestUnitID=''):
        super(QryOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryTradeField(BaseField):
    """查询成交"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TradeID', c_char * 21)  # 成交编号
        , ('TradeTimeStart', c_char * 9)  # 开始时间
        , ('TradeTimeEnd', c_char * 9)  # 结束时间
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', TradeID='', TradeTimeStart='', TradeTimeEnd='', InvestUnitID=''):
        super(QryTradeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TradeID = self._to_bytes(TradeID)
        self.TradeTimeStart = self._to_bytes(TradeTimeStart)
        self.TradeTimeEnd = self._to_bytes(TradeTimeEnd)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInvestorPositionField(BaseField):
    """查询投资者持仓"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryInvestorPositionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryTradingAccountField(BaseField):
    """查询资金账户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('BizType', c_char * 1)  # 业务类型
        , ('AccountID', c_char * 13)  # 投资者帐号
    ]

    def __init__(self, BrokerID='', InvestorID='', CurrencyID='', BizType='', AccountID=''):
        super(QryTradingAccountField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.BizType = self._to_bytes(BizType)
        self.AccountID = self._to_bytes(AccountID)


class QryInvestorField(BaseField):
    """查询投资者"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryInvestorField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class QryTradingCodeField(BaseField):
    """查询交易编码"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ClientIDType', c_char * 1)  # 交易编码类型
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID='', ClientID='', ClientIDType='', InvestUnitID=''):
        super(QryTradingCodeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ClientID = self._to_bytes(ClientID)
        self.ClientIDType = self._to_bytes(ClientIDType)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInvestorGroupField(BaseField):
    """查询投资者组"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(QryInvestorGroupField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class QryInstrumentMarginRateField(BaseField):
    """查询合约保证金率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', HedgeFlag='', ExchangeID='', InvestUnitID=''):
        super(QryInstrumentMarginRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInstrumentCommissionRateField(BaseField):
    """查询手续费率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryInstrumentCommissionRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInstrumentTradingRightField(BaseField):
    """查询合约交易权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID=''):
        super(QryInstrumentTradingRightField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class QryBrokerField(BaseField):
    """查询经纪公司"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(QryBrokerField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class QryTraderField(BaseField):
    """查询交易员"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ExchangeID='', ParticipantID='', TraderID=''):
        super(QryTraderField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.TraderID = self._to_bytes(TraderID)


class QrySuperUserFunctionField(BaseField):
    """查询管理用户功能权限"""
    _fields_ = [
        ('UserID', c_char * 16)  # ///用户代码
    ]

    def __init__(self, UserID=''):
        super(QrySuperUserFunctionField, self).__init__()

        self.UserID = self._to_bytes(UserID)


class QryUserSessionField(BaseField):
    """查询用户会话"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, FrontID=0, SessionID=0, BrokerID='', UserID=''):
        super(QryUserSessionField, self).__init__()

        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class QryPartBrokerField(BaseField):
    """查询经纪公司会员代码"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('ParticipantID', c_char * 11)  # 会员代码
    ]

    def __init__(self, ExchangeID='', BrokerID='', ParticipantID=''):
        super(QryPartBrokerField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.ParticipantID = self._to_bytes(ParticipantID)


class QryFrontStatusField(BaseField):
    """查询前置状态"""
    _fields_ = [
        ('FrontID', c_int)  # ///前置编号
    ]

    def __init__(self, FrontID=0):
        super(QryFrontStatusField, self).__init__()

        self.FrontID = int(FrontID)


class QryExchangeOrderField(BaseField):
    """查询交易所报单"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeInstID='', ExchangeID='', TraderID=''):
        super(QryExchangeOrderField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class QryOrderActionField(BaseField):
    """查询报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID=''):
        super(QryOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryExchangeOrderActionField(BaseField):
    """查询交易所报单操作"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeID='', TraderID=''):
        super(QryExchangeOrderActionField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class QrySuperUserField(BaseField):
    """查询管理用户"""
    _fields_ = [
        ('UserID', c_char * 16)  # ///用户代码
    ]

    def __init__(self, UserID=''):
        super(QrySuperUserField, self).__init__()

        self.UserID = self._to_bytes(UserID)


class QryExchangeField(BaseField):
    """查询交易所"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
    ]

    def __init__(self, ExchangeID=''):
        super(QryExchangeField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)


class QryProductField(BaseField):
    """查询产品"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('ProductClass', c_char * 1)  # 产品类型
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, ProductID='', ProductClass='', ExchangeID=''):
        super(QryProductField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.ProductClass = self._to_bytes(ProductClass)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryInstrumentField(BaseField):
    """查询合约"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ProductID', c_char * 31)  # 产品代码
    ]

    def __init__(self, InstrumentID='', ExchangeID='', ExchangeInstID='', ProductID=''):
        super(QryInstrumentField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ProductID = self._to_bytes(ProductID)


class QryDepthMarketDataField(BaseField):
    """查询行情"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, InstrumentID='', ExchangeID=''):
        super(QryDepthMarketDataField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryBrokerUserField(BaseField):
    """查询经纪公司用户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(QryBrokerUserField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class QryBrokerUserFunctionField(BaseField):
    """查询经纪公司用户权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(QryBrokerUserFunctionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class QryTraderOfferField(BaseField):
    """查询交易员报盘机"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ExchangeID='', ParticipantID='', TraderID=''):
        super(QryTraderOfferField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.TraderID = self._to_bytes(TraderID)


class QrySyncDepositField(BaseField):
    """查询出入金流水"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('DepositSeqNo', c_char * 15)  # 出入金流水号
    ]

    def __init__(self, BrokerID='', DepositSeqNo=''):
        super(QrySyncDepositField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.DepositSeqNo = self._to_bytes(DepositSeqNo)


class QrySettlementInfoField(BaseField):
    """查询投资者结算结果"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('TradingDay', c_char * 9)  # 交易日
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', InvestorID='', TradingDay='', AccountID='', CurrencyID=''):
        super(QrySettlementInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.TradingDay = self._to_bytes(TradingDay)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class QryExchangeMarginRateField(BaseField):
    """查询交易所保证金率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InstrumentID='', HedgeFlag='', ExchangeID=''):
        super(QryExchangeMarginRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryExchangeMarginRateAdjustField(BaseField):
    """查询交易所调整保证金率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
    ]

    def __init__(self, BrokerID='', InstrumentID='', HedgeFlag=''):
        super(QryExchangeMarginRateAdjustField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)


class QryExchangeRateField(BaseField):
    """查询汇率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('FromCurrencyID', c_char * 4)  # 源币种
        , ('ToCurrencyID', c_char * 4)  # 目标币种
    ]

    def __init__(self, BrokerID='', FromCurrencyID='', ToCurrencyID=''):
        super(QryExchangeRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.FromCurrencyID = self._to_bytes(FromCurrencyID)
        self.ToCurrencyID = self._to_bytes(ToCurrencyID)


class QrySyncFundMortgageField(BaseField):
    """查询货币质押流水"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('MortgageSeqNo', c_char * 15)  # 货币质押流水号
    ]

    def __init__(self, BrokerID='', MortgageSeqNo=''):
        super(QrySyncFundMortgageField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.MortgageSeqNo = self._to_bytes(MortgageSeqNo)


class QryHisOrderField(BaseField):
    """查询报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', OrderSysID='', InsertTimeStart='', InsertTimeEnd='', TradingDay='', SettlementID=0):
        super(QryHisOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)


class OptionInstrMiniMarginField(BaseField):
    """当前期权合约最小保证金"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('MinMargin', c_double)  # 单位（手）期权合约最小保证金
        , ('ValueMethod', c_char * 1)  # 取值方式
        , ('IsRelative', c_int)  # 是否跟随交易所收取
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', MinMargin=0.0, ValueMethod='', IsRelative=0):
        super(OptionInstrMiniMarginField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.MinMargin = float(MinMargin)
        self.ValueMethod = self._to_bytes(ValueMethod)
        self.IsRelative = int(IsRelative)


class OptionInstrMarginAdjustField(BaseField):
    """当前期权合约保证金调整系数"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('SShortMarginRatioByMoney', c_double)  # 投机空头保证金调整系数
        , ('SShortMarginRatioByVolume', c_double)  # 投机空头保证金调整系数
        , ('HShortMarginRatioByMoney', c_double)  # 保值空头保证金调整系数
        , ('HShortMarginRatioByVolume', c_double)  # 保值空头保证金调整系数
        , ('AShortMarginRatioByMoney', c_double)  # 套利空头保证金调整系数
        , ('AShortMarginRatioByVolume', c_double)  # 套利空头保证金调整系数
        , ('IsRelative', c_int)  # 是否跟随交易所收取
        , ('MShortMarginRatioByMoney', c_double)  # 做市商空头保证金调整系数
        , ('MShortMarginRatioByVolume', c_double)  # 做市商空头保证金调整系数
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', SShortMarginRatioByMoney=0.0, SShortMarginRatioByVolume=0.0, HShortMarginRatioByMoney=0.0, HShortMarginRatioByVolume=0.0,
                 AShortMarginRatioByMoney=0.0, AShortMarginRatioByVolume=0.0, IsRelative=0, MShortMarginRatioByMoney=0.0, MShortMarginRatioByVolume=0.0):
        super(OptionInstrMarginAdjustField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.SShortMarginRatioByMoney = float(SShortMarginRatioByMoney)
        self.SShortMarginRatioByVolume = float(SShortMarginRatioByVolume)
        self.HShortMarginRatioByMoney = float(HShortMarginRatioByMoney)
        self.HShortMarginRatioByVolume = float(HShortMarginRatioByVolume)
        self.AShortMarginRatioByMoney = float(AShortMarginRatioByMoney)
        self.AShortMarginRatioByVolume = float(AShortMarginRatioByVolume)
        self.IsRelative = int(IsRelative)
        self.MShortMarginRatioByMoney = float(MShortMarginRatioByMoney)
        self.MShortMarginRatioByVolume = float(MShortMarginRatioByVolume)


class OptionInstrCommRateField(BaseField):
    """当前期权合约手续费的详细内容"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OpenRatioByMoney', c_double)  # 开仓手续费率
        , ('OpenRatioByVolume', c_double)  # 开仓手续费
        , ('CloseRatioByMoney', c_double)  # 平仓手续费率
        , ('CloseRatioByVolume', c_double)  # 平仓手续费
        , ('CloseTodayRatioByMoney', c_double)  # 平今手续费率
        , ('CloseTodayRatioByVolume', c_double)  # 平今手续费
        , ('StrikeRatioByMoney', c_double)  # 执行手续费率
        , ('StrikeRatioByVolume', c_double)  # 执行手续费
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', OpenRatioByMoney=0.0, OpenRatioByVolume=0.0, CloseRatioByMoney=0.0, CloseRatioByVolume=0.0, CloseTodayRatioByMoney=0.0,
                 CloseTodayRatioByVolume=0.0, StrikeRatioByMoney=0.0, StrikeRatioByVolume=0.0, ExchangeID='', InvestUnitID=''):
        super(OptionInstrCommRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OpenRatioByMoney = float(OpenRatioByMoney)
        self.OpenRatioByVolume = float(OpenRatioByVolume)
        self.CloseRatioByMoney = float(CloseRatioByMoney)
        self.CloseRatioByVolume = float(CloseRatioByVolume)
        self.CloseTodayRatioByMoney = float(CloseTodayRatioByMoney)
        self.CloseTodayRatioByVolume = float(CloseTodayRatioByVolume)
        self.StrikeRatioByMoney = float(StrikeRatioByMoney)
        self.StrikeRatioByVolume = float(StrikeRatioByVolume)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class OptionInstrTradeCostField(BaseField):
    """期权交易成本"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('FixedMargin', c_double)  # 期权合约保证金不变部分
        , ('MiniMargin', c_double)  # 期权合约最小保证金
        , ('Royalty', c_double)  # 期权合约权利金
        , ('ExchFixedMargin', c_double)  # 交易所期权合约保证金不变部分
        , ('ExchMiniMargin', c_double)  # 交易所期权合约最小保证金
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', HedgeFlag='', FixedMargin=0.0, MiniMargin=0.0, Royalty=0.0, ExchFixedMargin=0.0, ExchMiniMargin=0.0, ExchangeID='', InvestUnitID=''):
        super(OptionInstrTradeCostField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.FixedMargin = float(FixedMargin)
        self.MiniMargin = float(MiniMargin)
        self.Royalty = float(Royalty)
        self.ExchFixedMargin = float(ExchFixedMargin)
        self.ExchMiniMargin = float(ExchMiniMargin)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryOptionInstrTradeCostField(BaseField):
    """期权交易成本查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('InputPrice', c_double)  # 期权合约报价
        , ('UnderlyingPrice', c_double)  # 标的价格,填0则用昨结算价
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', HedgeFlag='', InputPrice=0.0, UnderlyingPrice=0.0, ExchangeID='', InvestUnitID=''):
        super(QryOptionInstrTradeCostField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.InputPrice = float(InputPrice)
        self.UnderlyingPrice = float(UnderlyingPrice)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryOptionInstrCommRateField(BaseField):
    """期权手续费率查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryOptionInstrCommRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class IndexPriceField(BaseField):
    """股指现货指数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ClosePrice', c_double)  # 指数现货收盘价
    ]

    def __init__(self, BrokerID='', InstrumentID='', ClosePrice=0.0):
        super(IndexPriceField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ClosePrice = float(ClosePrice)


class InputExecOrderField(BaseField):
    """输入的执行宣告"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Volume', c_int)  # 数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionType', c_char * 1)  # 执行类型
        , ('PosiDirection', c_char * 1)  # 保留头寸申请的持仓方向
        , ('ReservePositionFlag', c_char * 1)  # 期权行权后是否保留期货头寸的标记,该字段已废弃
        , ('CloseFlag', c_char * 1)  # 期权行权后生成的头寸是否自动平仓
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExecOrderRef='', UserID='', Volume=0, RequestID=0, BusinessUnit='', OffsetFlag='', HedgeFlag='', ActionType='', PosiDirection='', ReservePositionFlag='',
                 CloseFlag='', ExchangeID='', InvestUnitID='', AccountID='', CurrencyID='', ClientID='', IPAddress='', MacAddress=''):
        super(InputExecOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.UserID = self._to_bytes(UserID)
        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionType = self._to_bytes(ActionType)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.ReservePositionFlag = self._to_bytes(ReservePositionFlag)
        self.CloseFlag = self._to_bytes(CloseFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class InputExecOrderActionField(BaseField):
    """输入执行宣告操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExecOrderActionRef', c_int)  # 执行宣告操作引用
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', ExecOrderActionRef=0, ExecOrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', ExecOrderSysID='', ActionFlag='', UserID='', InstrumentID='', InvestUnitID='',
                 IPAddress='', MacAddress=''):
        super(InputExecOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExecOrderActionRef = int(ExecOrderActionRef)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExecOrderField(BaseField):
    """执行宣告"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Volume', c_int)  # 数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionType', c_char * 1)  # 执行类型
        , ('PosiDirection', c_char * 1)  # 保留头寸申请的持仓方向
        , ('ReservePositionFlag', c_char * 1)  # 期权行权后是否保留期货头寸的标记,该字段已废弃
        , ('CloseFlag', c_char * 1)  # 期权行权后生成的头寸是否自动平仓
        , ('ExecOrderLocalID', c_char * 13)  # 本地执行宣告编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 执行宣告提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ExecResult', c_char * 1)  # 执行结果
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerExecOrderSeq', c_int)  # 经纪公司报单编号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExecOrderRef='', UserID='', Volume=0, RequestID=0, BusinessUnit='', OffsetFlag='', HedgeFlag='', ActionType='', PosiDirection='', ReservePositionFlag='',
                 CloseFlag='', ExecOrderLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0,
                 ExecOrderSysID='', InsertDate='', InsertTime='', CancelTime='', ExecResult='', ClearingPartID='', SequenceNo=0, FrontID=0, SessionID=0, UserProductInfo='', StatusMsg='', ActiveUserID='',
                 BrokerExecOrderSeq=0, BranchID='', InvestUnitID='', AccountID='', CurrencyID='', IPAddress='', MacAddress=''):
        super(ExecOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.UserID = self._to_bytes(UserID)
        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionType = self._to_bytes(ActionType)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.ReservePositionFlag = self._to_bytes(ReservePositionFlag)
        self.CloseFlag = self._to_bytes(CloseFlag)
        self.ExecOrderLocalID = self._to_bytes(ExecOrderLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ExecResult = self._to_bytes(ExecResult)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerExecOrderSeq = int(BrokerExecOrderSeq)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExecOrderActionField(BaseField):
    """执行宣告操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExecOrderActionRef', c_int)  # 执行宣告操作引用
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ExecOrderLocalID', c_char * 13)  # 本地执行宣告编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('ActionType', c_char * 1)  # 执行类型
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', ExecOrderActionRef=0, ExecOrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', ExecOrderSysID='', ActionFlag='', ActionDate='', ActionTime='', TraderID='',
                 InstallID=0, ExecOrderLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', ActionType='', StatusMsg='', InstrumentID='', BranchID='',
                 InvestUnitID='', IPAddress='', MacAddress=''):
        super(ExecOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExecOrderActionRef = int(ExecOrderActionRef)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ExecOrderLocalID = self._to_bytes(ExecOrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.ActionType = self._to_bytes(ActionType)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryExecOrderField(BaseField):
    """执行宣告查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告编号
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', ExecOrderSysID='', InsertTimeStart='', InsertTimeEnd=''):
        super(QryExecOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)


class ExchangeExecOrderField(BaseField):
    """交易所执行宣告信息"""
    _fields_ = [
        ('Volume', c_int)  # ///数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionType', c_char * 1)  # 执行类型
        , ('PosiDirection', c_char * 1)  # 保留头寸申请的持仓方向
        , ('ReservePositionFlag', c_char * 1)  # 期权行权后是否保留期货头寸的标记,该字段已废弃
        , ('CloseFlag', c_char * 1)  # 期权行权后生成的头寸是否自动平仓
        , ('ExecOrderLocalID', c_char * 13)  # 本地执行宣告编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 执行宣告提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ExecResult', c_char * 1)  # 执行结果
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, Volume=0, RequestID=0, BusinessUnit='', OffsetFlag='', HedgeFlag='', ActionType='', PosiDirection='', ReservePositionFlag='', CloseFlag='', ExecOrderLocalID='', ExchangeID='', ParticipantID='',
                 ClientID='', ExchangeInstID='', TraderID='', InstallID=0, OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, ExecOrderSysID='', InsertDate='', InsertTime='', CancelTime='',
                 ExecResult='', ClearingPartID='', SequenceNo=0, BranchID='', IPAddress='', MacAddress=''):
        super(ExchangeExecOrderField, self).__init__()

        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionType = self._to_bytes(ActionType)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.ReservePositionFlag = self._to_bytes(ReservePositionFlag)
        self.CloseFlag = self._to_bytes(CloseFlag)
        self.ExecOrderLocalID = self._to_bytes(ExecOrderLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ExecResult = self._to_bytes(ExecResult)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryExchangeExecOrderField(BaseField):
    """交易所执行宣告查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeInstID='', ExchangeID='', TraderID=''):
        super(QryExchangeExecOrderField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class QryExecOrderActionField(BaseField):
    """执行宣告操作查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID=''):
        super(QryExecOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ExchangeExecOrderActionField(BaseField):
    """交易所执行宣告操作"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ExecOrderLocalID', c_char * 13)  # 本地执行宣告编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('ActionType', c_char * 1)  # 执行类型
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('Volume', c_int)  # 数量
    ]

    def __init__(self, ExchangeID='', ExecOrderSysID='', ActionFlag='', ActionDate='', ActionTime='', TraderID='', InstallID=0, ExecOrderLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='',
                 OrderActionStatus='', UserID='', ActionType='', BranchID='', IPAddress='', MacAddress='', ExchangeInstID='', Volume=0):
        super(ExchangeExecOrderActionField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ExecOrderLocalID = self._to_bytes(ExecOrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.ActionType = self._to_bytes(ActionType)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.Volume = int(Volume)


class QryExchangeExecOrderActionField(BaseField):
    """交易所执行宣告操作查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeID='', TraderID=''):
        super(QryExchangeExecOrderActionField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class ErrExecOrderField(BaseField):
    """错误执行宣告"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Volume', c_int)  # 数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionType', c_char * 1)  # 执行类型
        , ('PosiDirection', c_char * 1)  # 保留头寸申请的持仓方向
        , ('ReservePositionFlag', c_char * 1)  # 期权行权后是否保留期货头寸的标记,该字段已废弃
        , ('CloseFlag', c_char * 1)  # 期权行权后生成的头寸是否自动平仓
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExecOrderRef='', UserID='', Volume=0, RequestID=0, BusinessUnit='', OffsetFlag='', HedgeFlag='', ActionType='', PosiDirection='', ReservePositionFlag='',
                 CloseFlag='', ExchangeID='', InvestUnitID='', AccountID='', CurrencyID='', ClientID='', IPAddress='', MacAddress='', ErrorID=0, ErrorMsg=''):
        super(ErrExecOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.UserID = self._to_bytes(UserID)
        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionType = self._to_bytes(ActionType)
        self.PosiDirection = self._to_bytes(PosiDirection)
        self.ReservePositionFlag = self._to_bytes(ReservePositionFlag)
        self.CloseFlag = self._to_bytes(CloseFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class QryErrExecOrderField(BaseField):
    """查询错误执行宣告"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryErrExecOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class ErrExecOrderActionField(BaseField):
    """错误执行宣告操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExecOrderActionRef', c_int)  # 执行宣告操作引用
        , ('ExecOrderRef', c_char * 13)  # 执行宣告引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExecOrderSysID', c_char * 21)  # 执行宣告操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, BrokerID='', InvestorID='', ExecOrderActionRef=0, ExecOrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', ExecOrderSysID='', ActionFlag='', UserID='', InstrumentID='', InvestUnitID='',
                 IPAddress='', MacAddress='', ErrorID=0, ErrorMsg=''):
        super(ErrExecOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExecOrderActionRef = int(ExecOrderActionRef)
        self.ExecOrderRef = self._to_bytes(ExecOrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExecOrderSysID = self._to_bytes(ExecOrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class QryErrExecOrderActionField(BaseField):
    """查询错误执行宣告操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryErrExecOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class OptionInstrTradingRightField(BaseField):
    """投资者期权合约交易权限"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('TradingRight', c_char * 1)  # 交易权限
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', Direction='', TradingRight=''):
        super(OptionInstrTradingRightField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Direction = self._to_bytes(Direction)
        self.TradingRight = self._to_bytes(TradingRight)


class QryOptionInstrTradingRightField(BaseField):
    """查询期权合约交易权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('Direction', c_char * 1)  # 买卖方向
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', Direction=''):
        super(QryOptionInstrTradingRightField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.Direction = self._to_bytes(Direction)


class InputForQuoteField(BaseField):
    """输入的询价"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ForQuoteRef', c_char * 13)  # 询价引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ForQuoteRef='', UserID='', ExchangeID='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(InputForQuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ForQuoteRef = self._to_bytes(ForQuoteRef)
        self.UserID = self._to_bytes(UserID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ForQuoteField(BaseField):
    """询价"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ForQuoteRef', c_char * 13)  # 询价引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('ForQuoteLocalID', c_char * 13)  # 本地询价编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('ForQuoteStatus', c_char * 1)  # 询价状态
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerForQutoSeq', c_int)  # 经纪公司询价编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ForQuoteRef='', UserID='', ForQuoteLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, InsertDate='',
                 InsertTime='', ForQuoteStatus='', FrontID=0, SessionID=0, StatusMsg='', ActiveUserID='', BrokerForQutoSeq=0, InvestUnitID='', IPAddress='', MacAddress=''):
        super(ForQuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ForQuoteRef = self._to_bytes(ForQuoteRef)
        self.UserID = self._to_bytes(UserID)
        self.ForQuoteLocalID = self._to_bytes(ForQuoteLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.ForQuoteStatus = self._to_bytes(ForQuoteStatus)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerForQutoSeq = int(BrokerForQutoSeq)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryForQuoteField(BaseField):
    """询价查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InsertTimeStart='', InsertTimeEnd='', InvestUnitID=''):
        super(QryForQuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class ExchangeForQuoteField(BaseField):
    """交易所询价信息"""
    _fields_ = [
        ('ForQuoteLocalID', c_char * 13)  # ///本地询价编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('ForQuoteStatus', c_char * 1)  # 询价状态
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, ForQuoteLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, InsertDate='', InsertTime='', ForQuoteStatus='', IPAddress='', MacAddress=''):
        super(ExchangeForQuoteField, self).__init__()

        self.ForQuoteLocalID = self._to_bytes(ForQuoteLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.ForQuoteStatus = self._to_bytes(ForQuoteStatus)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryExchangeForQuoteField(BaseField):
    """交易所询价查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeInstID='', ExchangeID='', TraderID=''):
        super(QryExchangeForQuoteField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class InputQuoteField(BaseField):
    """输入的报价"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('QuoteRef', c_char * 13)  # 报价引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('AskPrice', c_double)  # 卖价格
        , ('BidPrice', c_double)  # 买价格
        , ('AskVolume', c_int)  # 卖数量
        , ('BidVolume', c_int)  # 买数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('AskOffsetFlag', c_char * 1)  # 卖开平标志
        , ('BidOffsetFlag', c_char * 1)  # 买开平标志
        , ('AskHedgeFlag', c_char * 1)  # 卖投机套保标志
        , ('BidHedgeFlag', c_char * 1)  # 买投机套保标志
        , ('AskOrderRef', c_char * 13)  # 衍生卖报单引用
        , ('BidOrderRef', c_char * 13)  # 衍生买报单引用
        , ('ForQuoteSysID', c_char * 21)  # 应价编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', QuoteRef='', UserID='', AskPrice=0.0, BidPrice=0.0, AskVolume=0, BidVolume=0, RequestID=0, BusinessUnit='', AskOffsetFlag='', BidOffsetFlag='',
                 AskHedgeFlag='', BidHedgeFlag='', AskOrderRef='', BidOrderRef='', ForQuoteSysID='', ExchangeID='', InvestUnitID='', ClientID='', IPAddress='', MacAddress=''):
        super(InputQuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.QuoteRef = self._to_bytes(QuoteRef)
        self.UserID = self._to_bytes(UserID)
        self.AskPrice = float(AskPrice)
        self.BidPrice = float(BidPrice)
        self.AskVolume = int(AskVolume)
        self.BidVolume = int(BidVolume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.AskOffsetFlag = self._to_bytes(AskOffsetFlag)
        self.BidOffsetFlag = self._to_bytes(BidOffsetFlag)
        self.AskHedgeFlag = self._to_bytes(AskHedgeFlag)
        self.BidHedgeFlag = self._to_bytes(BidHedgeFlag)
        self.AskOrderRef = self._to_bytes(AskOrderRef)
        self.BidOrderRef = self._to_bytes(BidOrderRef)
        self.ForQuoteSysID = self._to_bytes(ForQuoteSysID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class InputQuoteActionField(BaseField):
    """输入报价操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('QuoteActionRef', c_int)  # 报价操作引用
        , ('QuoteRef', c_char * 13)  # 报价引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('QuoteSysID', c_char * 21)  # 报价操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', QuoteActionRef=0, QuoteRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', QuoteSysID='', ActionFlag='', UserID='', InstrumentID='', InvestUnitID='', ClientID='',
                 IPAddress='', MacAddress=''):
        super(InputQuoteActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.QuoteActionRef = int(QuoteActionRef)
        self.QuoteRef = self._to_bytes(QuoteRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QuoteField(BaseField):
    """报价"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('QuoteRef', c_char * 13)  # 报价引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('AskPrice', c_double)  # 卖价格
        , ('BidPrice', c_double)  # 买价格
        , ('AskVolume', c_int)  # 卖数量
        , ('BidVolume', c_int)  # 买数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('AskOffsetFlag', c_char * 1)  # 卖开平标志
        , ('BidOffsetFlag', c_char * 1)  # 买开平标志
        , ('AskHedgeFlag', c_char * 1)  # 卖投机套保标志
        , ('BidHedgeFlag', c_char * 1)  # 买投机套保标志
        , ('QuoteLocalID', c_char * 13)  # 本地报价编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('NotifySequence', c_int)  # 报价提示序号
        , ('OrderSubmitStatus', c_char * 1)  # 报价提交状态
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('QuoteSysID', c_char * 21)  # 报价编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('QuoteStatus', c_char * 1)  # 报价状态
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('AskOrderSysID', c_char * 21)  # 卖方报单编号
        , ('BidOrderSysID', c_char * 21)  # 买方报单编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerQuoteSeq', c_int)  # 经纪公司报价编号
        , ('AskOrderRef', c_char * 13)  # 衍生卖报单引用
        , ('BidOrderRef', c_char * 13)  # 衍生买报单引用
        , ('ForQuoteSysID', c_char * 21)  # 应价编号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', QuoteRef='', UserID='', AskPrice=0.0, BidPrice=0.0, AskVolume=0, BidVolume=0, RequestID=0, BusinessUnit='', AskOffsetFlag='', BidOffsetFlag='',
                 AskHedgeFlag='', BidHedgeFlag='', QuoteLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, NotifySequence=0, OrderSubmitStatus='', TradingDay='',
                 SettlementID=0, QuoteSysID='', InsertDate='', InsertTime='', CancelTime='', QuoteStatus='', ClearingPartID='', SequenceNo=0, AskOrderSysID='', BidOrderSysID='', FrontID=0, SessionID=0, UserProductInfo='',
                 StatusMsg='', ActiveUserID='', BrokerQuoteSeq=0, AskOrderRef='', BidOrderRef='', ForQuoteSysID='', BranchID='', InvestUnitID='', AccountID='', CurrencyID='', IPAddress='', MacAddress=''):
        super(QuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.QuoteRef = self._to_bytes(QuoteRef)
        self.UserID = self._to_bytes(UserID)
        self.AskPrice = float(AskPrice)
        self.BidPrice = float(BidPrice)
        self.AskVolume = int(AskVolume)
        self.BidVolume = int(BidVolume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.AskOffsetFlag = self._to_bytes(AskOffsetFlag)
        self.BidOffsetFlag = self._to_bytes(BidOffsetFlag)
        self.AskHedgeFlag = self._to_bytes(AskHedgeFlag)
        self.BidHedgeFlag = self._to_bytes(BidHedgeFlag)
        self.QuoteLocalID = self._to_bytes(QuoteLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.NotifySequence = int(NotifySequence)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.QuoteStatus = self._to_bytes(QuoteStatus)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.AskOrderSysID = self._to_bytes(AskOrderSysID)
        self.BidOrderSysID = self._to_bytes(BidOrderSysID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerQuoteSeq = int(BrokerQuoteSeq)
        self.AskOrderRef = self._to_bytes(AskOrderRef)
        self.BidOrderRef = self._to_bytes(BidOrderRef)
        self.ForQuoteSysID = self._to_bytes(ForQuoteSysID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QuoteActionField(BaseField):
    """报价操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('QuoteActionRef', c_int)  # 报价操作引用
        , ('QuoteRef', c_char * 13)  # 报价引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('QuoteSysID', c_char * 21)  # 报价操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('QuoteLocalID', c_char * 13)  # 本地报价编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', QuoteActionRef=0, QuoteRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', QuoteSysID='', ActionFlag='', ActionDate='', ActionTime='', TraderID='', InstallID=0,
                 QuoteLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', StatusMsg='', InstrumentID='', BranchID='', InvestUnitID='', IPAddress='',
                 MacAddress=''):
        super(QuoteActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.QuoteActionRef = int(QuoteActionRef)
        self.QuoteRef = self._to_bytes(QuoteRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.QuoteLocalID = self._to_bytes(QuoteLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryQuoteField(BaseField):
    """报价查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('QuoteSysID', c_char * 21)  # 报价编号
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', QuoteSysID='', InsertTimeStart='', InsertTimeEnd='', InvestUnitID=''):
        super(QryQuoteField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class ExchangeQuoteField(BaseField):
    """交易所报价信息"""
    _fields_ = [
        ('AskPrice', c_double)  # ///卖价格
        , ('BidPrice', c_double)  # 买价格
        , ('AskVolume', c_int)  # 卖数量
        , ('BidVolume', c_int)  # 买数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('AskOffsetFlag', c_char * 1)  # 卖开平标志
        , ('BidOffsetFlag', c_char * 1)  # 买开平标志
        , ('AskHedgeFlag', c_char * 1)  # 卖投机套保标志
        , ('BidHedgeFlag', c_char * 1)  # 买投机套保标志
        , ('QuoteLocalID', c_char * 13)  # 本地报价编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('NotifySequence', c_int)  # 报价提示序号
        , ('OrderSubmitStatus', c_char * 1)  # 报价提交状态
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('QuoteSysID', c_char * 21)  # 报价编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('QuoteStatus', c_char * 1)  # 报价状态
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('AskOrderSysID', c_char * 21)  # 卖方报单编号
        , ('BidOrderSysID', c_char * 21)  # 买方报单编号
        , ('ForQuoteSysID', c_char * 21)  # 应价编号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, AskPrice=0.0, BidPrice=0.0, AskVolume=0, BidVolume=0, RequestID=0, BusinessUnit='', AskOffsetFlag='', BidOffsetFlag='', AskHedgeFlag='', BidHedgeFlag='', QuoteLocalID='', ExchangeID='',
                 ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, NotifySequence=0, OrderSubmitStatus='', TradingDay='', SettlementID=0, QuoteSysID='', InsertDate='', InsertTime='',
                 CancelTime='', QuoteStatus='', ClearingPartID='', SequenceNo=0, AskOrderSysID='', BidOrderSysID='', ForQuoteSysID='', BranchID='', IPAddress='', MacAddress=''):
        super(ExchangeQuoteField, self).__init__()

        self.AskPrice = float(AskPrice)
        self.BidPrice = float(BidPrice)
        self.AskVolume = int(AskVolume)
        self.BidVolume = int(BidVolume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.AskOffsetFlag = self._to_bytes(AskOffsetFlag)
        self.BidOffsetFlag = self._to_bytes(BidOffsetFlag)
        self.AskHedgeFlag = self._to_bytes(AskHedgeFlag)
        self.BidHedgeFlag = self._to_bytes(BidHedgeFlag)
        self.QuoteLocalID = self._to_bytes(QuoteLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.NotifySequence = int(NotifySequence)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.QuoteStatus = self._to_bytes(QuoteStatus)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.AskOrderSysID = self._to_bytes(AskOrderSysID)
        self.BidOrderSysID = self._to_bytes(BidOrderSysID)
        self.ForQuoteSysID = self._to_bytes(ForQuoteSysID)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryExchangeQuoteField(BaseField):
    """交易所报价查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeInstID='', ExchangeID='', TraderID=''):
        super(QryExchangeQuoteField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class QryQuoteActionField(BaseField):
    """报价操作查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID=''):
        super(QryQuoteActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ExchangeQuoteActionField(BaseField):
    """交易所报价操作"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('QuoteSysID', c_char * 21)  # 报价操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('QuoteLocalID', c_char * 13)  # 本地报价编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, ExchangeID='', QuoteSysID='', ActionFlag='', ActionDate='', ActionTime='', TraderID='', InstallID=0, QuoteLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='',
                 OrderActionStatus='', UserID='', IPAddress='', MacAddress=''):
        super(ExchangeQuoteActionField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.QuoteSysID = self._to_bytes(QuoteSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.QuoteLocalID = self._to_bytes(QuoteLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryExchangeQuoteActionField(BaseField):
    """交易所报价操作查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeID='', TraderID=''):
        super(QryExchangeQuoteActionField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class OptionInstrDeltaField(BaseField):
    """期权合约delta值"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Delta', c_double)  # Delta值
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', Delta=0.0):
        super(OptionInstrDeltaField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Delta = float(Delta)


class ForQuoteRspField(BaseField):
    """发给做市商的询价请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ForQuoteSysID', c_char * 21)  # 询价编号
        , ('ForQuoteTime', c_char * 9)  # 询价时间
        , ('ActionDay', c_char * 9)  # 业务日期
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, TradingDay='', InstrumentID='', ForQuoteSysID='', ForQuoteTime='', ActionDay='', ExchangeID=''):
        super(ForQuoteRspField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ForQuoteSysID = self._to_bytes(ForQuoteSysID)
        self.ForQuoteTime = self._to_bytes(ForQuoteTime)
        self.ActionDay = self._to_bytes(ActionDay)
        self.ExchangeID = self._to_bytes(ExchangeID)


class StrikeOffsetField(BaseField):
    """当前期权合约执行偏移值的详细内容"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Offset', c_double)  # 执行偏移值
        , ('OffsetType', c_char * 1)  # 执行偏移类型
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', Offset=0.0, OffsetType=''):
        super(StrikeOffsetField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Offset = float(Offset)
        self.OffsetType = self._to_bytes(OffsetType)


class QryStrikeOffsetField(BaseField):
    """期权执行偏移值查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID=''):
        super(QryStrikeOffsetField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class InputBatchOrderActionField(BaseField):
    """输入批量报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, RequestID=0, FrontID=0, SessionID=0, ExchangeID='', UserID='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(InputBatchOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.UserID = self._to_bytes(UserID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class BatchOrderActionField(BaseField):
    """批量报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, RequestID=0, FrontID=0, SessionID=0, ExchangeID='', ActionDate='', ActionTime='', TraderID='', InstallID=0, ActionLocalID='', ParticipantID='',
                 ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', StatusMsg='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(BatchOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ExchangeBatchOrderActionField(BaseField):
    """交易所批量报单操作"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, ExchangeID='', ActionDate='', ActionTime='', TraderID='', InstallID=0, ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', IPAddress='', MacAddress=''):
        super(ExchangeBatchOrderActionField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryBatchOrderActionField(BaseField):
    """查询批量报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID=''):
        super(QryBatchOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class CombInstrumentGuardField(BaseField):
    """组合合约安全系数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('GuarantRatio', c_double)  # ,('ExchangeID',c_char*9)# 交易所代码
    ]

    def __init__(self, BrokerID='', InstrumentID='', GuarantRatio=0.0, ExchangeID=''):
        super(CombInstrumentGuardField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.GuarantRatio = float(GuarantRatio)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryCombInstrumentGuardField(BaseField):
    """组合合约安全系数查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InstrumentID='', ExchangeID=''):
        super(QryCombInstrumentGuardField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class InputCombActionField(BaseField):
    """输入的申请组合"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('CombActionRef', c_char * 13)  # 组合引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('Volume', c_int)  # 数量
        , ('CombDirection', c_char * 1)  # 组合指令方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', CombActionRef='', UserID='', Direction='', Volume=0, CombDirection='', HedgeFlag='', ExchangeID='', IPAddress='', MacAddress='', InvestUnitID=''):
        super(InputCombActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.CombActionRef = self._to_bytes(CombActionRef)
        self.UserID = self._to_bytes(UserID)
        self.Direction = self._to_bytes(Direction)
        self.Volume = int(Volume)
        self.CombDirection = self._to_bytes(CombDirection)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class CombActionField(BaseField):
    """申请组合"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('CombActionRef', c_char * 13)  # 组合引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('Volume', c_int)  # 数量
        , ('CombDirection', c_char * 1)  # 组合指令方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionLocalID', c_char * 13)  # 本地申请组合编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ActionStatus', c_char * 1)  # 组合状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('SequenceNo', c_int)  # 序号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ComTradeID', c_char * 21)  # 组合编号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', CombActionRef='', UserID='', Direction='', Volume=0, CombDirection='', HedgeFlag='', ActionLocalID='', ExchangeID='', ParticipantID='', ClientID='',
                 ExchangeInstID='', TraderID='', InstallID=0, ActionStatus='', NotifySequence=0, TradingDay='', SettlementID=0, SequenceNo=0, FrontID=0, SessionID=0, UserProductInfo='', StatusMsg='', IPAddress='',
                 MacAddress='', ComTradeID='', BranchID='', InvestUnitID=''):
        super(CombActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.CombActionRef = self._to_bytes(CombActionRef)
        self.UserID = self._to_bytes(UserID)
        self.Direction = self._to_bytes(Direction)
        self.Volume = int(Volume)
        self.CombDirection = self._to_bytes(CombDirection)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ActionStatus = self._to_bytes(ActionStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.SequenceNo = int(SequenceNo)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ComTradeID = self._to_bytes(ComTradeID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryCombActionField(BaseField):
    """申请组合查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryCombActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class ExchangeCombActionField(BaseField):
    """交易所申请组合信息"""
    _fields_ = [
        ('Direction', c_char * 1)  # ///买卖方向
        , ('Volume', c_int)  # 数量
        , ('CombDirection', c_char * 1)  # 组合指令方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ActionLocalID', c_char * 13)  # 本地申请组合编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('ActionStatus', c_char * 1)  # 组合状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('SequenceNo', c_int)  # 序号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ComTradeID', c_char * 21)  # 组合编号
        , ('BranchID', c_char * 9)  # 营业部编号
    ]

    def __init__(self, Direction='', Volume=0, CombDirection='', HedgeFlag='', ActionLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, ActionStatus='', NotifySequence=0,
                 TradingDay='', SettlementID=0, SequenceNo=0, IPAddress='', MacAddress='', ComTradeID='', BranchID=''):
        super(ExchangeCombActionField, self).__init__()

        self.Direction = self._to_bytes(Direction)
        self.Volume = int(Volume)
        self.CombDirection = self._to_bytes(CombDirection)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.ActionStatus = self._to_bytes(ActionStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.SequenceNo = int(SequenceNo)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ComTradeID = self._to_bytes(ComTradeID)
        self.BranchID = self._to_bytes(BranchID)


class QryExchangeCombActionField(BaseField):
    """交易所申请组合查询"""
    _fields_ = [
        ('ParticipantID', c_char * 11)  # ///会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ParticipantID='', ClientID='', ExchangeInstID='', ExchangeID='', TraderID=''):
        super(QryExchangeCombActionField, self).__init__()

        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)


class ProductExchRateField(BaseField):
    """产品报价汇率"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('QuoteCurrencyID', c_char * 4)  # 报价币种类型
        , ('ExchangeRate', c_double)  # 汇率
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, ProductID='', QuoteCurrencyID='', ExchangeRate=0.0, ExchangeID=''):
        super(ProductExchRateField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.QuoteCurrencyID = self._to_bytes(QuoteCurrencyID)
        self.ExchangeRate = float(ExchangeRate)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryProductExchRateField(BaseField):
    """产品报价汇率查询"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, ProductID='', ExchangeID=''):
        super(QryProductExchRateField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class QryForQuoteParamField(BaseField):
    """查询询价价差参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InstrumentID='', ExchangeID=''):
        super(QryForQuoteParamField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ForQuoteParamField(BaseField):
    """询价价差参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('LastPrice', c_double)  # 最新价
        , ('PriceInterval', c_double)  # 价差
    ]

    def __init__(self, BrokerID='', InstrumentID='', ExchangeID='', LastPrice=0.0, PriceInterval=0.0):
        super(ForQuoteParamField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.LastPrice = float(LastPrice)
        self.PriceInterval = float(PriceInterval)


class MMOptionInstrCommRateField(BaseField):
    """当前做市商期权合约手续费的详细内容"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OpenRatioByMoney', c_double)  # 开仓手续费率
        , ('OpenRatioByVolume', c_double)  # 开仓手续费
        , ('CloseRatioByMoney', c_double)  # 平仓手续费率
        , ('CloseRatioByVolume', c_double)  # 平仓手续费
        , ('CloseTodayRatioByMoney', c_double)  # 平今手续费率
        , ('CloseTodayRatioByVolume', c_double)  # 平今手续费
        , ('StrikeRatioByMoney', c_double)  # 执行手续费率
        , ('StrikeRatioByVolume', c_double)  # 执行手续费
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', OpenRatioByMoney=0.0, OpenRatioByVolume=0.0, CloseRatioByMoney=0.0, CloseRatioByVolume=0.0, CloseTodayRatioByMoney=0.0,
                 CloseTodayRatioByVolume=0.0, StrikeRatioByMoney=0.0, StrikeRatioByVolume=0.0):
        super(MMOptionInstrCommRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OpenRatioByMoney = float(OpenRatioByMoney)
        self.OpenRatioByVolume = float(OpenRatioByVolume)
        self.CloseRatioByMoney = float(CloseRatioByMoney)
        self.CloseRatioByVolume = float(CloseRatioByVolume)
        self.CloseTodayRatioByMoney = float(CloseTodayRatioByMoney)
        self.CloseTodayRatioByVolume = float(CloseTodayRatioByVolume)
        self.StrikeRatioByMoney = float(StrikeRatioByMoney)
        self.StrikeRatioByVolume = float(StrikeRatioByVolume)


class QryMMOptionInstrCommRateField(BaseField):
    """做市商期权手续费率查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID=''):
        super(QryMMOptionInstrCommRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class MMInstrumentCommissionRateField(BaseField):
    """做市商合约手续费率"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OpenRatioByMoney', c_double)  # 开仓手续费率
        , ('OpenRatioByVolume', c_double)  # 开仓手续费
        , ('CloseRatioByMoney', c_double)  # 平仓手续费率
        , ('CloseRatioByVolume', c_double)  # 平仓手续费
        , ('CloseTodayRatioByMoney', c_double)  # 平今手续费率
        , ('CloseTodayRatioByVolume', c_double)  # 平今手续费
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', OpenRatioByMoney=0.0, OpenRatioByVolume=0.0, CloseRatioByMoney=0.0, CloseRatioByVolume=0.0, CloseTodayRatioByMoney=0.0,
                 CloseTodayRatioByVolume=0.0):
        super(MMInstrumentCommissionRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OpenRatioByMoney = float(OpenRatioByMoney)
        self.OpenRatioByVolume = float(OpenRatioByVolume)
        self.CloseRatioByMoney = float(CloseRatioByMoney)
        self.CloseRatioByVolume = float(CloseRatioByVolume)
        self.CloseTodayRatioByMoney = float(CloseTodayRatioByMoney)
        self.CloseTodayRatioByVolume = float(CloseTodayRatioByVolume)


class QryMMInstrumentCommissionRateField(BaseField):
    """查询做市商合约手续费率"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID=''):
        super(QryMMInstrumentCommissionRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class InstrumentOrderCommRateField(BaseField):
    """当前报单手续费的详细内容"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('OrderCommByVolume', c_double)  # 报单手续费
        , ('OrderActionCommByVolume', c_double)  # 撤单手续费
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', HedgeFlag='', OrderCommByVolume=0.0, OrderActionCommByVolume=0.0, ExchangeID='', InvestUnitID=''):
        super(InstrumentOrderCommRateField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.OrderCommByVolume = float(OrderCommByVolume)
        self.OrderActionCommByVolume = float(OrderActionCommByVolume)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInstrumentOrderCommRateField(BaseField):
    """报单手续费率查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID=''):
        super(QryInstrumentOrderCommRateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class TradeParamField(BaseField):
    """交易参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('TradeParamID', c_char * 1)  # 参数代码
        , ('TradeParamValue', c_char * 256)  # 参数代码值
        , ('Memo', c_char * 161)  # 备注
    ]

    def __init__(self, BrokerID='', TradeParamID='', TradeParamValue='', Memo=''):
        super(TradeParamField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.TradeParamID = self._to_bytes(TradeParamID)
        self.TradeParamValue = self._to_bytes(TradeParamValue)
        self.Memo = self._to_bytes(Memo)


class InstrumentMarginRateULField(BaseField):
    """合约保证金率调整"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('LongMarginRatioByMoney', c_double)  # 多头保证金率
        , ('LongMarginRatioByVolume', c_double)  # 多头保证金费
        , ('ShortMarginRatioByMoney', c_double)  # 空头保证金率
        , ('ShortMarginRatioByVolume', c_double)  # 空头保证金费
    ]

    def __init__(self, InstrumentID='', InvestorRange='', BrokerID='', InvestorID='', HedgeFlag='', LongMarginRatioByMoney=0.0, LongMarginRatioByVolume=0.0, ShortMarginRatioByMoney=0.0, ShortMarginRatioByVolume=0.0):
        super(InstrumentMarginRateULField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.LongMarginRatioByMoney = float(LongMarginRatioByMoney)
        self.LongMarginRatioByVolume = float(LongMarginRatioByVolume)
        self.ShortMarginRatioByMoney = float(ShortMarginRatioByMoney)
        self.ShortMarginRatioByVolume = float(ShortMarginRatioByVolume)


class FutureLimitPosiParamField(BaseField):
    """期货持仓限制参数"""
    _fields_ = [
        ('InvestorRange', c_char * 1)  # ///投资者范围
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ProductID', c_char * 31)  # 产品代码
        , ('SpecOpenVolume', c_int)  # 当日投机开仓数量限制
        , ('ArbiOpenVolume', c_int)  # 当日套利开仓数量限制
        , ('OpenVolume', c_int)  # 当日投机+套利开仓数量限制
    ]

    def __init__(self, InvestorRange='', BrokerID='', InvestorID='', ProductID='', SpecOpenVolume=0, ArbiOpenVolume=0, OpenVolume=0):
        super(FutureLimitPosiParamField, self).__init__()

        self.InvestorRange = self._to_bytes(InvestorRange)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ProductID = self._to_bytes(ProductID)
        self.SpecOpenVolume = int(SpecOpenVolume)
        self.ArbiOpenVolume = int(ArbiOpenVolume)
        self.OpenVolume = int(OpenVolume)


class LoginForbiddenIPField(BaseField):
    """禁止登录IP"""
    _fields_ = [
        ('IPAddress', c_char * 16)  # ///IP地址
    ]

    def __init__(self, IPAddress=''):
        super(LoginForbiddenIPField, self).__init__()

        self.IPAddress = self._to_bytes(IPAddress)


class IPListField(BaseField):
    """IP列表"""
    _fields_ = [
        ('IPAddress', c_char * 16)  # ///IP地址
        , ('IsWhite', c_int)  # 是否白名单
    ]

    def __init__(self, IPAddress='', IsWhite=0):
        super(IPListField, self).__init__()

        self.IPAddress = self._to_bytes(IPAddress)
        self.IsWhite = int(IsWhite)


class InputOptionSelfCloseField(BaseField):
    """输入的期权自对冲"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OptionSelfCloseRef', c_char * 13)  # 期权自对冲引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Volume', c_int)  # 数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('OptSelfCloseFlag', c_char * 1)  # 期权行权的头寸是否自对冲
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OptionSelfCloseRef='', UserID='', Volume=0, RequestID=0, BusinessUnit='', HedgeFlag='', OptSelfCloseFlag='', ExchangeID='', InvestUnitID='', AccountID='',
                 CurrencyID='', ClientID='', IPAddress='', MacAddress=''):
        super(InputOptionSelfCloseField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OptionSelfCloseRef = self._to_bytes(OptionSelfCloseRef)
        self.UserID = self._to_bytes(UserID)
        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.OptSelfCloseFlag = self._to_bytes(OptSelfCloseFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class InputOptionSelfCloseActionField(BaseField):
    """输入期权自对冲操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OptionSelfCloseActionRef', c_int)  # 期权自对冲操作引用
        , ('OptionSelfCloseRef', c_char * 13)  # 期权自对冲引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OptionSelfCloseActionRef=0, OptionSelfCloseRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OptionSelfCloseSysID='', ActionFlag='', UserID='', InstrumentID='',
                 InvestUnitID='', IPAddress='', MacAddress=''):
        super(InputOptionSelfCloseActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OptionSelfCloseActionRef = int(OptionSelfCloseActionRef)
        self.OptionSelfCloseRef = self._to_bytes(OptionSelfCloseRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class OptionSelfCloseField(BaseField):
    """期权自对冲"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OptionSelfCloseRef', c_char * 13)  # 期权自对冲引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('Volume', c_int)  # 数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('OptSelfCloseFlag', c_char * 1)  # 期权行权的头寸是否自对冲
        , ('OptionSelfCloseLocalID', c_char * 13)  # 本地期权自对冲编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 期权自对冲提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ExecResult', c_char * 1)  # 自对冲结果
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerOptionSelfCloseSeq', c_int)  # 经纪公司报单编号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OptionSelfCloseRef='', UserID='', Volume=0, RequestID=0, BusinessUnit='', HedgeFlag='', OptSelfCloseFlag='', OptionSelfCloseLocalID='', ExchangeID='',
                 ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0, OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, OptionSelfCloseSysID='', InsertDate='', InsertTime='',
                 CancelTime='', ExecResult='', ClearingPartID='', SequenceNo=0, FrontID=0, SessionID=0, UserProductInfo='', StatusMsg='', ActiveUserID='', BrokerOptionSelfCloseSeq=0, BranchID='', InvestUnitID='',
                 AccountID='', CurrencyID='', IPAddress='', MacAddress=''):
        super(OptionSelfCloseField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OptionSelfCloseRef = self._to_bytes(OptionSelfCloseRef)
        self.UserID = self._to_bytes(UserID)
        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.OptSelfCloseFlag = self._to_bytes(OptSelfCloseFlag)
        self.OptionSelfCloseLocalID = self._to_bytes(OptionSelfCloseLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ExecResult = self._to_bytes(ExecResult)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerOptionSelfCloseSeq = int(BrokerOptionSelfCloseSeq)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class OptionSelfCloseActionField(BaseField):
    """期权自对冲操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OptionSelfCloseActionRef', c_int)  # 期权自对冲操作引用
        , ('OptionSelfCloseRef', c_char * 13)  # 期权自对冲引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OptionSelfCloseLocalID', c_char * 13)  # 本地期权自对冲编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OptionSelfCloseActionRef=0, OptionSelfCloseRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OptionSelfCloseSysID='', ActionFlag='', ActionDate='',
                 ActionTime='', TraderID='', InstallID=0, OptionSelfCloseLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', StatusMsg='', InstrumentID='',
                 BranchID='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(OptionSelfCloseActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OptionSelfCloseActionRef = int(OptionSelfCloseActionRef)
        self.OptionSelfCloseRef = self._to_bytes(OptionSelfCloseRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OptionSelfCloseLocalID = self._to_bytes(OptionSelfCloseLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryOptionSelfCloseField(BaseField):
    """期权自对冲查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲编号
        , ('InsertTimeStart', c_char * 9)  # 开始时间
        , ('InsertTimeEnd', c_char * 9)  # 结束时间
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', OptionSelfCloseSysID='', InsertTimeStart='', InsertTimeEnd=''):
        super(QryOptionSelfCloseField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.InsertTimeStart = self._to_bytes(InsertTimeStart)
        self.InsertTimeEnd = self._to_bytes(InsertTimeEnd)


class ExchangeOptionSelfCloseField(BaseField):
    """交易所期权自对冲信息"""
    _fields_ = [
        ('Volume', c_int)  # ///数量
        , ('RequestID', c_int)  # 请求编号
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('OptSelfCloseFlag', c_char * 1)  # 期权行权的头寸是否自对冲
        , ('OptionSelfCloseLocalID', c_char * 13)  # 本地期权自对冲编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 期权自对冲提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲编号
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 插入时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ExecResult', c_char * 1)  # 自对冲结果
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, Volume=0, RequestID=0, BusinessUnit='', HedgeFlag='', OptSelfCloseFlag='', OptionSelfCloseLocalID='', ExchangeID='', ParticipantID='', ClientID='', ExchangeInstID='', TraderID='', InstallID=0,
                 OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, OptionSelfCloseSysID='', InsertDate='', InsertTime='', CancelTime='', ExecResult='', ClearingPartID='', SequenceNo=0, BranchID='',
                 IPAddress='', MacAddress=''):
        super(ExchangeOptionSelfCloseField, self).__init__()

        self.Volume = int(Volume)
        self.RequestID = int(RequestID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.OptSelfCloseFlag = self._to_bytes(OptSelfCloseFlag)
        self.OptionSelfCloseLocalID = self._to_bytes(OptionSelfCloseLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ExecResult = self._to_bytes(ExecResult)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryOptionSelfCloseActionField(BaseField):
    """期权自对冲操作查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID=''):
        super(QryOptionSelfCloseActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ExchangeOptionSelfCloseActionField(BaseField):
    """交易所期权自对冲操作"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('OptionSelfCloseSysID', c_char * 21)  # 期权自对冲操作编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OptionSelfCloseLocalID', c_char * 13)  # 本地期权自对冲编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('OptSelfCloseFlag', c_char * 1)  # 期权行权的头寸是否自对冲
    ]

    def __init__(self, ExchangeID='', OptionSelfCloseSysID='', ActionFlag='', ActionDate='', ActionTime='', TraderID='', InstallID=0, OptionSelfCloseLocalID='', ActionLocalID='', ParticipantID='', ClientID='',
                 BusinessUnit='', OrderActionStatus='', UserID='', BranchID='', IPAddress='', MacAddress='', ExchangeInstID='', OptSelfCloseFlag=''):
        super(ExchangeOptionSelfCloseActionField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OptionSelfCloseSysID = self._to_bytes(OptionSelfCloseSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OptionSelfCloseLocalID = self._to_bytes(OptionSelfCloseLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.BranchID = self._to_bytes(BranchID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.OptSelfCloseFlag = self._to_bytes(OptSelfCloseFlag)


class SyncDelaySwapField(BaseField):
    """延时换汇同步"""
    _fields_ = [
        ('DelaySwapSeqNo', c_char * 15)  # ///换汇流水号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('FromCurrencyID', c_char * 4)  # 源币种
        , ('FromAmount', c_double)  # 源金额
        , ('FromFrozenSwap', c_double)  # 源换汇冻结金额(可用冻结)
        , ('FromRemainSwap', c_double)  # 源剩余换汇额度(可提冻结)
        , ('ToCurrencyID', c_char * 4)  # 目标币种
        , ('ToAmount', c_double)  # 目标金额
    ]

    def __init__(self, DelaySwapSeqNo='', BrokerID='', InvestorID='', FromCurrencyID='', FromAmount=0.0, FromFrozenSwap=0.0, FromRemainSwap=0.0, ToCurrencyID='', ToAmount=0.0):
        super(SyncDelaySwapField, self).__init__()

        self.DelaySwapSeqNo = self._to_bytes(DelaySwapSeqNo)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.FromCurrencyID = self._to_bytes(FromCurrencyID)
        self.FromAmount = float(FromAmount)
        self.FromFrozenSwap = float(FromFrozenSwap)
        self.FromRemainSwap = float(FromRemainSwap)
        self.ToCurrencyID = self._to_bytes(ToCurrencyID)
        self.ToAmount = float(ToAmount)


class QrySyncDelaySwapField(BaseField):
    """查询延时换汇同步"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('DelaySwapSeqNo', c_char * 15)  # 延时换汇流水号
    ]

    def __init__(self, BrokerID='', DelaySwapSeqNo=''):
        super(QrySyncDelaySwapField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.DelaySwapSeqNo = self._to_bytes(DelaySwapSeqNo)


class InvestUnitField(BaseField):
    """投资单元"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('InvestorUnitName', c_char * 81)  # 投资者单元名称
        , ('InvestorGroupID', c_char * 13)  # 投资者分组代码
        , ('CommModelID', c_char * 13)  # 手续费率模板代码
        , ('MarginModelID', c_char * 13)  # 保证金率模板代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InvestUnitID='', InvestorUnitName='', InvestorGroupID='', CommModelID='', MarginModelID='', AccountID='', CurrencyID=''):
        super(InvestUnitField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.InvestorUnitName = self._to_bytes(InvestorUnitName)
        self.InvestorGroupID = self._to_bytes(InvestorGroupID)
        self.CommModelID = self._to_bytes(CommModelID)
        self.MarginModelID = self._to_bytes(MarginModelID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class QryInvestUnitField(BaseField):
    """查询投资单元"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InvestUnitID=''):
        super(QryInvestUnitField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class SecAgentCheckModeField(BaseField):
    """二级代理商资金校验模式"""
    _fields_ = [
        ('InvestorID', c_char * 13)  # ///投资者代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('CurrencyID', c_char * 4)  # 币种
        , ('BrokerSecAgentID', c_char * 13)  # 境外中介机构资金帐号
        , ('CheckSelfAccount', c_int)  # 是否需要校验自己的资金账户
    ]

    def __init__(self, InvestorID='', BrokerID='', CurrencyID='', BrokerSecAgentID='', CheckSelfAccount=0):
        super(SecAgentCheckModeField, self).__init__()

        self.InvestorID = self._to_bytes(InvestorID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.BrokerSecAgentID = self._to_bytes(BrokerSecAgentID)
        self.CheckSelfAccount = int(CheckSelfAccount)


class SecAgentTradeInfoField(BaseField):
    """二级代理商信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('BrokerSecAgentID', c_char * 13)  # 境外中介机构资金帐号
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('LongCustomerName', c_char * 161)  # 二级代理商姓名
    ]

    def __init__(self, BrokerID='', BrokerSecAgentID='', InvestorID='', LongCustomerName=''):
        super(SecAgentTradeInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerSecAgentID = self._to_bytes(BrokerSecAgentID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class MarketDataField(BaseField):
    """市场行情"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('LastPrice', c_double)  # 最新价
        , ('PreSettlementPrice', c_double)  # 上次结算价
        , ('PreClosePrice', c_double)  # 昨收盘
        , ('PreOpenInterest', c_double)  # 昨持仓量
        , ('OpenPrice', c_double)  # 今开盘
        , ('HighestPrice', c_double)  # 最高价
        , ('LowestPrice', c_double)  # 最低价
        , ('Volume', c_int)  # 数量
        , ('Turnover', c_double)  # 成交金额
        , ('OpenInterest', c_double)  # 持仓量
        , ('ClosePrice', c_double)  # 今收盘
        , ('SettlementPrice', c_double)  # 本次结算价
        , ('UpperLimitPrice', c_double)  # 涨停板价
        , ('LowerLimitPrice', c_double)  # 跌停板价
        , ('PreDelta', c_double)  # 昨虚实度
        , ('CurrDelta', c_double)  # 今虚实度
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('UpdateMillisec', c_int)  # 最后修改毫秒
        , ('ActionDay', c_char * 9)  # 业务日期
    ]

    def __init__(self, TradingDay='', InstrumentID='', ExchangeID='', ExchangeInstID='', LastPrice=0.0, PreSettlementPrice=0.0, PreClosePrice=0.0, PreOpenInterest=0.0, OpenPrice=0.0, HighestPrice=0.0, LowestPrice=0.0,
                 Volume=0, Turnover=0.0, OpenInterest=0.0, ClosePrice=0.0, SettlementPrice=0.0, UpperLimitPrice=0.0, LowerLimitPrice=0.0, PreDelta=0.0, CurrDelta=0.0, UpdateTime='', UpdateMillisec=0, ActionDay=''):
        super(MarketDataField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.LastPrice = float(LastPrice)
        self.PreSettlementPrice = float(PreSettlementPrice)
        self.PreClosePrice = float(PreClosePrice)
        self.PreOpenInterest = float(PreOpenInterest)
        self.OpenPrice = float(OpenPrice)
        self.HighestPrice = float(HighestPrice)
        self.LowestPrice = float(LowestPrice)
        self.Volume = int(Volume)
        self.Turnover = float(Turnover)
        self.OpenInterest = float(OpenInterest)
        self.ClosePrice = float(ClosePrice)
        self.SettlementPrice = float(SettlementPrice)
        self.UpperLimitPrice = float(UpperLimitPrice)
        self.LowerLimitPrice = float(LowerLimitPrice)
        self.PreDelta = float(PreDelta)
        self.CurrDelta = float(CurrDelta)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.UpdateMillisec = int(UpdateMillisec)
        self.ActionDay = self._to_bytes(ActionDay)


class MarketDataBaseField(BaseField):
    """行情基础属性"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('PreSettlementPrice', c_double)  # 上次结算价
        , ('PreClosePrice', c_double)  # 昨收盘
        , ('PreOpenInterest', c_double)  # 昨持仓量
        , ('PreDelta', c_double)  # 昨虚实度
    ]

    def __init__(self, TradingDay='', PreSettlementPrice=0.0, PreClosePrice=0.0, PreOpenInterest=0.0, PreDelta=0.0):
        super(MarketDataBaseField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.PreSettlementPrice = float(PreSettlementPrice)
        self.PreClosePrice = float(PreClosePrice)
        self.PreOpenInterest = float(PreOpenInterest)
        self.PreDelta = float(PreDelta)


class MarketDataStaticField(BaseField):
    """行情静态属性"""
    _fields_ = [
        ('OpenPrice', c_double)  # ///今开盘
        , ('HighestPrice', c_double)  # 最高价
        , ('LowestPrice', c_double)  # 最低价
        , ('ClosePrice', c_double)  # 今收盘
        , ('UpperLimitPrice', c_double)  # 涨停板价
        , ('LowerLimitPrice', c_double)  # 跌停板价
        , ('SettlementPrice', c_double)  # 本次结算价
        , ('CurrDelta', c_double)  # 今虚实度
    ]

    def __init__(self, OpenPrice=0.0, HighestPrice=0.0, LowestPrice=0.0, ClosePrice=0.0, UpperLimitPrice=0.0, LowerLimitPrice=0.0, SettlementPrice=0.0, CurrDelta=0.0):
        super(MarketDataStaticField, self).__init__()

        self.OpenPrice = float(OpenPrice)
        self.HighestPrice = float(HighestPrice)
        self.LowestPrice = float(LowestPrice)
        self.ClosePrice = float(ClosePrice)
        self.UpperLimitPrice = float(UpperLimitPrice)
        self.LowerLimitPrice = float(LowerLimitPrice)
        self.SettlementPrice = float(SettlementPrice)
        self.CurrDelta = float(CurrDelta)


class MarketDataLastMatchField(BaseField):
    """行情最新成交属性"""
    _fields_ = [
        ('LastPrice', c_double)  # ///最新价
        , ('Volume', c_int)  # 数量
        , ('Turnover', c_double)  # 成交金额
        , ('OpenInterest', c_double)  # 持仓量
    ]

    def __init__(self, LastPrice=0.0, Volume=0, Turnover=0.0, OpenInterest=0.0):
        super(MarketDataLastMatchField, self).__init__()

        self.LastPrice = float(LastPrice)
        self.Volume = int(Volume)
        self.Turnover = float(Turnover)
        self.OpenInterest = float(OpenInterest)


class MarketDataBestPriceField(BaseField):
    """行情最优价属性"""
    _fields_ = [
        ('BidPrice1', c_double)  # ///申买价一
        , ('BidVolume1', c_int)  # 申买量一
        , ('AskPrice1', c_double)  # 申卖价一
        , ('AskVolume1', c_int)  # 申卖量一
    ]

    def __init__(self, BidPrice1=0.0, BidVolume1=0, AskPrice1=0.0, AskVolume1=0):
        super(MarketDataBestPriceField, self).__init__()

        self.BidPrice1 = float(BidPrice1)
        self.BidVolume1 = int(BidVolume1)
        self.AskPrice1 = float(AskPrice1)
        self.AskVolume1 = int(AskVolume1)


class MarketDataBid23Field(BaseField):
    """行情申买二、三属性"""
    _fields_ = [
        ('BidPrice2', c_double)  # ///申买价二
        , ('BidVolume2', c_int)  # 申买量二
        , ('BidPrice3', c_double)  # 申买价三
        , ('BidVolume3', c_int)  # 申买量三
    ]

    def __init__(self, BidPrice2=0.0, BidVolume2=0, BidPrice3=0.0, BidVolume3=0):
        super(MarketDataBid23Field, self).__init__()

        self.BidPrice2 = float(BidPrice2)
        self.BidVolume2 = int(BidVolume2)
        self.BidPrice3 = float(BidPrice3)
        self.BidVolume3 = int(BidVolume3)


class MarketDataAsk23Field(BaseField):
    """行情申卖二、三属性"""
    _fields_ = [
        ('AskPrice2', c_double)  # ///申卖价二
        , ('AskVolume2', c_int)  # 申卖量二
        , ('AskPrice3', c_double)  # 申卖价三
        , ('AskVolume3', c_int)  # 申卖量三
    ]

    def __init__(self, AskPrice2=0.0, AskVolume2=0, AskPrice3=0.0, AskVolume3=0):
        super(MarketDataAsk23Field, self).__init__()

        self.AskPrice2 = float(AskPrice2)
        self.AskVolume2 = int(AskVolume2)
        self.AskPrice3 = float(AskPrice3)
        self.AskVolume3 = int(AskVolume3)


class MarketDataBid45Field(BaseField):
    """行情申买四、五属性"""
    _fields_ = [
        ('BidPrice4', c_double)  # ///申买价四
        , ('BidVolume4', c_int)  # 申买量四
        , ('BidPrice5', c_double)  # 申买价五
        , ('BidVolume5', c_int)  # 申买量五
    ]

    def __init__(self, BidPrice4=0.0, BidVolume4=0, BidPrice5=0.0, BidVolume5=0):
        super(MarketDataBid45Field, self).__init__()

        self.BidPrice4 = float(BidPrice4)
        self.BidVolume4 = int(BidVolume4)
        self.BidPrice5 = float(BidPrice5)
        self.BidVolume5 = int(BidVolume5)


class MarketDataAsk45Field(BaseField):
    """行情申卖四、五属性"""
    _fields_ = [
        ('AskPrice4', c_double)  # ///申卖价四
        , ('AskVolume4', c_int)  # 申卖量四
        , ('AskPrice5', c_double)  # 申卖价五
        , ('AskVolume5', c_int)  # 申卖量五
    ]

    def __init__(self, AskPrice4=0.0, AskVolume4=0, AskPrice5=0.0, AskVolume5=0):
        super(MarketDataAsk45Field, self).__init__()

        self.AskPrice4 = float(AskPrice4)
        self.AskVolume4 = int(AskVolume4)
        self.AskPrice5 = float(AskPrice5)
        self.AskVolume5 = int(AskVolume5)


class MarketDataUpdateTimeField(BaseField):
    """行情更新时间属性"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('UpdateMillisec', c_int)  # 最后修改毫秒
        , ('ActionDay', c_char * 9)  # 业务日期
    ]

    def __init__(self, InstrumentID='', UpdateTime='', UpdateMillisec=0, ActionDay=''):
        super(MarketDataUpdateTimeField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.UpdateMillisec = int(UpdateMillisec)
        self.ActionDay = self._to_bytes(ActionDay)


class MarketDataExchangeField(BaseField):
    """行情交易所代码属性"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
    ]

    def __init__(self, ExchangeID=''):
        super(MarketDataExchangeField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)


class SpecificInstrumentField(BaseField):
    """指定的合约"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
    ]

    def __init__(self, InstrumentID=''):
        super(SpecificInstrumentField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)


class InstrumentStatusField(BaseField):
    """合约状态"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('SettlementGroupID', c_char * 9)  # 结算组代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InstrumentStatus', c_char * 1)  # 合约交易状态
        , ('TradingSegmentSN', c_int)  # 交易阶段编号
        , ('EnterTime', c_char * 9)  # 进入本状态时间
        , ('EnterReason', c_char * 1)  # 进入本状态原因
    ]

    def __init__(self, ExchangeID='', ExchangeInstID='', SettlementGroupID='', InstrumentID='', InstrumentStatus='', TradingSegmentSN=0, EnterTime='', EnterReason=''):
        super(InstrumentStatusField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.SettlementGroupID = self._to_bytes(SettlementGroupID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InstrumentStatus = self._to_bytes(InstrumentStatus)
        self.TradingSegmentSN = int(TradingSegmentSN)
        self.EnterTime = self._to_bytes(EnterTime)
        self.EnterReason = self._to_bytes(EnterReason)


class QryInstrumentStatusField(BaseField):
    """查询合约状态"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
    ]

    def __init__(self, ExchangeID='', ExchangeInstID=''):
        super(QryInstrumentStatusField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)


class InvestorAccountField(BaseField):
    """投资者账户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', InvestorID='', AccountID='', CurrencyID=''):
        super(InvestorAccountField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class PositionProfitAlgorithmField(BaseField):
    """浮动盈亏算法"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Algorithm', c_char * 1)  # 盈亏算法
        , ('Memo', c_char * 161)  # 备注
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', Algorithm='', Memo='', CurrencyID=''):
        super(PositionProfitAlgorithmField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.Algorithm = self._to_bytes(Algorithm)
        self.Memo = self._to_bytes(Memo)
        self.CurrencyID = self._to_bytes(CurrencyID)


class DiscountField(BaseField):
    """会员资金折扣"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Discount', c_double)  # 资金折扣比例
    ]

    def __init__(self, BrokerID='', InvestorRange='', InvestorID='', Discount=0.0):
        super(DiscountField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Discount = float(Discount)


class QryTransferBankField(BaseField):
    """查询转帐银行"""
    _fields_ = [
        ('BankID', c_char * 4)  # ///银行代码
        , ('BankBrchID', c_char * 5)  # 银行分中心代码
    ]

    def __init__(self, BankID='', BankBrchID=''):
        super(QryTransferBankField, self).__init__()

        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)


class TransferBankField(BaseField):
    """转帐银行"""
    _fields_ = [
        ('BankID', c_char * 4)  # ///银行代码
        , ('BankBrchID', c_char * 5)  # 银行分中心代码
        , ('BankName', c_char * 101)  # 银行名称
        , ('IsActive', c_int)  # 是否活跃
    ]

    def __init__(self, BankID='', BankBrchID='', BankName='', IsActive=0):
        super(TransferBankField, self).__init__()

        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)
        self.BankName = self._to_bytes(BankName)
        self.IsActive = int(IsActive)


class QryInvestorPositionDetailField(BaseField):
    """查询投资者持仓明细"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryInvestorPositionDetailField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class InvestorPositionDetailField(BaseField):
    """投资者持仓明细"""
    _fields_ = [
        ('InstrumentID', c_char * 31)  # ///合约代码
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('Direction', c_char * 1)  # 买卖
        , ('OpenDate', c_char * 9)  # 开仓日期
        , ('TradeID', c_char * 21)  # 成交编号
        , ('Volume', c_int)  # 数量
        , ('OpenPrice', c_double)  # 开仓价
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('TradeType', c_char * 1)  # 成交类型
        , ('CombInstrumentID', c_char * 31)  # 组合合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('CloseProfitByDate', c_double)  # 逐日盯市平仓盈亏
        , ('CloseProfitByTrade', c_double)  # 逐笔对冲平仓盈亏
        , ('PositionProfitByDate', c_double)  # 逐日盯市持仓盈亏
        , ('PositionProfitByTrade', c_double)  # 逐笔对冲持仓盈亏
        , ('Margin', c_double)  # 投资者保证金
        , ('ExchMargin', c_double)  # 交易所保证金
        , ('MarginRateByMoney', c_double)  # 保证金率
        , ('MarginRateByVolume', c_double)  # 保证金率(按手数)
        , ('LastSettlementPrice', c_double)  # 昨结算价
        , ('SettlementPrice', c_double)  # 结算价
        , ('CloseVolume', c_int)  # 平仓量
        , ('CloseAmount', c_double)  # 平仓金额
        , ('TimeFirstVolume', c_int)  # 按照时间顺序平仓的笔数,大商所专用
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, InstrumentID='', BrokerID='', InvestorID='', HedgeFlag='', Direction='', OpenDate='', TradeID='', Volume=0, OpenPrice=0.0, TradingDay='', SettlementID=0, TradeType='', CombInstrumentID='',
                 ExchangeID='', CloseProfitByDate=0.0, CloseProfitByTrade=0.0, PositionProfitByDate=0.0, PositionProfitByTrade=0.0, Margin=0.0, ExchMargin=0.0, MarginRateByMoney=0.0, MarginRateByVolume=0.0,
                 LastSettlementPrice=0.0, SettlementPrice=0.0, CloseVolume=0, CloseAmount=0.0, TimeFirstVolume=0, InvestUnitID=''):
        super(InvestorPositionDetailField, self).__init__()

        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.Direction = self._to_bytes(Direction)
        self.OpenDate = self._to_bytes(OpenDate)
        self.TradeID = self._to_bytes(TradeID)
        self.Volume = int(Volume)
        self.OpenPrice = float(OpenPrice)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.TradeType = self._to_bytes(TradeType)
        self.CombInstrumentID = self._to_bytes(CombInstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.CloseProfitByDate = float(CloseProfitByDate)
        self.CloseProfitByTrade = float(CloseProfitByTrade)
        self.PositionProfitByDate = float(PositionProfitByDate)
        self.PositionProfitByTrade = float(PositionProfitByTrade)
        self.Margin = float(Margin)
        self.ExchMargin = float(ExchMargin)
        self.MarginRateByMoney = float(MarginRateByMoney)
        self.MarginRateByVolume = float(MarginRateByVolume)
        self.LastSettlementPrice = float(LastSettlementPrice)
        self.SettlementPrice = float(SettlementPrice)
        self.CloseVolume = int(CloseVolume)
        self.CloseAmount = float(CloseAmount)
        self.TimeFirstVolume = int(TimeFirstVolume)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class TradingAccountPasswordField(BaseField):
    """资金账户口令域"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 密码
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', Password='', CurrencyID=''):
        super(TradingAccountPasswordField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.CurrencyID = self._to_bytes(CurrencyID)


class MDTraderOfferField(BaseField):
    """交易所行情报盘机"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('Password', c_char * 41)  # 密码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('TraderConnectStatus', c_char * 1)  # 交易所交易员连接状态
        , ('ConnectRequestDate', c_char * 9)  # 发出连接请求的日期
        , ('ConnectRequestTime', c_char * 9)  # 发出连接请求的时间
        , ('LastReportDate', c_char * 9)  # 上次报告日期
        , ('LastReportTime', c_char * 9)  # 上次报告时间
        , ('ConnectDate', c_char * 9)  # 完成连接日期
        , ('ConnectTime', c_char * 9)  # 完成连接时间
        , ('StartDate', c_char * 9)  # 启动日期
        , ('StartTime', c_char * 9)  # 启动时间
        , ('TradingDay', c_char * 9)  # 交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('MaxTradeID', c_char * 21)  # 本席位最大成交编号
        , ('MaxOrderMessageReference', c_char * 7)  # 本席位最大报单备拷
    ]

    def __init__(self, ExchangeID='', TraderID='', ParticipantID='', Password='', InstallID=0, OrderLocalID='', TraderConnectStatus='', ConnectRequestDate='', ConnectRequestTime='', LastReportDate='', LastReportTime='',
                 ConnectDate='', ConnectTime='', StartDate='', StartTime='', TradingDay='', BrokerID='', MaxTradeID='', MaxOrderMessageReference=''):
        super(MDTraderOfferField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TraderID = self._to_bytes(TraderID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.TraderConnectStatus = self._to_bytes(TraderConnectStatus)
        self.ConnectRequestDate = self._to_bytes(ConnectRequestDate)
        self.ConnectRequestTime = self._to_bytes(ConnectRequestTime)
        self.LastReportDate = self._to_bytes(LastReportDate)
        self.LastReportTime = self._to_bytes(LastReportTime)
        self.ConnectDate = self._to_bytes(ConnectDate)
        self.ConnectTime = self._to_bytes(ConnectTime)
        self.StartDate = self._to_bytes(StartDate)
        self.StartTime = self._to_bytes(StartTime)
        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.MaxTradeID = self._to_bytes(MaxTradeID)
        self.MaxOrderMessageReference = self._to_bytes(MaxOrderMessageReference)


class QryMDTraderOfferField(BaseField):
    """查询行情报盘机"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
    ]

    def __init__(self, ExchangeID='', ParticipantID='', TraderID=''):
        super(QryMDTraderOfferField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.TraderID = self._to_bytes(TraderID)


class QryNoticeField(BaseField):
    """查询客户通知"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(QryNoticeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class NoticeField(BaseField):
    """客户通知"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('Content', c_char * 501)  # 消息正文
        , ('SequenceLabel', c_char * 2)  # 经纪公司通知内容序列号
    ]

    def __init__(self, BrokerID='', Content='', SequenceLabel=''):
        super(NoticeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.Content = self._to_bytes(Content)
        self.SequenceLabel = self._to_bytes(SequenceLabel)


class UserRightField(BaseField):
    """用户权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserRightType', c_char * 1)  # 客户权限类型
        , ('IsForbidden', c_int)  # 是否禁止
    ]

    def __init__(self, BrokerID='', UserID='', UserRightType='', IsForbidden=0):
        super(UserRightField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserRightType = self._to_bytes(UserRightType)
        self.IsForbidden = int(IsForbidden)


class QrySettlementInfoConfirmField(BaseField):
    """查询结算信息确认域"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', InvestorID='', AccountID='', CurrencyID=''):
        super(QrySettlementInfoConfirmField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class LoadSettlementInfoField(BaseField):
    """装载结算信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(LoadSettlementInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class BrokerWithdrawAlgorithmField(BaseField):
    """经纪公司可提资金算法表"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('WithdrawAlgorithm', c_char * 1)  # 可提资金算法
        , ('UsingRatio', c_double)  # 资金使用率
        , ('IncludeCloseProfit', c_char * 1)  # 可提是否包含平仓盈利
        , ('AllWithoutTrade', c_char * 1)  # 本日无仓且无成交客户是否受可提比例限制
        , ('AvailIncludeCloseProfit', c_char * 1)  # 可用是否包含平仓盈利
        , ('IsBrokerUserEvent', c_int)  # 是否启用用户事件
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('FundMortgageRatio', c_double)  # 货币质押比率
        , ('BalanceAlgorithm', c_char * 1)  # 权益算法
    ]

    def __init__(self, BrokerID='', WithdrawAlgorithm='', UsingRatio=0.0, IncludeCloseProfit='', AllWithoutTrade='', AvailIncludeCloseProfit='', IsBrokerUserEvent=0, CurrencyID='', FundMortgageRatio=0.0,
                 BalanceAlgorithm=''):
        super(BrokerWithdrawAlgorithmField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.WithdrawAlgorithm = self._to_bytes(WithdrawAlgorithm)
        self.UsingRatio = float(UsingRatio)
        self.IncludeCloseProfit = self._to_bytes(IncludeCloseProfit)
        self.AllWithoutTrade = self._to_bytes(AllWithoutTrade)
        self.AvailIncludeCloseProfit = self._to_bytes(AvailIncludeCloseProfit)
        self.IsBrokerUserEvent = int(IsBrokerUserEvent)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.FundMortgageRatio = float(FundMortgageRatio)
        self.BalanceAlgorithm = self._to_bytes(BalanceAlgorithm)


class TradingAccountPasswordUpdateV1Field(BaseField):
    """资金账户口令变更域"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OldPassword', c_char * 41)  # 原来的口令
        , ('NewPassword', c_char * 41)  # 新的口令
    ]

    def __init__(self, BrokerID='', InvestorID='', OldPassword='', NewPassword=''):
        super(TradingAccountPasswordUpdateV1Field, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OldPassword = self._to_bytes(OldPassword)
        self.NewPassword = self._to_bytes(NewPassword)


class TradingAccountPasswordUpdateField(BaseField):
    """资金账户口令变更域"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('OldPassword', c_char * 41)  # 原来的口令
        , ('NewPassword', c_char * 41)  # 新的口令
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', OldPassword='', NewPassword='', CurrencyID=''):
        super(TradingAccountPasswordUpdateField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.OldPassword = self._to_bytes(OldPassword)
        self.NewPassword = self._to_bytes(NewPassword)
        self.CurrencyID = self._to_bytes(CurrencyID)


class QryCombinationLegField(BaseField):
    """查询组合合约分腿"""
    _fields_ = [
        ('CombInstrumentID', c_char * 31)  # ///组合合约代码
        , ('LegID', c_int)  # 单腿编号
        , ('LegInstrumentID', c_char * 31)  # 单腿合约代码
    ]

    def __init__(self, CombInstrumentID='', LegID=0, LegInstrumentID=''):
        super(QryCombinationLegField, self).__init__()

        self.CombInstrumentID = self._to_bytes(CombInstrumentID)
        self.LegID = int(LegID)
        self.LegInstrumentID = self._to_bytes(LegInstrumentID)


class QrySyncStatusField(BaseField):
    """查询组合合约分腿"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
    ]

    def __init__(self, TradingDay=''):
        super(QrySyncStatusField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)


class CombinationLegField(BaseField):
    """组合交易合约的单腿"""
    _fields_ = [
        ('CombInstrumentID', c_char * 31)  # ///组合合约代码
        , ('LegID', c_int)  # 单腿编号
        , ('LegInstrumentID', c_char * 31)  # 单腿合约代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('LegMultiple', c_int)  # 单腿乘数
        , ('ImplyLevel', c_int)  # 派生层数
    ]

    def __init__(self, CombInstrumentID='', LegID=0, LegInstrumentID='', Direction='', LegMultiple=0, ImplyLevel=0):
        super(CombinationLegField, self).__init__()

        self.CombInstrumentID = self._to_bytes(CombInstrumentID)
        self.LegID = int(LegID)
        self.LegInstrumentID = self._to_bytes(LegInstrumentID)
        self.Direction = self._to_bytes(Direction)
        self.LegMultiple = int(LegMultiple)
        self.ImplyLevel = int(ImplyLevel)


class SyncStatusField(BaseField):
    """数据同步状态"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('DataSyncStatus', c_char * 1)  # 数据同步状态
    ]

    def __init__(self, TradingDay='', DataSyncStatus=''):
        super(SyncStatusField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.DataSyncStatus = self._to_bytes(DataSyncStatus)


class QryLinkManField(BaseField):
    """查询联系人"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryLinkManField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class LinkManField(BaseField):
    """联系人"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('PersonType', c_char * 1)  # 联系人类型
        , ('IdentifiedCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('PersonName', c_char * 81)  # 名称
        , ('Telephone', c_char * 41)  # 联系电话
        , ('Address', c_char * 101)  # 通讯地址
        , ('ZipCode', c_char * 7)  # 邮政编码
        , ('Priority', c_int)  # 优先级
        , ('UOAZipCode', c_char * 11)  # 开户邮政编码
        , ('PersonFullName', c_char * 101)  # 全称
    ]

    def __init__(self, BrokerID='', InvestorID='', PersonType='', IdentifiedCardType='', IdentifiedCardNo='', PersonName='', Telephone='', Address='', ZipCode='', Priority=0, UOAZipCode='', PersonFullName=''):
        super(LinkManField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.PersonType = self._to_bytes(PersonType)
        self.IdentifiedCardType = self._to_bytes(IdentifiedCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.PersonName = self._to_bytes(PersonName)
        self.Telephone = self._to_bytes(Telephone)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Priority = int(Priority)
        self.UOAZipCode = self._to_bytes(UOAZipCode)
        self.PersonFullName = self._to_bytes(PersonFullName)


class QryBrokerUserEventField(BaseField):
    """查询经纪公司用户事件"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserEventType', c_char * 1)  # 用户事件类型
    ]

    def __init__(self, BrokerID='', UserID='', UserEventType=''):
        super(QryBrokerUserEventField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserEventType = self._to_bytes(UserEventType)


class BrokerUserEventField(BaseField):
    """查询经纪公司用户事件"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('UserEventType', c_char * 1)  # 用户事件类型
        , ('EventSequenceNo', c_int)  # 用户事件序号
        , ('EventDate', c_char * 9)  # 事件发生日期
        , ('EventTime', c_char * 9)  # 事件发生时间
        , ('UserEventInfo', c_char * 1025)  # 用户事件信息
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', UserID='', UserEventType='', EventSequenceNo=0, EventDate='', EventTime='', UserEventInfo='', InvestorID='', InstrumentID=''):
        super(BrokerUserEventField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.UserEventType = self._to_bytes(UserEventType)
        self.EventSequenceNo = int(EventSequenceNo)
        self.EventDate = self._to_bytes(EventDate)
        self.EventTime = self._to_bytes(EventTime)
        self.UserEventInfo = self._to_bytes(UserEventInfo)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class QryContractBankField(BaseField):
    """查询签约银行请求"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBrchID', c_char * 5)  # 银行分中心代码
    ]

    def __init__(self, BrokerID='', BankID='', BankBrchID=''):
        super(QryContractBankField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)


class ContractBankField(BaseField):
    """查询签约银行响应"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBrchID', c_char * 5)  # 银行分中心代码
        , ('BankName', c_char * 101)  # 银行名称
    ]

    def __init__(self, BrokerID='', BankID='', BankBrchID='', BankName=''):
        super(ContractBankField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.BankID = self._to_bytes(BankID)
        self.BankBrchID = self._to_bytes(BankBrchID)
        self.BankName = self._to_bytes(BankName)


class InvestorPositionCombineDetailField(BaseField):
    """投资者组合持仓明细"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('OpenDate', c_char * 9)  # 开仓日期
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('SettlementID', c_int)  # 结算编号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ComTradeID', c_char * 21)  # 组合编号
        , ('TradeID', c_char * 21)  # 撮合编号
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('Direction', c_char * 1)  # 买卖
        , ('TotalAmt', c_int)  # 持仓量
        , ('Margin', c_double)  # 投资者保证金
        , ('ExchMargin', c_double)  # 交易所保证金
        , ('MarginRateByMoney', c_double)  # 保证金率
        , ('MarginRateByVolume', c_double)  # 保证金率(按手数)
        , ('LegID', c_int)  # 单腿编号
        , ('LegMultiple', c_int)  # 单腿乘数
        , ('CombInstrumentID', c_char * 31)  # 组合持仓合约编码
        , ('TradeGroupID', c_int)  # 成交组号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, TradingDay='', OpenDate='', ExchangeID='', SettlementID=0, BrokerID='', InvestorID='', ComTradeID='', TradeID='', InstrumentID='', HedgeFlag='', Direction='', TotalAmt=0, Margin=0.0, ExchMargin=0.0,
                 MarginRateByMoney=0.0, MarginRateByVolume=0.0, LegID=0, LegMultiple=0, CombInstrumentID='', TradeGroupID=0, InvestUnitID=''):
        super(InvestorPositionCombineDetailField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.OpenDate = self._to_bytes(OpenDate)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.SettlementID = int(SettlementID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ComTradeID = self._to_bytes(ComTradeID)
        self.TradeID = self._to_bytes(TradeID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.Direction = self._to_bytes(Direction)
        self.TotalAmt = int(TotalAmt)
        self.Margin = float(Margin)
        self.ExchMargin = float(ExchMargin)
        self.MarginRateByMoney = float(MarginRateByMoney)
        self.MarginRateByVolume = float(MarginRateByVolume)
        self.LegID = int(LegID)
        self.LegMultiple = int(LegMultiple)
        self.CombInstrumentID = self._to_bytes(CombInstrumentID)
        self.TradeGroupID = int(TradeGroupID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class ParkedOrderField(BaseField):
    """预埋单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('OrderPriceType', c_char * 1)  # 报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('UserForceClose', c_int)  # 用户强评标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParkedOrderID', c_char * 13)  # 预埋报单编号
        , ('UserType', c_char * 1)  # 用户类型
        , ('Status', c_char * 1)  # 预埋单状态
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('IsSwapOrder', c_int)  # 互换单标志
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='',
                 GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='', StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, UserForceClose=0, ExchangeID='', ParkedOrderID='',
                 UserType='', Status='', ErrorID=0, ErrorMsg='', IsSwapOrder=0, AccountID='', CurrencyID='', ClientID='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(ParkedOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.UserForceClose = int(UserForceClose)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParkedOrderID = self._to_bytes(ParkedOrderID)
        self.UserType = self._to_bytes(UserType)
        self.Status = self._to_bytes(Status)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.IsSwapOrder = int(IsSwapOrder)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ParkedOrderActionField(BaseField):
    """输入预埋单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeChange', c_int)  # 数量变化
        , ('UserID', c_char * 16)  # 用户代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ParkedOrderActionID', c_char * 13)  # 预埋撤单单编号
        , ('UserType', c_char * 1)  # 用户类型
        , ('Status', c_char * 1)  # 预埋撤单状态
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, OrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OrderSysID='', ActionFlag='', LimitPrice=0.0, VolumeChange=0, UserID='',
                 InstrumentID='', ParkedOrderActionID='', UserType='', Status='', ErrorID=0, ErrorMsg='', InvestUnitID='', IPAddress='', MacAddress=''):
        super(ParkedOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.OrderRef = self._to_bytes(OrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeChange = int(VolumeChange)
        self.UserID = self._to_bytes(UserID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ParkedOrderActionID = self._to_bytes(ParkedOrderActionID)
        self.UserType = self._to_bytes(UserType)
        self.Status = self._to_bytes(Status)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryParkedOrderField(BaseField):
    """查询预埋单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryParkedOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryParkedOrderActionField(BaseField):
    """查询预埋撤单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryParkedOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class RemoveParkedOrderField(BaseField):
    """删除预埋单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ParkedOrderID', c_char * 13)  # 预埋报单编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ParkedOrderID='', InvestUnitID=''):
        super(RemoveParkedOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ParkedOrderID = self._to_bytes(ParkedOrderID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class RemoveParkedOrderActionField(BaseField):
    """删除预埋撤单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ParkedOrderActionID', c_char * 13)  # 预埋撤单编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ParkedOrderActionID='', InvestUnitID=''):
        super(RemoveParkedOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ParkedOrderActionID = self._to_bytes(ParkedOrderActionID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class InvestorWithdrawAlgorithmField(BaseField):
    """经纪公司可提资金算法表"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('UsingRatio', c_double)  # 可提资金比例
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('FundMortgageRatio', c_double)  # 货币质押比率
    ]

    def __init__(self, BrokerID='', InvestorRange='', InvestorID='', UsingRatio=0.0, CurrencyID='', FundMortgageRatio=0.0):
        super(InvestorWithdrawAlgorithmField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.InvestorID = self._to_bytes(InvestorID)
        self.UsingRatio = float(UsingRatio)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.FundMortgageRatio = float(FundMortgageRatio)


class QryInvestorPositionCombineDetailField(BaseField):
    """查询组合持仓明细"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('CombInstrumentID', c_char * 31)  # 组合持仓合约编码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', CombInstrumentID='', ExchangeID='', InvestUnitID=''):
        super(QryInvestorPositionCombineDetailField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.CombInstrumentID = self._to_bytes(CombInstrumentID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class MarketDataAveragePriceField(BaseField):
    """成交均价"""
    _fields_ = [
        ('AveragePrice', c_double)  # ///当日均价
    ]

    def __init__(self, AveragePrice=0.0):
        super(MarketDataAveragePriceField, self).__init__()

        self.AveragePrice = float(AveragePrice)


class VerifyInvestorPasswordField(BaseField):
    """校验投资者密码"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Password', c_char * 41)  # 密码
    ]

    def __init__(self, BrokerID='', InvestorID='', Password=''):
        super(VerifyInvestorPasswordField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Password = self._to_bytes(Password)


class UserIPField(BaseField):
    """用户IP"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('IPMask', c_char * 16)  # IP地址掩码
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', UserID='', IPAddress='', IPMask='', MacAddress=''):
        super(UserIPField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.IPMask = self._to_bytes(IPMask)
        self.MacAddress = self._to_bytes(MacAddress)


class TradingNoticeInfoField(BaseField):
    """用户事件通知信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('SendTime', c_char * 9)  # 发送时间
        , ('FieldContent', c_char * 501)  # 消息正文
        , ('SequenceSeries', c_short)  # 序列系列号
        , ('SequenceNo', c_int)  # 序列号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', SendTime='', FieldContent='', SequenceSeries=0, SequenceNo=0, InvestUnitID=''):
        super(TradingNoticeInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.SendTime = self._to_bytes(SendTime)
        self.FieldContent = self._to_bytes(FieldContent)
        self.SequenceSeries = int(SequenceSeries)
        self.SequenceNo = int(SequenceNo)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class TradingNoticeField(BaseField):
    """用户事件通知"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('SequenceSeries', c_short)  # 序列系列号
        , ('UserID', c_char * 16)  # 用户代码
        , ('SendTime', c_char * 9)  # 发送时间
        , ('SequenceNo', c_int)  # 序列号
        , ('FieldContent', c_char * 501)  # 消息正文
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorRange='', InvestorID='', SequenceSeries=0, UserID='', SendTime='', SequenceNo=0, FieldContent='', InvestUnitID=''):
        super(TradingNoticeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.InvestorID = self._to_bytes(InvestorID)
        self.SequenceSeries = int(SequenceSeries)
        self.UserID = self._to_bytes(UserID)
        self.SendTime = self._to_bytes(SendTime)
        self.SequenceNo = int(SequenceNo)
        self.FieldContent = self._to_bytes(FieldContent)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryTradingNoticeField(BaseField):
    """查询交易事件通知"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InvestUnitID=''):
        super(QryTradingNoticeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryErrOrderField(BaseField):
    """查询错误报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryErrOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class ErrOrderField(BaseField):
    """错误报单"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('OrderPriceType', c_char * 1)  # 报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('UserForceClose', c_int)  # 用户强评标志
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('IsSwapOrder', c_int)  # 互换单标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('ClientID', c_char * 11)  # 交易编码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='',
                 GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='', StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, UserForceClose=0, ErrorID=0, ErrorMsg='',
                 IsSwapOrder=0, ExchangeID='', InvestUnitID='', AccountID='', CurrencyID='', ClientID='', IPAddress='', MacAddress=''):
        super(ErrOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.UserForceClose = int(UserForceClose)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.IsSwapOrder = int(IsSwapOrder)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.ClientID = self._to_bytes(ClientID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class ErrorConditionalOrderField(BaseField):
    """查询错误报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('UserID', c_char * 16)  # 用户代码
        , ('OrderPriceType', c_char * 1)  # 报单价格条件
        , ('Direction', c_char * 1)  # 买卖方向
        , ('CombOffsetFlag', c_char * 5)  # 组合开平标志
        , ('CombHedgeFlag', c_char * 5)  # 组合投机套保标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeTotalOriginal', c_int)  # 数量
        , ('TimeCondition', c_char * 1)  # 有效期类型
        , ('GTDDate', c_char * 9)  # GTD日期
        , ('VolumeCondition', c_char * 1)  # 成交量类型
        , ('MinVolume', c_int)  # 最小成交量
        , ('ContingentCondition', c_char * 1)  # 触发条件
        , ('StopPrice', c_double)  # 止损价
        , ('ForceCloseReason', c_char * 1)  # 强平原因
        , ('IsAutoSuspend', c_int)  # 自动挂起标志
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('RequestID', c_int)  # 请求编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('ExchangeInstID', c_char * 31)  # 合约在交易所的代码
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderSubmitStatus', c_char * 1)  # 报单提交状态
        , ('NotifySequence', c_int)  # 报单提示序号
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('OrderSource', c_char * 1)  # 报单来源
        , ('OrderStatus', c_char * 1)  # 报单状态
        , ('OrderType', c_char * 1)  # 报单类型
        , ('VolumeTraded', c_int)  # 今成交数量
        , ('VolumeTotal', c_int)  # 剩余数量
        , ('InsertDate', c_char * 9)  # 报单日期
        , ('InsertTime', c_char * 9)  # 委托时间
        , ('ActiveTime', c_char * 9)  # 激活时间
        , ('SuspendTime', c_char * 9)  # 挂起时间
        , ('UpdateTime', c_char * 9)  # 最后修改时间
        , ('CancelTime', c_char * 9)  # 撤销时间
        , ('ActiveTraderID', c_char * 21)  # 最后修改交易所交易员代码
        , ('ClearingPartID', c_char * 11)  # 结算会员编号
        , ('SequenceNo', c_int)  # 序号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('UserForceClose', c_int)  # 用户强评标志
        , ('ActiveUserID', c_char * 16)  # 操作用户代码
        , ('BrokerOrderSeq', c_int)  # 经纪公司报单编号
        , ('RelativeOrderSysID', c_char * 21)  # 相关报单
        , ('ZCETotalTradedVolume', c_int)  # 郑商所成交数量
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('IsSwapOrder', c_int)  # 互换单标志
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('AccountID', c_char * 13)  # 资金账号
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', OrderRef='', UserID='', OrderPriceType='', Direction='', CombOffsetFlag='', CombHedgeFlag='', LimitPrice=0.0, VolumeTotalOriginal=0, TimeCondition='',
                 GTDDate='', VolumeCondition='', MinVolume=0, ContingentCondition='', StopPrice=0.0, ForceCloseReason='', IsAutoSuspend=0, BusinessUnit='', RequestID=0, OrderLocalID='', ExchangeID='', ParticipantID='',
                 ClientID='', ExchangeInstID='', TraderID='', InstallID=0, OrderSubmitStatus='', NotifySequence=0, TradingDay='', SettlementID=0, OrderSysID='', OrderSource='', OrderStatus='', OrderType='', VolumeTraded=0,
                 VolumeTotal=0, InsertDate='', InsertTime='', ActiveTime='', SuspendTime='', UpdateTime='', CancelTime='', ActiveTraderID='', ClearingPartID='', SequenceNo=0, FrontID=0, SessionID=0, UserProductInfo='',
                 StatusMsg='', UserForceClose=0, ActiveUserID='', BrokerOrderSeq=0, RelativeOrderSysID='', ZCETotalTradedVolume=0, ErrorID=0, ErrorMsg='', IsSwapOrder=0, BranchID='', InvestUnitID='', AccountID='',
                 CurrencyID='', IPAddress='', MacAddress=''):
        super(ErrorConditionalOrderField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.OrderRef = self._to_bytes(OrderRef)
        self.UserID = self._to_bytes(UserID)
        self.OrderPriceType = self._to_bytes(OrderPriceType)
        self.Direction = self._to_bytes(Direction)
        self.CombOffsetFlag = self._to_bytes(CombOffsetFlag)
        self.CombHedgeFlag = self._to_bytes(CombHedgeFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeTotalOriginal = int(VolumeTotalOriginal)
        self.TimeCondition = self._to_bytes(TimeCondition)
        self.GTDDate = self._to_bytes(GTDDate)
        self.VolumeCondition = self._to_bytes(VolumeCondition)
        self.MinVolume = int(MinVolume)
        self.ContingentCondition = self._to_bytes(ContingentCondition)
        self.StopPrice = float(StopPrice)
        self.ForceCloseReason = self._to_bytes(ForceCloseReason)
        self.IsAutoSuspend = int(IsAutoSuspend)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.RequestID = int(RequestID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.ExchangeInstID = self._to_bytes(ExchangeInstID)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderSubmitStatus = self._to_bytes(OrderSubmitStatus)
        self.NotifySequence = int(NotifySequence)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.OrderSource = self._to_bytes(OrderSource)
        self.OrderStatus = self._to_bytes(OrderStatus)
        self.OrderType = self._to_bytes(OrderType)
        self.VolumeTraded = int(VolumeTraded)
        self.VolumeTotal = int(VolumeTotal)
        self.InsertDate = self._to_bytes(InsertDate)
        self.InsertTime = self._to_bytes(InsertTime)
        self.ActiveTime = self._to_bytes(ActiveTime)
        self.SuspendTime = self._to_bytes(SuspendTime)
        self.UpdateTime = self._to_bytes(UpdateTime)
        self.CancelTime = self._to_bytes(CancelTime)
        self.ActiveTraderID = self._to_bytes(ActiveTraderID)
        self.ClearingPartID = self._to_bytes(ClearingPartID)
        self.SequenceNo = int(SequenceNo)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.UserForceClose = int(UserForceClose)
        self.ActiveUserID = self._to_bytes(ActiveUserID)
        self.BrokerOrderSeq = int(BrokerOrderSeq)
        self.RelativeOrderSysID = self._to_bytes(RelativeOrderSysID)
        self.ZCETotalTradedVolume = int(ZCETotalTradedVolume)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.IsSwapOrder = int(IsSwapOrder)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)


class QryErrOrderActionField(BaseField):
    """查询错误报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryErrOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class ErrOrderActionField(BaseField):
    """错误报单操作"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('OrderActionRef', c_int)  # 报单操作引用
        , ('OrderRef', c_char * 13)  # 报单引用
        , ('RequestID', c_int)  # 请求编号
        , ('FrontID', c_int)  # 前置编号
        , ('SessionID', c_int)  # 会话编号
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('OrderSysID', c_char * 21)  # 报单编号
        , ('ActionFlag', c_char * 1)  # 操作标志
        , ('LimitPrice', c_double)  # 价格
        , ('VolumeChange', c_int)  # 数量变化
        , ('ActionDate', c_char * 9)  # 操作日期
        , ('ActionTime', c_char * 9)  # 操作时间
        , ('TraderID', c_char * 21)  # 交易所交易员代码
        , ('InstallID', c_int)  # 安装编号
        , ('OrderLocalID', c_char * 13)  # 本地报单编号
        , ('ActionLocalID', c_char * 13)  # 操作本地编号
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ClientID', c_char * 11)  # 客户代码
        , ('BusinessUnit', c_char * 21)  # 业务单元
        , ('OrderActionStatus', c_char * 1)  # 报单操作状态
        , ('UserID', c_char * 16)  # 用户代码
        , ('StatusMsg', c_char * 81)  # 状态信息
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('BranchID', c_char * 9)  # 营业部编号
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
        , ('IPAddress', c_char * 16)  # IP地址
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, BrokerID='', InvestorID='', OrderActionRef=0, OrderRef='', RequestID=0, FrontID=0, SessionID=0, ExchangeID='', OrderSysID='', ActionFlag='', LimitPrice=0.0, VolumeChange=0, ActionDate='',
                 ActionTime='', TraderID='', InstallID=0, OrderLocalID='', ActionLocalID='', ParticipantID='', ClientID='', BusinessUnit='', OrderActionStatus='', UserID='', StatusMsg='', InstrumentID='', BranchID='',
                 InvestUnitID='', IPAddress='', MacAddress='', ErrorID=0, ErrorMsg=''):
        super(ErrOrderActionField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.OrderActionRef = int(OrderActionRef)
        self.OrderRef = self._to_bytes(OrderRef)
        self.RequestID = int(RequestID)
        self.FrontID = int(FrontID)
        self.SessionID = int(SessionID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.OrderSysID = self._to_bytes(OrderSysID)
        self.ActionFlag = self._to_bytes(ActionFlag)
        self.LimitPrice = float(LimitPrice)
        self.VolumeChange = int(VolumeChange)
        self.ActionDate = self._to_bytes(ActionDate)
        self.ActionTime = self._to_bytes(ActionTime)
        self.TraderID = self._to_bytes(TraderID)
        self.InstallID = int(InstallID)
        self.OrderLocalID = self._to_bytes(OrderLocalID)
        self.ActionLocalID = self._to_bytes(ActionLocalID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ClientID = self._to_bytes(ClientID)
        self.BusinessUnit = self._to_bytes(BusinessUnit)
        self.OrderActionStatus = self._to_bytes(OrderActionStatus)
        self.UserID = self._to_bytes(UserID)
        self.StatusMsg = self._to_bytes(StatusMsg)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.BranchID = self._to_bytes(BranchID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)
        self.IPAddress = self._to_bytes(IPAddress)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class QryExchangeSequenceField(BaseField):
    """查询交易所状态"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
    ]

    def __init__(self, ExchangeID=''):
        super(QryExchangeSequenceField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)


class ExchangeSequenceField(BaseField):
    """交易所状态"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('SequenceNo', c_int)  # 序号
        , ('MarketStatus', c_char * 1)  # 合约交易状态
    ]

    def __init__(self, ExchangeID='', SequenceNo=0, MarketStatus=''):
        super(ExchangeSequenceField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.SequenceNo = int(SequenceNo)
        self.MarketStatus = self._to_bytes(MarketStatus)


class QueryMaxOrderVolumeWithPriceField(BaseField):
    """根据价格查询最大报单数量"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('OffsetFlag', c_char * 1)  # 开平标志
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('MaxVolume', c_int)  # 最大允许报单数量
        , ('Price', c_double)  # 报单价格
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InstrumentID='', Direction='', OffsetFlag='', HedgeFlag='', MaxVolume=0, Price=0.0, ExchangeID='', InvestUnitID=''):
        super(QueryMaxOrderVolumeWithPriceField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.Direction = self._to_bytes(Direction)
        self.OffsetFlag = self._to_bytes(OffsetFlag)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.MaxVolume = int(MaxVolume)
        self.Price = float(Price)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryBrokerTradingParamsField(BaseField):
    """查询经纪公司交易参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('AccountID', c_char * 13)  # 投资者帐号
    ]

    def __init__(self, BrokerID='', InvestorID='', CurrencyID='', AccountID=''):
        super(QryBrokerTradingParamsField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.AccountID = self._to_bytes(AccountID)


class BrokerTradingParamsField(BaseField):
    """经纪公司交易参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('MarginPriceType', c_char * 1)  # 保证金价格类型
        , ('Algorithm', c_char * 1)  # 盈亏算法
        , ('AvailIncludeCloseProfit', c_char * 1)  # 可用是否包含平仓盈利
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('OptionRoyaltyPriceType', c_char * 1)  # 期权权利金价格类型
        , ('AccountID', c_char * 13)  # 投资者帐号
    ]

    def __init__(self, BrokerID='', InvestorID='', MarginPriceType='', Algorithm='', AvailIncludeCloseProfit='', CurrencyID='', OptionRoyaltyPriceType='', AccountID=''):
        super(BrokerTradingParamsField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.MarginPriceType = self._to_bytes(MarginPriceType)
        self.Algorithm = self._to_bytes(Algorithm)
        self.AvailIncludeCloseProfit = self._to_bytes(AvailIncludeCloseProfit)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.OptionRoyaltyPriceType = self._to_bytes(OptionRoyaltyPriceType)
        self.AccountID = self._to_bytes(AccountID)


class QryBrokerTradingAlgosField(BaseField):
    """查询经纪公司交易算法"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InstrumentID', c_char * 31)  # 合约代码
    ]

    def __init__(self, BrokerID='', ExchangeID='', InstrumentID=''):
        super(QryBrokerTradingAlgosField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InstrumentID = self._to_bytes(InstrumentID)


class BrokerTradingAlgosField(BaseField):
    """经纪公司交易算法"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('HandlePositionAlgoID', c_char * 1)  # 持仓处理算法编号
        , ('FindMarginRateAlgoID', c_char * 1)  # 寻找保证金率算法编号
        , ('HandleTradingAccountAlgoID', c_char * 1)  # 资金处理算法编号
    ]

    def __init__(self, BrokerID='', ExchangeID='', InstrumentID='', HandlePositionAlgoID='', FindMarginRateAlgoID='', HandleTradingAccountAlgoID=''):
        super(BrokerTradingAlgosField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.HandlePositionAlgoID = self._to_bytes(HandlePositionAlgoID)
        self.FindMarginRateAlgoID = self._to_bytes(FindMarginRateAlgoID)
        self.HandleTradingAccountAlgoID = self._to_bytes(HandleTradingAccountAlgoID)


class QueryBrokerDepositField(BaseField):
    """查询经纪公司资金"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, BrokerID='', ExchangeID=''):
        super(QueryBrokerDepositField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class BrokerDepositField(BaseField):
    """经纪公司资金"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日期
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('ParticipantID', c_char * 11)  # 会员代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('PreBalance', c_double)  # 上次结算准备金
        , ('CurrMargin', c_double)  # 当前保证金总额
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('Balance', c_double)  # 期货结算准备金
        , ('Deposit', c_double)  # 入金金额
        , ('Withdraw', c_double)  # 出金金额
        , ('Available', c_double)  # 可提资金
        , ('Reserve', c_double)  # 基本准备金
        , ('FrozenMargin', c_double)  # 冻结的保证金
    ]

    def __init__(self, TradingDay='', BrokerID='', ParticipantID='', ExchangeID='', PreBalance=0.0, CurrMargin=0.0, CloseProfit=0.0, Balance=0.0, Deposit=0.0, Withdraw=0.0, Available=0.0, Reserve=0.0, FrozenMargin=0.0):
        super(BrokerDepositField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.PreBalance = float(PreBalance)
        self.CurrMargin = float(CurrMargin)
        self.CloseProfit = float(CloseProfit)
        self.Balance = float(Balance)
        self.Deposit = float(Deposit)
        self.Withdraw = float(Withdraw)
        self.Available = float(Available)
        self.Reserve = float(Reserve)
        self.FrozenMargin = float(FrozenMargin)


class QryCFMMCBrokerKeyField(BaseField):
    """查询保证金监管系统经纪公司密钥"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
    ]

    def __init__(self, BrokerID=''):
        super(QryCFMMCBrokerKeyField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)


class CFMMCBrokerKeyField(BaseField):
    """保证金监管系统经纪公司密钥"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ParticipantID', c_char * 11)  # 经纪公司统一编码
        , ('CreateDate', c_char * 9)  # 密钥生成日期
        , ('CreateTime', c_char * 9)  # 密钥生成时间
        , ('KeyID', c_int)  # 密钥编号
        , ('CurrentKey', c_char * 21)  # 动态密钥
        , ('KeyKind', c_char * 1)  # 动态密钥类型
    ]

    def __init__(self, BrokerID='', ParticipantID='', CreateDate='', CreateTime='', KeyID=0, CurrentKey='', KeyKind=''):
        super(CFMMCBrokerKeyField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.CreateDate = self._to_bytes(CreateDate)
        self.CreateTime = self._to_bytes(CreateTime)
        self.KeyID = int(KeyID)
        self.CurrentKey = self._to_bytes(CurrentKey)
        self.KeyKind = self._to_bytes(KeyKind)


class CFMMCTradingAccountKeyField(BaseField):
    """保证金监管系统经纪公司资金账户密钥"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ParticipantID', c_char * 11)  # 经纪公司统一编码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('KeyID', c_int)  # 密钥编号
        , ('CurrentKey', c_char * 21)  # 动态密钥
    ]

    def __init__(self, BrokerID='', ParticipantID='', AccountID='', KeyID=0, CurrentKey=''):
        super(CFMMCTradingAccountKeyField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.AccountID = self._to_bytes(AccountID)
        self.KeyID = int(KeyID)
        self.CurrentKey = self._to_bytes(CurrentKey)


class QryCFMMCTradingAccountKeyField(BaseField):
    """请求查询保证金监管系统经纪公司资金账户密钥"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QryCFMMCTradingAccountKeyField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class BrokerUserOTPParamField(BaseField):
    """用户动态令牌参数"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('OTPVendorsID', c_char * 2)  # 动态令牌提供商
        , ('SerialNumber', c_char * 17)  # 动态令牌序列号
        , ('AuthKey', c_char * 41)  # 令牌密钥
        , ('LastDrift', c_int)  # 漂移值
        , ('LastSuccess', c_int)  # 成功值
        , ('OTPType', c_char * 1)  # 动态令牌类型
    ]

    def __init__(self, BrokerID='', UserID='', OTPVendorsID='', SerialNumber='', AuthKey='', LastDrift=0, LastSuccess=0, OTPType=''):
        super(BrokerUserOTPParamField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.OTPVendorsID = self._to_bytes(OTPVendorsID)
        self.SerialNumber = self._to_bytes(SerialNumber)
        self.AuthKey = self._to_bytes(AuthKey)
        self.LastDrift = int(LastDrift)
        self.LastSuccess = int(LastSuccess)
        self.OTPType = self._to_bytes(OTPType)


class ManualSyncBrokerUserOTPField(BaseField):
    """手工同步用户动态令牌"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('OTPType', c_char * 1)  # 动态令牌类型
        , ('FirstOTP', c_char * 41)  # 第一个动态密码
        , ('SecondOTP', c_char * 41)  # 第二个动态密码
    ]

    def __init__(self, BrokerID='', UserID='', OTPType='', FirstOTP='', SecondOTP=''):
        super(ManualSyncBrokerUserOTPField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.OTPType = self._to_bytes(OTPType)
        self.FirstOTP = self._to_bytes(FirstOTP)
        self.SecondOTP = self._to_bytes(SecondOTP)


class CommRateModelField(BaseField):
    """投资者手续费率模板"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('CommModelID', c_char * 13)  # 手续费率模板代码
        , ('CommModelName', c_char * 161)  # 模板名称
    ]

    def __init__(self, BrokerID='', CommModelID='', CommModelName=''):
        super(CommRateModelField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.CommModelID = self._to_bytes(CommModelID)
        self.CommModelName = self._to_bytes(CommModelName)


class QryCommRateModelField(BaseField):
    """请求查询投资者手续费率模板"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('CommModelID', c_char * 13)  # 手续费率模板代码
    ]

    def __init__(self, BrokerID='', CommModelID=''):
        super(QryCommRateModelField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.CommModelID = self._to_bytes(CommModelID)


class MarginModelField(BaseField):
    """投资者保证金率模板"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('MarginModelID', c_char * 13)  # 保证金率模板代码
        , ('MarginModelName', c_char * 161)  # 模板名称
    ]

    def __init__(self, BrokerID='', MarginModelID='', MarginModelName=''):
        super(MarginModelField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.MarginModelID = self._to_bytes(MarginModelID)
        self.MarginModelName = self._to_bytes(MarginModelName)


class QryMarginModelField(BaseField):
    """请求查询投资者保证金率模板"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('MarginModelID', c_char * 13)  # 保证金率模板代码
    ]

    def __init__(self, BrokerID='', MarginModelID=''):
        super(QryMarginModelField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.MarginModelID = self._to_bytes(MarginModelID)


class EWarrantOffsetField(BaseField):
    """仓单折抵信息"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日期
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('Direction', c_char * 1)  # 买卖方向
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('Volume', c_int)  # 数量
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, TradingDay='', BrokerID='', InvestorID='', ExchangeID='', InstrumentID='', Direction='', HedgeFlag='', Volume=0, InvestUnitID=''):
        super(EWarrantOffsetField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.Direction = self._to_bytes(Direction)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.Volume = int(Volume)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryEWarrantOffsetField(BaseField):
    """查询仓单折抵信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InstrumentID', c_char * 31)  # 合约代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ExchangeID='', InstrumentID='', InvestUnitID=''):
        super(QryEWarrantOffsetField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InstrumentID = self._to_bytes(InstrumentID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QryInvestorProductGroupMarginField(BaseField):
    """查询投资者品种/跨品种保证金"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('ProductGroupID', c_char * 31)  # 品种/跨品种标示
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', ProductGroupID='', HedgeFlag='', ExchangeID='', InvestUnitID=''):
        super(QryInvestorProductGroupMarginField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.ProductGroupID = self._to_bytes(ProductGroupID)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class InvestorProductGroupMarginField(BaseField):
    """投资者品种/跨品种保证金"""
    _fields_ = [
        ('ProductGroupID', c_char * 31)  # ///品种/跨品种标示
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('TradingDay', c_char * 9)  # 交易日
        , ('SettlementID', c_int)  # 结算编号
        , ('FrozenMargin', c_double)  # 冻结的保证金
        , ('LongFrozenMargin', c_double)  # 多头冻结的保证金
        , ('ShortFrozenMargin', c_double)  # 空头冻结的保证金
        , ('UseMargin', c_double)  # 占用的保证金
        , ('LongUseMargin', c_double)  # 多头保证金
        , ('ShortUseMargin', c_double)  # 空头保证金
        , ('ExchMargin', c_double)  # 交易所保证金
        , ('LongExchMargin', c_double)  # 交易所多头保证金
        , ('ShortExchMargin', c_double)  # 交易所空头保证金
        , ('CloseProfit', c_double)  # 平仓盈亏
        , ('FrozenCommission', c_double)  # 冻结的手续费
        , ('Commission', c_double)  # 手续费
        , ('FrozenCash', c_double)  # 冻结的资金
        , ('CashIn', c_double)  # 资金差额
        , ('PositionProfit', c_double)  # 持仓盈亏
        , ('OffsetAmount', c_double)  # 折抵总金额
        , ('LongOffsetAmount', c_double)  # 多头折抵总金额
        , ('ShortOffsetAmount', c_double)  # 空头折抵总金额
        , ('ExchOffsetAmount', c_double)  # 交易所折抵总金额
        , ('LongExchOffsetAmount', c_double)  # 交易所多头折抵总金额
        , ('ShortExchOffsetAmount', c_double)  # 交易所空头折抵总金额
        , ('HedgeFlag', c_char * 1)  # 投机套保标志
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, ProductGroupID='', BrokerID='', InvestorID='', TradingDay='', SettlementID=0, FrozenMargin=0.0, LongFrozenMargin=0.0, ShortFrozenMargin=0.0, UseMargin=0.0, LongUseMargin=0.0, ShortUseMargin=0.0,
                 ExchMargin=0.0, LongExchMargin=0.0, ShortExchMargin=0.0, CloseProfit=0.0, FrozenCommission=0.0, Commission=0.0, FrozenCash=0.0, CashIn=0.0, PositionProfit=0.0, OffsetAmount=0.0, LongOffsetAmount=0.0,
                 ShortOffsetAmount=0.0, ExchOffsetAmount=0.0, LongExchOffsetAmount=0.0, ShortExchOffsetAmount=0.0, HedgeFlag='', ExchangeID='', InvestUnitID=''):
        super(InvestorProductGroupMarginField, self).__init__()

        self.ProductGroupID = self._to_bytes(ProductGroupID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.TradingDay = self._to_bytes(TradingDay)
        self.SettlementID = int(SettlementID)
        self.FrozenMargin = float(FrozenMargin)
        self.LongFrozenMargin = float(LongFrozenMargin)
        self.ShortFrozenMargin = float(ShortFrozenMargin)
        self.UseMargin = float(UseMargin)
        self.LongUseMargin = float(LongUseMargin)
        self.ShortUseMargin = float(ShortUseMargin)
        self.ExchMargin = float(ExchMargin)
        self.LongExchMargin = float(LongExchMargin)
        self.ShortExchMargin = float(ShortExchMargin)
        self.CloseProfit = float(CloseProfit)
        self.FrozenCommission = float(FrozenCommission)
        self.Commission = float(Commission)
        self.FrozenCash = float(FrozenCash)
        self.CashIn = float(CashIn)
        self.PositionProfit = float(PositionProfit)
        self.OffsetAmount = float(OffsetAmount)
        self.LongOffsetAmount = float(LongOffsetAmount)
        self.ShortOffsetAmount = float(ShortOffsetAmount)
        self.ExchOffsetAmount = float(ExchOffsetAmount)
        self.LongExchOffsetAmount = float(LongExchOffsetAmount)
        self.ShortExchOffsetAmount = float(ShortExchOffsetAmount)
        self.HedgeFlag = self._to_bytes(HedgeFlag)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class QueryCFMMCTradingAccountTokenField(BaseField):
    """查询监控中心用户令牌"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('InvestUnitID', c_char * 17)  # 投资单元代码
    ]

    def __init__(self, BrokerID='', InvestorID='', InvestUnitID=''):
        super(QueryCFMMCTradingAccountTokenField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.InvestUnitID = self._to_bytes(InvestUnitID)


class CFMMCTradingAccountTokenField(BaseField):
    """监控中心用户令牌"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('ParticipantID', c_char * 11)  # 经纪公司统一编码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('KeyID', c_int)  # 密钥编号
        , ('Token', c_char * 21)  # 动态令牌
    ]

    def __init__(self, BrokerID='', ParticipantID='', AccountID='', KeyID=0, Token=''):
        super(CFMMCTradingAccountTokenField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.ParticipantID = self._to_bytes(ParticipantID)
        self.AccountID = self._to_bytes(AccountID)
        self.KeyID = int(KeyID)
        self.Token = self._to_bytes(Token)


class QryProductGroupField(BaseField):
    """查询产品组"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
    ]

    def __init__(self, ProductID='', ExchangeID=''):
        super(QryProductGroupField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.ExchangeID = self._to_bytes(ExchangeID)


class ProductGroupField(BaseField):
    """投资者品种/跨品种保证金产品组"""
    _fields_ = [
        ('ProductID', c_char * 31)  # ///产品代码
        , ('ExchangeID', c_char * 9)  # 交易所代码
        , ('ProductGroupID', c_char * 31)  # 产品组代码
    ]

    def __init__(self, ProductID='', ExchangeID='', ProductGroupID=''):
        super(ProductGroupField, self).__init__()

        self.ProductID = self._to_bytes(ProductID)
        self.ExchangeID = self._to_bytes(ExchangeID)
        self.ProductGroupID = self._to_bytes(ProductGroupID)


class BulletinField(BaseField):
    """交易所公告"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('TradingDay', c_char * 9)  # 交易日
        , ('BulletinID', c_int)  # 公告编号
        , ('SequenceNo', c_int)  # 序列号
        , ('NewsType', c_char * 3)  # 公告类型
        , ('NewsUrgency', c_char * 1)  # 紧急程度
        , ('SendTime', c_char * 9)  # 发送时间
        , ('Abstract', c_char * 81)  # 消息摘要
        , ('ComeFrom', c_char * 21)  # 消息来源
        , ('Content', c_char * 501)  # 消息正文
        , ('URLLink', c_char * 201)  # WEB地址
        , ('MarketID', c_char * 31)  # 市场代码
    ]

    def __init__(self, ExchangeID='', TradingDay='', BulletinID=0, SequenceNo=0, NewsType='', NewsUrgency='', SendTime='', Abstract='', ComeFrom='', Content='', URLLink='', MarketID=''):
        super(BulletinField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.TradingDay = self._to_bytes(TradingDay)
        self.BulletinID = int(BulletinID)
        self.SequenceNo = int(SequenceNo)
        self.NewsType = self._to_bytes(NewsType)
        self.NewsUrgency = self._to_bytes(NewsUrgency)
        self.SendTime = self._to_bytes(SendTime)
        self.Abstract = self._to_bytes(Abstract)
        self.ComeFrom = self._to_bytes(ComeFrom)
        self.Content = self._to_bytes(Content)
        self.URLLink = self._to_bytes(URLLink)
        self.MarketID = self._to_bytes(MarketID)


class QryBulletinField(BaseField):
    """查询交易所公告"""
    _fields_ = [
        ('ExchangeID', c_char * 9)  # ///交易所代码
        , ('BulletinID', c_int)  # 公告编号
        , ('SequenceNo', c_int)  # 序列号
        , ('NewsType', c_char * 3)  # 公告类型
        , ('NewsUrgency', c_char * 1)  # 紧急程度
    ]

    def __init__(self, ExchangeID='', BulletinID=0, SequenceNo=0, NewsType='', NewsUrgency=''):
        super(QryBulletinField, self).__init__()

        self.ExchangeID = self._to_bytes(ExchangeID)
        self.BulletinID = int(BulletinID)
        self.SequenceNo = int(SequenceNo)
        self.NewsType = self._to_bytes(NewsType)
        self.NewsUrgency = self._to_bytes(NewsUrgency)


class ReqOpenAccountField(BaseField):
    """转帐开户请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('CashExchangeCode', c_char * 1)  # 汇钞标志
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('TID', c_int)  # 交易ID
        , ('UserID', c_char * 16)  # 用户标识
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 AccountID='', Password='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', CashExchangeCode='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='',
                 BankPwdFlag='', SecuPwdFlag='', OperNo='', TID=0, UserID='', LongCustomerName=''):
        super(ReqOpenAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.CashExchangeCode = self._to_bytes(CashExchangeCode)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.TID = int(TID)
        self.UserID = self._to_bytes(UserID)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ReqCancelAccountField(BaseField):
    """转帐销户请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('CashExchangeCode', c_char * 1)  # 汇钞标志
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('TID', c_int)  # 交易ID
        , ('UserID', c_char * 16)  # 用户标识
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 AccountID='', Password='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', CashExchangeCode='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='',
                 BankPwdFlag='', SecuPwdFlag='', OperNo='', TID=0, UserID='', LongCustomerName=''):
        super(ReqCancelAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.CashExchangeCode = self._to_bytes(CashExchangeCode)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.TID = int(TID)
        self.UserID = self._to_bytes(UserID)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ReqChangeAccountField(BaseField):
    """变更银行账户请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('NewBankAccount', c_char * 41)  # 新银行帐号
        , ('NewBankPassWord', c_char * 41)  # 新银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('TID', c_int)  # 交易ID
        , ('Digest', c_char * 36)  # 摘要
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 NewBankAccount='', NewBankPassWord='', AccountID='', Password='', BankAccType='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', BrokerIDByBank='', BankPwdFlag='', SecuPwdFlag='', TID=0, Digest='',
                 LongCustomerName=''):
        super(ReqChangeAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.NewBankAccount = self._to_bytes(NewBankAccount)
        self.NewBankPassWord = self._to_bytes(NewBankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.BankAccType = self._to_bytes(BankAccType)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.TID = int(TID)
        self.Digest = self._to_bytes(Digest)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ReqTransferField(BaseField):
    """转账请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('FutureFetchAmount', c_double)  # 期货可取金额
        , ('FeePayFlag', c_char * 1)  # 费用支付标志
        , ('CustFee', c_double)  # 应收客户费用
        , ('BrokerFee', c_double)  # 应收期货公司费用
        , ('Message', c_char * 129)  # 发送方给接收方的消息
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('TransferStatus', c_char * 1)  # 转账交易状态
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', InstallID=0, FutureSerial=0, UserID='', VerifyCertNoFlag='', CurrencyID='', TradeAmount=0.0,
                 FutureFetchAmount=0.0, FeePayFlag='', CustFee=0.0, BrokerFee=0.0, Message='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='',
                 OperNo='', RequestID=0, TID=0, TransferStatus='', LongCustomerName=''):
        super(ReqTransferField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.FutureSerial = int(FutureSerial)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.FutureFetchAmount = float(FutureFetchAmount)
        self.FeePayFlag = self._to_bytes(FeePayFlag)
        self.CustFee = float(CustFee)
        self.BrokerFee = float(BrokerFee)
        self.Message = self._to_bytes(Message)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.TransferStatus = self._to_bytes(TransferStatus)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class RspTransferField(BaseField):
    """银行发起银行资金转期货响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('FutureFetchAmount', c_double)  # 期货可取金额
        , ('FeePayFlag', c_char * 1)  # 费用支付标志
        , ('CustFee', c_double)  # 应收客户费用
        , ('BrokerFee', c_double)  # 应收期货公司费用
        , ('Message', c_char * 129)  # 发送方给接收方的消息
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('TransferStatus', c_char * 1)  # 转账交易状态
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', InstallID=0, FutureSerial=0, UserID='', VerifyCertNoFlag='', CurrencyID='', TradeAmount=0.0,
                 FutureFetchAmount=0.0, FeePayFlag='', CustFee=0.0, BrokerFee=0.0, Message='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='',
                 OperNo='', RequestID=0, TID=0, TransferStatus='', ErrorID=0, ErrorMsg='', LongCustomerName=''):
        super(RspTransferField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.FutureSerial = int(FutureSerial)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.FutureFetchAmount = float(FutureFetchAmount)
        self.FeePayFlag = self._to_bytes(FeePayFlag)
        self.CustFee = float(CustFee)
        self.BrokerFee = float(BrokerFee)
        self.Message = self._to_bytes(Message)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.TransferStatus = self._to_bytes(TransferStatus)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ReqRepealField(BaseField):
    """冲正请求"""
    _fields_ = [
        ('RepealTimeInterval', c_int)  # ///冲正时间间隔
        , ('RepealedTimes', c_int)  # 已经冲正次数
        , ('BankRepealFlag', c_char * 1)  # 银行冲正标志
        , ('BrokerRepealFlag', c_char * 1)  # 期商冲正标志
        , ('PlateRepealSerial', c_int)  # 被冲正平台流水号
        , ('BankRepealSerial', c_char * 13)  # 被冲正银行流水号
        , ('FutureRepealSerial', c_int)  # 被冲正期货流水号
        , ('TradeCode', c_char * 7)  # 业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('FutureFetchAmount', c_double)  # 期货可取金额
        , ('FeePayFlag', c_char * 1)  # 费用支付标志
        , ('CustFee', c_double)  # 应收客户费用
        , ('BrokerFee', c_double)  # 应收期货公司费用
        , ('Message', c_char * 129)  # 发送方给接收方的消息
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('TransferStatus', c_char * 1)  # 转账交易状态
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, RepealTimeInterval=0, RepealedTimes=0, BankRepealFlag='', BrokerRepealFlag='', PlateRepealSerial=0, BankRepealSerial='', FutureRepealSerial=0, TradeCode='', BankID='', BankBranchID='', BrokerID='',
                 BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='', IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='',
                 BankPassWord='', AccountID='', Password='', InstallID=0, FutureSerial=0, UserID='', VerifyCertNoFlag='', CurrencyID='', TradeAmount=0.0, FutureFetchAmount=0.0, FeePayFlag='', CustFee=0.0, BrokerFee=0.0,
                 Message='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='', OperNo='', RequestID=0, TID=0, TransferStatus='',
                 LongCustomerName=''):
        super(ReqRepealField, self).__init__()

        self.RepealTimeInterval = int(RepealTimeInterval)
        self.RepealedTimes = int(RepealedTimes)
        self.BankRepealFlag = self._to_bytes(BankRepealFlag)
        self.BrokerRepealFlag = self._to_bytes(BrokerRepealFlag)
        self.PlateRepealSerial = int(PlateRepealSerial)
        self.BankRepealSerial = self._to_bytes(BankRepealSerial)
        self.FutureRepealSerial = int(FutureRepealSerial)
        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.FutureSerial = int(FutureSerial)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.FutureFetchAmount = float(FutureFetchAmount)
        self.FeePayFlag = self._to_bytes(FeePayFlag)
        self.CustFee = float(CustFee)
        self.BrokerFee = float(BrokerFee)
        self.Message = self._to_bytes(Message)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.TransferStatus = self._to_bytes(TransferStatus)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class RspRepealField(BaseField):
    """冲正响应"""
    _fields_ = [
        ('RepealTimeInterval', c_int)  # ///冲正时间间隔
        , ('RepealedTimes', c_int)  # 已经冲正次数
        , ('BankRepealFlag', c_char * 1)  # 银行冲正标志
        , ('BrokerRepealFlag', c_char * 1)  # 期商冲正标志
        , ('PlateRepealSerial', c_int)  # 被冲正平台流水号
        , ('BankRepealSerial', c_char * 13)  # 被冲正银行流水号
        , ('FutureRepealSerial', c_int)  # 被冲正期货流水号
        , ('TradeCode', c_char * 7)  # 业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('FutureFetchAmount', c_double)  # 期货可取金额
        , ('FeePayFlag', c_char * 1)  # 费用支付标志
        , ('CustFee', c_double)  # 应收客户费用
        , ('BrokerFee', c_double)  # 应收期货公司费用
        , ('Message', c_char * 129)  # 发送方给接收方的消息
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('TransferStatus', c_char * 1)  # 转账交易状态
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, RepealTimeInterval=0, RepealedTimes=0, BankRepealFlag='', BrokerRepealFlag='', PlateRepealSerial=0, BankRepealSerial='', FutureRepealSerial=0, TradeCode='', BankID='', BankBranchID='', BrokerID='',
                 BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='', IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='',
                 BankPassWord='', AccountID='', Password='', InstallID=0, FutureSerial=0, UserID='', VerifyCertNoFlag='', CurrencyID='', TradeAmount=0.0, FutureFetchAmount=0.0, FeePayFlag='', CustFee=0.0, BrokerFee=0.0,
                 Message='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='', OperNo='', RequestID=0, TID=0, TransferStatus='', ErrorID=0,
                 ErrorMsg='', LongCustomerName=''):
        super(RspRepealField, self).__init__()

        self.RepealTimeInterval = int(RepealTimeInterval)
        self.RepealedTimes = int(RepealedTimes)
        self.BankRepealFlag = self._to_bytes(BankRepealFlag)
        self.BrokerRepealFlag = self._to_bytes(BrokerRepealFlag)
        self.PlateRepealSerial = int(PlateRepealSerial)
        self.BankRepealSerial = self._to_bytes(BankRepealSerial)
        self.FutureRepealSerial = int(FutureRepealSerial)
        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.FutureSerial = int(FutureSerial)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.FutureFetchAmount = float(FutureFetchAmount)
        self.FeePayFlag = self._to_bytes(FeePayFlag)
        self.CustFee = float(CustFee)
        self.BrokerFee = float(BrokerFee)
        self.Message = self._to_bytes(Message)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.TransferStatus = self._to_bytes(TransferStatus)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ReqQueryAccountField(BaseField):
    """查询账户信息请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', FutureSerial=0, InstallID=0, UserID='', VerifyCertNoFlag='', CurrencyID='', Digest='',
                 BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='', OperNo='', RequestID=0, TID=0, LongCustomerName=''):
        super(ReqQueryAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.FutureSerial = int(FutureSerial)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class RspQueryAccountField(BaseField):
    """查询账户信息响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('BankUseAmount', c_double)  # 银行可用金额
        , ('BankFetchAmount', c_double)  # 银行可取金额
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', FutureSerial=0, InstallID=0, UserID='', VerifyCertNoFlag='', CurrencyID='', Digest='',
                 BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='', OperNo='', RequestID=0, TID=0, BankUseAmount=0.0, BankFetchAmount=0.0,
                 LongCustomerName=''):
        super(RspQueryAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.FutureSerial = int(FutureSerial)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.BankUseAmount = float(BankUseAmount)
        self.BankFetchAmount = float(BankFetchAmount)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class FutureSignIOField(BaseField):
    """期商签到签退"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0):
        super(FutureSignIOField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)


class RspFutureSignInField(BaseField):
    """期商签到响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('PinKey', c_char * 129)  # PIN密钥
        , ('MacKey', c_char * 129)  # MAC密钥
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg='', PinKey='', MacKey=''):
        super(RspFutureSignInField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.PinKey = self._to_bytes(PinKey)
        self.MacKey = self._to_bytes(MacKey)


class ReqFutureSignOutField(BaseField):
    """期商签退请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0):
        super(ReqFutureSignOutField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)


class RspFutureSignOutField(BaseField):
    """期商签退响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg=''):
        super(RspFutureSignOutField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class ReqQueryTradeResultBySerialField(BaseField):
    """查询指定流水号的交易结果请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('Reference', c_int)  # 流水号
        , ('RefrenceIssureType', c_char * 1)  # 本流水号发布者的机构类型
        , ('RefrenceIssure', c_char * 36)  # 本流水号发布者机构编码
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('Digest', c_char * 36)  # 摘要
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, Reference=0,
                 RefrenceIssureType='', RefrenceIssure='', CustomerName='', IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', CurrencyID='', TradeAmount=0.0,
                 Digest='', LongCustomerName=''):
        super(ReqQueryTradeResultBySerialField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.Reference = int(Reference)
        self.RefrenceIssureType = self._to_bytes(RefrenceIssureType)
        self.RefrenceIssure = self._to_bytes(RefrenceIssure)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.Digest = self._to_bytes(Digest)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class RspQueryTradeResultBySerialField(BaseField):
    """查询指定流水号的交易结果响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('Reference', c_int)  # 流水号
        , ('RefrenceIssureType', c_char * 1)  # 本流水号发布者的机构类型
        , ('RefrenceIssure', c_char * 36)  # 本流水号发布者机构编码
        , ('OriginReturnCode', c_char * 7)  # 原始返回代码
        , ('OriginDescrInfoForReturnCode', c_char * 129)  # 原始返回码描述
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 转帐金额
        , ('Digest', c_char * 36)  # 摘要
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, ErrorID=0,
                 ErrorMsg='', Reference=0, RefrenceIssureType='', RefrenceIssure='', OriginReturnCode='', OriginDescrInfoForReturnCode='', BankAccount='', BankPassWord='', AccountID='', Password='', CurrencyID='',
                 TradeAmount=0.0, Digest=''):
        super(RspQueryTradeResultBySerialField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.Reference = int(Reference)
        self.RefrenceIssureType = self._to_bytes(RefrenceIssureType)
        self.RefrenceIssure = self._to_bytes(RefrenceIssure)
        self.OriginReturnCode = self._to_bytes(OriginReturnCode)
        self.OriginDescrInfoForReturnCode = self._to_bytes(OriginDescrInfoForReturnCode)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.Digest = self._to_bytes(Digest)


class ReqDayEndFileReadyField(BaseField):
    """日终文件就绪请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('FileBusinessCode', c_char * 1)  # 文件业务功能
        , ('Digest', c_char * 36)  # 摘要
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, FileBusinessCode='',
                 Digest=''):
        super(ReqDayEndFileReadyField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.FileBusinessCode = self._to_bytes(FileBusinessCode)
        self.Digest = self._to_bytes(Digest)


class ReturnResultField(BaseField):
    """返回结果"""
    _fields_ = [
        ('ReturnCode', c_char * 7)  # ///返回代码
        , ('DescrInfoForReturnCode', c_char * 129)  # 返回码描述
    ]

    def __init__(self, ReturnCode='', DescrInfoForReturnCode=''):
        super(ReturnResultField, self).__init__()

        self.ReturnCode = self._to_bytes(ReturnCode)
        self.DescrInfoForReturnCode = self._to_bytes(DescrInfoForReturnCode)


class VerifyFuturePasswordField(BaseField):
    """验证期货资金密码"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('InstallID', c_int)  # 安装编号
        , ('TID', c_int)  # 交易ID
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, AccountID='',
                 Password='', BankAccount='', BankPassWord='', InstallID=0, TID=0, CurrencyID=''):
        super(VerifyFuturePasswordField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.InstallID = int(InstallID)
        self.TID = int(TID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class VerifyCustInfoField(BaseField):
    """验证客户信息"""
    _fields_ = [
        ('CustomerName', c_char * 51)  # ///客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, CustomerName='', IdCardType='', IdentifiedCardNo='', CustType='', LongCustomerName=''):
        super(VerifyCustInfoField, self).__init__()

        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class VerifyFuturePasswordAndCustInfoField(BaseField):
    """验证期货资金密码和客户信息"""
    _fields_ = [
        ('CustomerName', c_char * 51)  # ///客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, CustomerName='', IdCardType='', IdentifiedCardNo='', CustType='', AccountID='', Password='', CurrencyID='', LongCustomerName=''):
        super(VerifyFuturePasswordAndCustInfoField, self).__init__()

        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class DepositResultInformField(BaseField):
    """验证期货资金密码和客户信息"""
    _fields_ = [
        ('DepositSeqNo', c_char * 15)  # ///出入金流水号，该流水号为银期报盘返回的流水号
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('Deposit', c_double)  # 入金金额
        , ('RequestID', c_int)  # 请求编号
        , ('ReturnCode', c_char * 7)  # 返回代码
        , ('DescrInfoForReturnCode', c_char * 129)  # 返回码描述
    ]

    def __init__(self, DepositSeqNo='', BrokerID='', InvestorID='', Deposit=0.0, RequestID=0, ReturnCode='', DescrInfoForReturnCode=''):
        super(DepositResultInformField, self).__init__()

        self.DepositSeqNo = self._to_bytes(DepositSeqNo)
        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.Deposit = float(Deposit)
        self.RequestID = int(RequestID)
        self.ReturnCode = self._to_bytes(ReturnCode)
        self.DescrInfoForReturnCode = self._to_bytes(DescrInfoForReturnCode)


class ReqSyncKeyField(BaseField):
    """交易核心向银期报盘发出密钥同步请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Message', c_char * 129)  # 交易核心给银期报盘的消息
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Message='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0):
        super(ReqSyncKeyField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Message = self._to_bytes(Message)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)


class RspSyncKeyField(BaseField):
    """交易核心向银期报盘发出密钥同步响应"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Message', c_char * 129)  # 交易核心给银期报盘的消息
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Message='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg=''):
        super(RspSyncKeyField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Message = self._to_bytes(Message)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class NotifyQueryAccountField(BaseField):
    """查询账户信息通知"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('BankUseAmount', c_double)  # 银行可用金额
        , ('BankFetchAmount', c_double)  # 银行可取金额
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', CustType='', BankAccount='', BankPassWord='', AccountID='', Password='', FutureSerial=0, InstallID=0, UserID='', VerifyCertNoFlag='', CurrencyID='', Digest='',
                 BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='', BankPwdFlag='', SecuPwdFlag='', OperNo='', RequestID=0, TID=0, BankUseAmount=0.0, BankFetchAmount=0.0, ErrorID=0,
                 ErrorMsg='', LongCustomerName=''):
        super(NotifyQueryAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustType = self._to_bytes(CustType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.FutureSerial = int(FutureSerial)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.BankUseAmount = float(BankUseAmount)
        self.BankFetchAmount = float(BankFetchAmount)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class TransferSerialField(BaseField):
    """银期转账交易流水表"""
    _fields_ = [
        ('PlateSerial', c_int)  # ///平台流水号
        , ('TradeDate', c_char * 9)  # 交易发起方日期
        , ('TradingDay', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('TradeCode', c_char * 7)  # 交易代码
        , ('SessionID', c_int)  # 会话编号
        , ('BankID', c_char * 4)  # 银行编码
        , ('BankBranchID', c_char * 5)  # 银行分支机构编码
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('BrokerID', c_char * 11)  # 期货公司编码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('FutureAccType', c_char * 1)  # 期货公司帐号类型
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('InvestorID', c_char * 13)  # 投资者代码
        , ('FutureSerial', c_int)  # 期货公司流水号
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('TradeAmount', c_double)  # 交易金额
        , ('CustFee', c_double)  # 应收客户费用
        , ('BrokerFee', c_double)  # 应收期货公司费用
        , ('AvailabilityFlag', c_char * 1)  # 有效标志
        , ('OperatorCode', c_char * 17)  # 操作员
        , ('BankNewAccount', c_char * 41)  # 新银行帐号
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, PlateSerial=0, TradeDate='', TradingDay='', TradeTime='', TradeCode='', SessionID=0, BankID='', BankBranchID='', BankAccType='', BankAccount='', BankSerial='', BrokerID='', BrokerBranchID='',
                 FutureAccType='', AccountID='', InvestorID='', FutureSerial=0, IdCardType='', IdentifiedCardNo='', CurrencyID='', TradeAmount=0.0, CustFee=0.0, BrokerFee=0.0, AvailabilityFlag='', OperatorCode='',
                 BankNewAccount='', ErrorID=0, ErrorMsg=''):
        super(TransferSerialField, self).__init__()

        self.PlateSerial = int(PlateSerial)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradingDay = self._to_bytes(TradingDay)
        self.TradeTime = self._to_bytes(TradeTime)
        self.TradeCode = self._to_bytes(TradeCode)
        self.SessionID = int(SessionID)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BankAccType = self._to_bytes(BankAccType)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankSerial = self._to_bytes(BankSerial)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.FutureAccType = self._to_bytes(FutureAccType)
        self.AccountID = self._to_bytes(AccountID)
        self.InvestorID = self._to_bytes(InvestorID)
        self.FutureSerial = int(FutureSerial)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.TradeAmount = float(TradeAmount)
        self.CustFee = float(CustFee)
        self.BrokerFee = float(BrokerFee)
        self.AvailabilityFlag = self._to_bytes(AvailabilityFlag)
        self.OperatorCode = self._to_bytes(OperatorCode)
        self.BankNewAccount = self._to_bytes(BankNewAccount)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class QryTransferSerialField(BaseField):
    """请求查询转帐流水"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('BankID', c_char * 4)  # 银行编码
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', BankID='', CurrencyID=''):
        super(QryTransferSerialField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.BankID = self._to_bytes(BankID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class NotifyFutureSignInField(BaseField):
    """期商签到通知"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('PinKey', c_char * 129)  # PIN密钥
        , ('MacKey', c_char * 129)  # MAC密钥
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg='', PinKey='', MacKey=''):
        super(NotifyFutureSignInField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.PinKey = self._to_bytes(PinKey)
        self.MacKey = self._to_bytes(MacKey)


class NotifyFutureSignOutField(BaseField):
    """期商签退通知"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Digest', c_char * 36)  # 摘要
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Digest='', CurrencyID='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg=''):
        super(NotifyFutureSignOutField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Digest = self._to_bytes(Digest)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class NotifySyncKeyField(BaseField):
    """交易核心向银期报盘发出密钥同步处理结果的通知"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('InstallID', c_int)  # 安装编号
        , ('UserID', c_char * 16)  # 用户标识
        , ('Message', c_char * 129)  # 交易核心给银期报盘的消息
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('RequestID', c_int)  # 请求编号
        , ('TID', c_int)  # 交易ID
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, InstallID=0,
                 UserID='', Message='', DeviceID='', BrokerIDByBank='', OperNo='', RequestID=0, TID=0, ErrorID=0, ErrorMsg=''):
        super(NotifySyncKeyField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.InstallID = int(InstallID)
        self.UserID = self._to_bytes(UserID)
        self.Message = self._to_bytes(Message)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.OperNo = self._to_bytes(OperNo)
        self.RequestID = int(RequestID)
        self.TID = int(TID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class QryAccountregisterField(BaseField):
    """请求查询银期签约关系"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('BankID', c_char * 4)  # 银行编码
        , ('BankBranchID', c_char * 5)  # 银行分支机构编码
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', BankID='', BankBranchID='', CurrencyID=''):
        super(QryAccountregisterField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class AccountregisterField(BaseField):
    """客户开销户信息表"""
    _fields_ = [
        ('TradeDay', c_char * 9)  # ///交易日期
        , ('BankID', c_char * 4)  # 银行编码
        , ('BankBranchID', c_char * 5)  # 银行分支机构编码
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BrokerID', c_char * 11)  # 期货公司编码
        , ('BrokerBranchID', c_char * 31)  # 期货公司分支机构编码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('OpenOrDestroy', c_char * 1)  # 开销户类别
        , ('RegDate', c_char * 9)  # 签约日期
        , ('OutDate', c_char * 9)  # 解约日期
        , ('TID', c_int)  # 交易ID
        , ('CustType', c_char * 1)  # 客户类型
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeDay='', BankID='', BankBranchID='', BankAccount='', BrokerID='', BrokerBranchID='', AccountID='', IdCardType='', IdentifiedCardNo='', CustomerName='', CurrencyID='', OpenOrDestroy='',
                 RegDate='', OutDate='', TID=0, CustType='', BankAccType='', LongCustomerName=''):
        super(AccountregisterField, self).__init__()

        self.TradeDay = self._to_bytes(TradeDay)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.AccountID = self._to_bytes(AccountID)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.CustomerName = self._to_bytes(CustomerName)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.OpenOrDestroy = self._to_bytes(OpenOrDestroy)
        self.RegDate = self._to_bytes(RegDate)
        self.OutDate = self._to_bytes(OutDate)
        self.TID = int(TID)
        self.CustType = self._to_bytes(CustType)
        self.BankAccType = self._to_bytes(BankAccType)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class OpenAccountField(BaseField):
    """银期开户信息"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('CashExchangeCode', c_char * 1)  # 汇钞标志
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('TID', c_int)  # 交易ID
        , ('UserID', c_char * 16)  # 用户标识
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 AccountID='', Password='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', CashExchangeCode='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='',
                 BankPwdFlag='', SecuPwdFlag='', OperNo='', TID=0, UserID='', ErrorID=0, ErrorMsg='', LongCustomerName=''):
        super(OpenAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.CashExchangeCode = self._to_bytes(CashExchangeCode)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.TID = int(TID)
        self.UserID = self._to_bytes(UserID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class CancelAccountField(BaseField):
    """银期销户信息"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('CashExchangeCode', c_char * 1)  # 汇钞标志
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('DeviceID', c_char * 3)  # 渠道标志
        , ('BankSecuAccType', c_char * 1)  # 期货单位帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankSecuAcc', c_char * 41)  # 期货单位帐号
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('OperNo', c_char * 17)  # 交易柜员
        , ('TID', c_int)  # 交易ID
        , ('UserID', c_char * 16)  # 用户标识
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 AccountID='', Password='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', CashExchangeCode='', Digest='', BankAccType='', DeviceID='', BankSecuAccType='', BrokerIDByBank='', BankSecuAcc='',
                 BankPwdFlag='', SecuPwdFlag='', OperNo='', TID=0, UserID='', ErrorID=0, ErrorMsg='', LongCustomerName=''):
        super(CancelAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.CashExchangeCode = self._to_bytes(CashExchangeCode)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.DeviceID = self._to_bytes(DeviceID)
        self.BankSecuAccType = self._to_bytes(BankSecuAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankSecuAcc = self._to_bytes(BankSecuAcc)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.OperNo = self._to_bytes(OperNo)
        self.TID = int(TID)
        self.UserID = self._to_bytes(UserID)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class ChangeAccountField(BaseField):
    """银期变更银行账号信息"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 51)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('NewBankAccount', c_char * 41)  # 新银行帐号
        , ('NewBankPassWord', c_char * 41)  # 新银行密码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('BankPwdFlag', c_char * 1)  # 银行密码标志
        , ('SecuPwdFlag', c_char * 1)  # 期货资金密码核对标志
        , ('TID', c_int)  # 交易ID
        , ('Digest', c_char * 36)  # 摘要
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
        , ('LongCustomerName', c_char * 161)  # 长客户姓名
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 NewBankAccount='', NewBankPassWord='', AccountID='', Password='', BankAccType='', InstallID=0, VerifyCertNoFlag='', CurrencyID='', BrokerIDByBank='', BankPwdFlag='', SecuPwdFlag='', TID=0, Digest='',
                 ErrorID=0, ErrorMsg='', LongCustomerName=''):
        super(ChangeAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.NewBankAccount = self._to_bytes(NewBankAccount)
        self.NewBankPassWord = self._to_bytes(NewBankPassWord)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.BankAccType = self._to_bytes(BankAccType)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.BankPwdFlag = self._to_bytes(BankPwdFlag)
        self.SecuPwdFlag = self._to_bytes(SecuPwdFlag)
        self.TID = int(TID)
        self.Digest = self._to_bytes(Digest)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)
        self.LongCustomerName = self._to_bytes(LongCustomerName)


class SecAgentACIDMapField(BaseField):
    """二级代理操作员银期权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('AccountID', c_char * 13)  # 资金账户
        , ('CurrencyID', c_char * 4)  # 币种
        , ('BrokerSecAgentID', c_char * 13)  # 境外中介机构资金帐号
    ]

    def __init__(self, BrokerID='', UserID='', AccountID='', CurrencyID='', BrokerSecAgentID=''):
        super(SecAgentACIDMapField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.BrokerSecAgentID = self._to_bytes(BrokerSecAgentID)


class QrySecAgentACIDMapField(BaseField):
    """二级代理操作员银期权限查询"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('AccountID', c_char * 13)  # 资金账户
        , ('CurrencyID', c_char * 4)  # 币种
    ]

    def __init__(self, BrokerID='', UserID='', AccountID='', CurrencyID=''):
        super(QrySecAgentACIDMapField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.AccountID = self._to_bytes(AccountID)
        self.CurrencyID = self._to_bytes(CurrencyID)


class UserRightsAssignField(BaseField):
    """灾备中心交易权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///应用单元代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('DRIdentityID', c_int)  # 交易中心代码
    ]

    def __init__(self, BrokerID='', UserID='', DRIdentityID=0):
        super(UserRightsAssignField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.DRIdentityID = int(DRIdentityID)


class BrokerUserRightAssignField(BaseField):
    """经济公司是否有在本标示的交易权限"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///应用单元代码
        , ('DRIdentityID', c_int)  # 交易中心代码
        , ('Tradeable', c_int)  # 能否交易
    ]

    def __init__(self, BrokerID='', DRIdentityID=0, Tradeable=0):
        super(BrokerUserRightAssignField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.DRIdentityID = int(DRIdentityID)
        self.Tradeable = int(Tradeable)


class DRTransferField(BaseField):
    """灾备交易转换报文"""
    _fields_ = [
        ('OrigDRIdentityID', c_int)  # ///原交易中心代码
        , ('DestDRIdentityID', c_int)  # 目标交易中心代码
        , ('OrigBrokerID', c_char * 11)  # 原应用单元代码
        , ('DestBrokerID', c_char * 11)  # 目标易用单元代码
    ]

    def __init__(self, OrigDRIdentityID=0, DestDRIdentityID=0, OrigBrokerID='', DestBrokerID=''):
        super(DRTransferField, self).__init__()

        self.OrigDRIdentityID = int(OrigDRIdentityID)
        self.DestDRIdentityID = int(DestDRIdentityID)
        self.OrigBrokerID = self._to_bytes(OrigBrokerID)
        self.DestBrokerID = self._to_bytes(DestBrokerID)


class FensUserInfoField(BaseField):
    """Fens用户信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('LoginMode', c_char * 1)  # 登录模式
    ]

    def __init__(self, BrokerID='', UserID='', LoginMode=''):
        super(FensUserInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.LoginMode = self._to_bytes(LoginMode)


class CurrTransferIdentityField(BaseField):
    """当前银期所属交易中心"""
    _fields_ = [
        ('IdentityID', c_int)  # ///交易中心代码
    ]

    def __init__(self, IdentityID=0):
        super(CurrTransferIdentityField, self).__init__()

        self.IdentityID = int(IdentityID)


class LoginForbiddenUserField(BaseField):
    """禁止登录用户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('IPAddress', c_char * 16)  # IP地址
    ]

    def __init__(self, BrokerID='', UserID='', IPAddress=''):
        super(LoginForbiddenUserField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.IPAddress = self._to_bytes(IPAddress)


class QryLoginForbiddenUserField(BaseField):
    """查询禁止登录用户"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(QryLoginForbiddenUserField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class MulticastGroupInfoField(BaseField):
    """UDP组播组信息"""
    _fields_ = [
        ('GroupIP', c_char * 16)  # ///组播组IP地址
        , ('GroupPort', c_int)  # 组播组IP端口
        , ('SourceIP', c_char * 16)  # 源地址
    ]

    def __init__(self, GroupIP='', GroupPort=0, SourceIP=''):
        super(MulticastGroupInfoField, self).__init__()

        self.GroupIP = self._to_bytes(GroupIP)
        self.GroupPort = int(GroupPort)
        self.SourceIP = self._to_bytes(SourceIP)


class TradingAccountReserveField(BaseField):
    """资金账户基本准备金"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Reserve', c_double)  # 基本准备金
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', Reserve=0.0, CurrencyID=''):
        super(TradingAccountReserveField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.Reserve = float(Reserve)
        self.CurrencyID = self._to_bytes(CurrencyID)


class QryLoginForbiddenIPField(BaseField):
    """查询禁止登录IP"""
    _fields_ = [
        ('IPAddress', c_char * 16)  # ///IP地址
    ]

    def __init__(self, IPAddress=''):
        super(QryLoginForbiddenIPField, self).__init__()

        self.IPAddress = self._to_bytes(IPAddress)


class QryIPListField(BaseField):
    """查询IP列表"""
    _fields_ = [
        ('IPAddress', c_char * 16)  # ///IP地址
    ]

    def __init__(self, IPAddress=''):
        super(QryIPListField, self).__init__()

        self.IPAddress = self._to_bytes(IPAddress)


class QryUserRightsAssignField(BaseField):
    """查询用户下单权限分配表"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///应用单元代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, BrokerID='', UserID=''):
        super(QryUserRightsAssignField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class ReserveOpenAccountConfirmField(BaseField):
    """银期预约开户确认请求"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 161)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('TID', c_int)  # 交易ID
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('Password', c_char * 41)  # 期货密码
        , ('BankReserveOpenSeq', c_char * 13)  # 预约开户银行流水号
        , ('BookDate', c_char * 9)  # 预约开户日期
        , ('BookPsw', c_char * 41)  # 预约开户验证密码
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 InstallID=0, VerifyCertNoFlag='', CurrencyID='', Digest='', BankAccType='', BrokerIDByBank='', TID=0, AccountID='', Password='', BankReserveOpenSeq='', BookDate='', BookPsw='', ErrorID=0, ErrorMsg=''):
        super(ReserveOpenAccountConfirmField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.TID = int(TID)
        self.AccountID = self._to_bytes(AccountID)
        self.Password = self._to_bytes(Password)
        self.BankReserveOpenSeq = self._to_bytes(BankReserveOpenSeq)
        self.BookDate = self._to_bytes(BookDate)
        self.BookPsw = self._to_bytes(BookPsw)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class ReserveOpenAccountField(BaseField):
    """银期预约开户"""
    _fields_ = [
        ('TradeCode', c_char * 7)  # ///业务功能码
        , ('BankID', c_char * 4)  # 银行代码
        , ('BankBranchID', c_char * 5)  # 银行分支机构代码
        , ('BrokerID', c_char * 11)  # 期商代码
        , ('BrokerBranchID', c_char * 31)  # 期商分支机构代码
        , ('TradeDate', c_char * 9)  # 交易日期
        , ('TradeTime', c_char * 9)  # 交易时间
        , ('BankSerial', c_char * 13)  # 银行流水号
        , ('TradingDay', c_char * 9)  # 交易系统日期
        , ('PlateSerial', c_int)  # 银期平台消息流水号
        , ('LastFragment', c_char * 1)  # 最后分片标志
        , ('SessionID', c_int)  # 会话号
        , ('CustomerName', c_char * 161)  # 客户姓名
        , ('IdCardType', c_char * 1)  # 证件类型
        , ('IdentifiedCardNo', c_char * 51)  # 证件号码
        , ('Gender', c_char * 1)  # 性别
        , ('CountryCode', c_char * 21)  # 国家代码
        , ('CustType', c_char * 1)  # 客户类型
        , ('Address', c_char * 101)  # 地址
        , ('ZipCode', c_char * 7)  # 邮编
        , ('Telephone', c_char * 41)  # 电话号码
        , ('MobilePhone', c_char * 21)  # 手机
        , ('Fax', c_char * 41)  # 传真
        , ('EMail', c_char * 41)  # 电子邮件
        , ('MoneyAccountStatus', c_char * 1)  # 资金账户状态
        , ('BankAccount', c_char * 41)  # 银行帐号
        , ('BankPassWord', c_char * 41)  # 银行密码
        , ('InstallID', c_int)  # 安装编号
        , ('VerifyCertNoFlag', c_char * 1)  # 验证客户证件号码标志
        , ('CurrencyID', c_char * 4)  # 币种代码
        , ('Digest', c_char * 36)  # 摘要
        , ('BankAccType', c_char * 1)  # 银行帐号类型
        , ('BrokerIDByBank', c_char * 33)  # 期货公司银行编码
        , ('TID', c_int)  # 交易ID
        , ('ReserveOpenAccStas', c_char * 1)  # 预约开户状态
        , ('ErrorID', c_int)  # 错误代码
        , ('ErrorMsg', c_char * 81)  # 错误信息
    ]

    def __init__(self, TradeCode='', BankID='', BankBranchID='', BrokerID='', BrokerBranchID='', TradeDate='', TradeTime='', BankSerial='', TradingDay='', PlateSerial=0, LastFragment='', SessionID=0, CustomerName='',
                 IdCardType='', IdentifiedCardNo='', Gender='', CountryCode='', CustType='', Address='', ZipCode='', Telephone='', MobilePhone='', Fax='', EMail='', MoneyAccountStatus='', BankAccount='', BankPassWord='',
                 InstallID=0, VerifyCertNoFlag='', CurrencyID='', Digest='', BankAccType='', BrokerIDByBank='', TID=0, ReserveOpenAccStas='', ErrorID=0, ErrorMsg=''):
        super(ReserveOpenAccountField, self).__init__()

        self.TradeCode = self._to_bytes(TradeCode)
        self.BankID = self._to_bytes(BankID)
        self.BankBranchID = self._to_bytes(BankBranchID)
        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerBranchID = self._to_bytes(BrokerBranchID)
        self.TradeDate = self._to_bytes(TradeDate)
        self.TradeTime = self._to_bytes(TradeTime)
        self.BankSerial = self._to_bytes(BankSerial)
        self.TradingDay = self._to_bytes(TradingDay)
        self.PlateSerial = int(PlateSerial)
        self.LastFragment = self._to_bytes(LastFragment)
        self.SessionID = int(SessionID)
        self.CustomerName = self._to_bytes(CustomerName)
        self.IdCardType = self._to_bytes(IdCardType)
        self.IdentifiedCardNo = self._to_bytes(IdentifiedCardNo)
        self.Gender = self._to_bytes(Gender)
        self.CountryCode = self._to_bytes(CountryCode)
        self.CustType = self._to_bytes(CustType)
        self.Address = self._to_bytes(Address)
        self.ZipCode = self._to_bytes(ZipCode)
        self.Telephone = self._to_bytes(Telephone)
        self.MobilePhone = self._to_bytes(MobilePhone)
        self.Fax = self._to_bytes(Fax)
        self.EMail = self._to_bytes(EMail)
        self.MoneyAccountStatus = self._to_bytes(MoneyAccountStatus)
        self.BankAccount = self._to_bytes(BankAccount)
        self.BankPassWord = self._to_bytes(BankPassWord)
        self.InstallID = int(InstallID)
        self.VerifyCertNoFlag = self._to_bytes(VerifyCertNoFlag)
        self.CurrencyID = self._to_bytes(CurrencyID)
        self.Digest = self._to_bytes(Digest)
        self.BankAccType = self._to_bytes(BankAccType)
        self.BrokerIDByBank = self._to_bytes(BrokerIDByBank)
        self.TID = int(TID)
        self.ReserveOpenAccStas = self._to_bytes(ReserveOpenAccStas)
        self.ErrorID = int(ErrorID)
        self.ErrorMsg = self._to_bytes(ErrorMsg)


class AccountPropertyField(BaseField):
    """银行账户属性"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('AccountID', c_char * 13)  # 投资者帐号
        , ('BankID', c_char * 4)  # 银行统一标识类型
        , ('BankAccount', c_char * 41)  # 银行账户
        , ('OpenName', c_char * 101)  # 银行账户的开户人名称
        , ('OpenBank', c_char * 101)  # 银行账户的开户行
        , ('IsActive', c_int)  # 是否活跃
        , ('AccountSourceType', c_char * 1)  # 账户来源
        , ('OpenDate', c_char * 9)  # 开户日期
        , ('CancelDate', c_char * 9)  # 注销日期
        , ('OperatorID', c_char * 65)  # 录入员代码
        , ('OperateDate', c_char * 9)  # 录入日期
        , ('OperateTime', c_char * 9)  # 录入时间
        , ('CurrencyID', c_char * 4)  # 币种代码
    ]

    def __init__(self, BrokerID='', AccountID='', BankID='', BankAccount='', OpenName='', OpenBank='', IsActive=0, AccountSourceType='', OpenDate='', CancelDate='', OperatorID='', OperateDate='', OperateTime='',
                 CurrencyID=''):
        super(AccountPropertyField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.AccountID = self._to_bytes(AccountID)
        self.BankID = self._to_bytes(BankID)
        self.BankAccount = self._to_bytes(BankAccount)
        self.OpenName = self._to_bytes(OpenName)
        self.OpenBank = self._to_bytes(OpenBank)
        self.IsActive = int(IsActive)
        self.AccountSourceType = self._to_bytes(AccountSourceType)
        self.OpenDate = self._to_bytes(OpenDate)
        self.CancelDate = self._to_bytes(CancelDate)
        self.OperatorID = self._to_bytes(OperatorID)
        self.OperateDate = self._to_bytes(OperateDate)
        self.OperateTime = self._to_bytes(OperateTime)
        self.CurrencyID = self._to_bytes(CurrencyID)


class QryCurrDRIdentityField(BaseField):
    """查询当前交易中心"""
    _fields_ = [
        ('DRIdentityID', c_int)  # ///交易中心代码
    ]

    def __init__(self, DRIdentityID=0):
        super(QryCurrDRIdentityField, self).__init__()

        self.DRIdentityID = int(DRIdentityID)


class CurrDRIdentityField(BaseField):
    """当前交易中心"""
    _fields_ = [
        ('DRIdentityID', c_int)  # ///交易中心代码
    ]

    def __init__(self, DRIdentityID=0):
        super(CurrDRIdentityField, self).__init__()

        self.DRIdentityID = int(DRIdentityID)


class QrySecAgentCheckModeField(BaseField):
    """查询二级代理商资金校验模式"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', InvestorID=''):
        super(QrySecAgentCheckModeField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.InvestorID = self._to_bytes(InvestorID)


class QrySecAgentTradeInfoField(BaseField):
    """查询二级代理商信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('BrokerSecAgentID', c_char * 13)  # 境外中介机构资金帐号
    ]

    def __init__(self, BrokerID='', BrokerSecAgentID=''):
        super(QrySecAgentTradeInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.BrokerSecAgentID = self._to_bytes(BrokerSecAgentID)


class UserSystemInfoField(BaseField):
    """用户系统信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('ClientSystemInfoLen', c_int)  # 用户端系统内部信息长度
        , ('ClientSystemInfo', c_char * 273)  # 用户端系统内部信息
        , ('ClientPublicIP', c_char * 16)  # 用户公网IP
        , ('ClientIPPort', c_int)  # 终端IP端口
        , ('ClientLoginTime', c_char * 9)  # 登录成功时间
        , ('ClientAppID', c_char * 33)  # App代码
    ]

    def __init__(self, BrokerID='', UserID='', ClientSystemInfoLen=0, ClientSystemInfo='', ClientPublicIP='', ClientIPPort=0, ClientLoginTime='', ClientAppID=''):
        super(UserSystemInfoField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.ClientSystemInfoLen = int(ClientSystemInfoLen)
        self.ClientSystemInfo = self._to_bytes(ClientSystemInfo)
        self.ClientPublicIP = self._to_bytes(ClientPublicIP)
        self.ClientIPPort = int(ClientIPPort)
        self.ClientLoginTime = self._to_bytes(ClientLoginTime)
        self.ClientAppID = self._to_bytes(ClientAppID)


class ReqUserAuthMethodField(BaseField):
    """用户发出获取安全安全登陆方法请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID=''):
        super(ReqUserAuthMethodField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class RspUserAuthMethodField(BaseField):
    """用户发出获取安全安全登陆方法回复"""
    _fields_ = [
        ('UsableAuthMethod', c_int)  # ///当前可以用的认证模式
    ]

    def __init__(self, UsableAuthMethod=0):
        super(RspUserAuthMethodField, self).__init__()

        self.UsableAuthMethod = int(UsableAuthMethod)


class ReqGenUserCaptchaField(BaseField):
    """用户发出获取安全安全登陆方法请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID=''):
        super(ReqGenUserCaptchaField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class RspGenUserCaptchaField(BaseField):
    """生成的图片验证码信息"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('CaptchaInfoLen', c_int)  # 图片信息长度
        , ('CaptchaInfo', c_char * 2561)  # 图片信息
    ]

    def __init__(self, BrokerID='', UserID='', CaptchaInfoLen=0, CaptchaInfo=''):
        super(RspGenUserCaptchaField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.CaptchaInfoLen = int(CaptchaInfoLen)
        self.CaptchaInfo = self._to_bytes(CaptchaInfo)


class ReqGenUserTextField(BaseField):
    """用户发出获取安全安全登陆方法请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID=''):
        super(ReqGenUserTextField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)


class RspGenUserTextField(BaseField):
    """短信验证码生成的回复"""
    _fields_ = [
        ('UserTextSeq', c_int)  # ///短信验证码序号
    ]

    def __init__(self, UserTextSeq=0):
        super(RspGenUserTextField, self).__init__()

        self.UserTextSeq = int(UserTextSeq)


class ReqUserLoginWithCaptchaField(BaseField):
    """用户发出带图形验证码的登录请求请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('Password', c_char * 41)  # 密码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ClientIPAddress', c_char * 16)  # 终端IP地址
        , ('LoginRemark', c_char * 36)  # 登录备注
        , ('Captcha', c_char * 41)  # 图形验证码的文字内容
        , ('ClientIPPort', c_int)  # 终端IP端口
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID='', Password='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', MacAddress='', ClientIPAddress='', LoginRemark='', Captcha='', ClientIPPort=0):
        super(ReqUserLoginWithCaptchaField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.Password = self._to_bytes(Password)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ClientIPAddress = self._to_bytes(ClientIPAddress)
        self.LoginRemark = self._to_bytes(LoginRemark)
        self.Captcha = self._to_bytes(Captcha)
        self.ClientIPPort = int(ClientIPPort)


class ReqUserLoginWithTextField(BaseField):
    """用户发出带短信验证码的登录请求请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('Password', c_char * 41)  # 密码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ClientIPAddress', c_char * 16)  # 终端IP地址
        , ('LoginRemark', c_char * 36)  # 登录备注
        , ('Text', c_char * 41)  # 短信验证码文字内容
        , ('ClientIPPort', c_int)  # 终端IP端口
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID='', Password='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', MacAddress='', ClientIPAddress='', LoginRemark='', Text='', ClientIPPort=0):
        super(ReqUserLoginWithTextField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.Password = self._to_bytes(Password)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ClientIPAddress = self._to_bytes(ClientIPAddress)
        self.LoginRemark = self._to_bytes(LoginRemark)
        self.Text = self._to_bytes(Text)
        self.ClientIPPort = int(ClientIPPort)


class ReqUserLoginWithOTPField(BaseField):
    """用户发出带动态验证码的登录请求请求"""
    _fields_ = [
        ('TradingDay', c_char * 9)  # ///交易日
        , ('BrokerID', c_char * 11)  # 经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('Password', c_char * 41)  # 密码
        , ('UserProductInfo', c_char * 11)  # 用户端产品信息
        , ('InterfaceProductInfo', c_char * 11)  # 接口端产品信息
        , ('ProtocolInfo', c_char * 11)  # 协议信息
        , ('MacAddress', c_char * 21)  # Mac地址
        , ('ClientIPAddress', c_char * 16)  # 终端IP地址
        , ('LoginRemark', c_char * 36)  # 登录备注
        , ('OTPPassword', c_char * 41)  # OTP密码
        , ('ClientIPPort', c_int)  # 终端IP端口
    ]

    def __init__(self, TradingDay='', BrokerID='', UserID='', Password='', UserProductInfo='', InterfaceProductInfo='', ProtocolInfo='', MacAddress='', ClientIPAddress='', LoginRemark='', OTPPassword='', ClientIPPort=0):
        super(ReqUserLoginWithOTPField, self).__init__()

        self.TradingDay = self._to_bytes(TradingDay)
        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.Password = self._to_bytes(Password)
        self.UserProductInfo = self._to_bytes(UserProductInfo)
        self.InterfaceProductInfo = self._to_bytes(InterfaceProductInfo)
        self.ProtocolInfo = self._to_bytes(ProtocolInfo)
        self.MacAddress = self._to_bytes(MacAddress)
        self.ClientIPAddress = self._to_bytes(ClientIPAddress)
        self.LoginRemark = self._to_bytes(LoginRemark)
        self.OTPPassword = self._to_bytes(OTPPassword)
        self.ClientIPPort = int(ClientIPPort)


class ReqApiHandshakeField(BaseField):
    """api握手请求"""
    _fields_ = [
        ('CryptoKeyVersion', c_char * 31)  # ///api与front通信密钥版本号
    ]

    def __init__(self, CryptoKeyVersion=''):
        super(ReqApiHandshakeField, self).__init__()

        self.CryptoKeyVersion = self._to_bytes(CryptoKeyVersion)


class RspApiHandshakeField(BaseField):
    """front发给api的握手回复"""
    _fields_ = [
        ('FrontHandshakeDataLen', c_int)  # ///握手回复数据长度
        , ('FrontHandshakeData', c_char * 301)  # 握手回复数据
        , ('IsApiAuthEnabled', c_int)  # API认证是否开启
    ]

    def __init__(self, FrontHandshakeDataLen=0, FrontHandshakeData='', IsApiAuthEnabled=0):
        super(RspApiHandshakeField, self).__init__()

        self.FrontHandshakeDataLen = int(FrontHandshakeDataLen)
        self.FrontHandshakeData = self._to_bytes(FrontHandshakeData)
        self.IsApiAuthEnabled = int(IsApiAuthEnabled)


class ReqVerifyApiKeyField(BaseField):
    """api给front的验证key的请求"""
    _fields_ = [
        ('ApiHandshakeDataLen', c_int)  # ///握手回复数据长度
        , ('ApiHandshakeData', c_char * 301)  # 握手回复数据
    ]

    def __init__(self, ApiHandshakeDataLen=0, ApiHandshakeData=''):
        super(ReqVerifyApiKeyField, self).__init__()

        self.ApiHandshakeDataLen = int(ApiHandshakeDataLen)
        self.ApiHandshakeData = self._to_bytes(ApiHandshakeData)


class DepartmentUserField(BaseField):
    """操作员组织架构关系"""
    _fields_ = [
        ('BrokerID', c_char * 11)  # ///经纪公司代码
        , ('UserID', c_char * 16)  # 用户代码
        , ('InvestorRange', c_char * 1)  # 投资者范围
        , ('InvestorID', c_char * 13)  # 投资者代码
    ]

    def __init__(self, BrokerID='', UserID='', InvestorRange='', InvestorID=''):
        super(DepartmentUserField, self).__init__()

        self.BrokerID = self._to_bytes(BrokerID)
        self.UserID = self._to_bytes(UserID)
        self.InvestorRange = self._to_bytes(InvestorRange)
        self.InvestorID = self._to_bytes(InvestorID)


class QueryFreqField(BaseField):
    """查询频率，每秒查询比数"""
    _fields_ = [
        ('QueryFreq', c_int)  # ///查询频率
    ]

    def __init__(self, QueryFreq=0):
        super(QueryFreqField, self).__init__()

        self.QueryFreq = int(QueryFreq)

    def from_tuple(self, i_tuple):
        self.QueryFreq = int(i_tuple[1])
