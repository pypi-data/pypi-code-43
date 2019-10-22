import time
import urllib.parse
import hashlib
import requests


class Yiyatong(object):
    """
    调用怡亚通接口类

    """
    status = "test"

    urlDict ={
        "test": "http://pre-openapi.380star.com",
        "pro": "https://openapi.380star.com"
    }
    appKeyDict = {
        "test": "yd2c0fc4f4a49a3e47",
        "pro": "yd2c0fc4f4a49a3e47"
    }
    appSecretDict = {
        "test": "7db7f1cbab1e44f686012ad0cb42c460",
        "pro": "7db7f1cbab1e44f686012ad0cb42c460"
    }
    proxiesDict = {
        "pro": {"https": "https://120.76.64.3"},
        "test": {"http": "http://47.112.106.24:3128", "https": "https://47.112.106.24:3128"}
    }
    url = "https://testapi.zhylgz.cn/api/other/yiyatong"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    def __init__(self):
        self.yyt_url = self.urlDict.get(self.status)
        self.currentTime = self.get_timestamp()
        self.appKey = self.appKeyDict.get(self.status)
        self.appSercet = self.appSecretDict.get(self.status)
        self.proxies = self.proxiesDict.get(self.status)

    def get_timestamp(self):
        now = time.time()  # 1s = 1000ms
        now = int(now * 1000)  # 获得13位时间戳
        print(now)
        return now

    def get_sign(self,data:dict):
        params = sorted(data.items(), key=lambda x: x[0])
        print(params)
        stringA = ""
        for item in params:
            stringA = stringA + str(item[0])+"="+str(item[1])+"&"
        stringSignTemp = stringA + self.appSercet
        print(stringSignTemp)
        gen = hashlib.md5(stringSignTemp.encode("utf-8"))
        gen = gen.hexdigest()
        print(gen)
        return gen

    def sort_params(self,params:dict):
        return sorted(params.items(),key=lambda x:x[0])

    def getSpuIdList(self,pageIndex=1,pageSize=500,createStartTime=None,createEndTime=None):
        """
        获取商品SpuId列表
        :param pageIndex: 页码，默认 1
        :param pageSize: 每页大小，默认 500，最大1000
        :param createStartTime: 选品开始时间，格式 为 'yyyy-MM-dd HH:mm:ss'
        :param createEndTime:选品截止时间，格式 为 'yyyy-MM-dd HH:mm:ss'
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "pageIndex":pageIndex,
            "pageSize": pageSize,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/getSpuIdList"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        if int(data["code"]) == 0:
            return data["data"]
        return data

    def getSpuDetail(self,spuIds):
        """
        查询SPU详情【不包含sku列表】
        :param spuIds:  一次最多请求50个spu，超过按50个算，用英文逗号分隔
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "spuIds": spuIds,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/getSpuDetail"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        return result.json()

    def getSkuListDetailBySpuId(self,spuId):
        """
        根据SPUID 查询SKU信息
        :param spuId: spuId
        :return:
        """
        params = {
             "appKey": self.appKey,
            "currentTime": self.currentTime,
            "spuId": spuId
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/getSkuListDetailBySpuId"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findBrandList(self,pageIndex=1, pageSize=100):
        """
        查询品牌列表
        :param pageIndex: 当前页 默认第一页
        :param pageSize: 每页大小，默认 100 最大500
        :return:
        """
        params = {
             "appKey": self.appKey,
            "currentTime": self.currentTime,
            "pageIndex":pageIndex,
            "pageSize": pageSize,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/findBrandList"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def getAddressInfo(self, provinceName, cityName, regionName):
        """
        查询品牌列表
        :param pageIndex: 当前页 默认第一页
        :param pageSize: 每页大小，默认 100 最大500
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "provinceName": provinceName,
            "cityName": cityName,
            "regionName": regionName,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/address/getAddressInfo"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findProdCategory(self, categoryId=None):
        """
        查询分类信息
        :param categoryId: 分类ID,不传则查询所有一级分类,反之则查询该分类下的子分类信息
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
        }
        if categoryId:
            params["categoryId"] = categoryId
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/findProdCategory"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findSkuInventory(self, codes, areaId=None,):
        """
        4.2.7 查询商品库存
        :param areaId: 区域ID 省市区唯一ID, 使用英文逗号拼接
        :param codes: 最多查200个,code 多个以英文逗号拼接
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "codes": codes
        }
        if areaId:
            params["areaId"] = areaId
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/findSkuInventory"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findSkuSalePrice(self, codes):
        """
        4.2.8 查询商品价格
        :param codes: 最多查200个,code 多个以英文逗号拼接
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "codes": codes
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/findSkuSalePrice"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def preHoldSkuInventory(self, areaId, outOrderNo, codeInvList):
        """
        4.3.1 预占商品库存
        :param areaId: 省市区唯一ID, 使用英文逗号拼接
        :param outOrderNo: 第三方订单号 <= 32位
        :param codeInvList: 商品及库存信息json, 参考下面的demo
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "areaId": areaId,
            "outOrderNo": outOrderNo,
            "codeInvList": codeInvList
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/goods/preHoldSkuInventory"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def addOrder(self, outOrderNo, receiverAreaName, receiverAreaId, receiverAddr, receiver, receiverPhone, skuList):
        """
        4.3.3 订单下单
        :param outOrderNo: 第三方订单号 <= 32位
        :param receiverAreaName: 必填 提货地区，例如：辽宁省,沈阳市,铁西区
        :param receiverAreaId: 收货人省市区街道(省ID,市ID,区ID) 例如：4524130,4524157,4524163
        :param receiverAddr: 收货人详细地址
        :param receiver: 收货人
        :param receiverPhone: 收货人电话
        :param skuList: 商品列表 json 串，格式参考下面json [
    {
        "code": "SL-ECP-6072",  //必填       商品编码
        "quantity": "1"         //必填       数量
    }
]
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "receiverAreaName": receiverAreaName,
            "outOrderNo": outOrderNo,
            "receiverAreaId": receiverAreaId,
            "receiverAddr":receiverAddr,
            "receiver":receiver,
            "receiverPhone": receiverPhone,
            "skuList": skuList,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/order/addOrder"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findOrderByOrderSn(self, orderSn):
        """
        4.3.5 订单详情
        :param orderSn: 星链子订单sn
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "orderSn": orderSn
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/order/findOrderByOrderSn"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def findExpressInfoByOrderSn(self, orderSn):
        """
        4.3.6 订单物流信息
        :param orderSn: 星链子订单sn
        :return:
        """
        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "orderSn": orderSn
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/order/findExpressInfoByOrderSn"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data

    def getOrderFreight(self,regionId,receiverAddr,skuList):
        """
        4.3.7 订单运费查询
        :param regionId: 区域ID
        :param receiverAddr: 收货人详细地址
        :param skuList: 商品列表 json 串，格式参考下面json
        :return:
        skuList = [
    {
        "code": "SL-ECP-6072",  //必填       商品编码
        "quantity": "1"         //必填       数量
    }
]
        """

        params = {
            "appKey": self.appKey,
            "currentTime": self.currentTime,
            "regionId": regionId,
            "receiverAddr": receiverAddr,
            "skuList": skuList,
        }
        sign = self.get_sign(params)
        params["sign"] = sign
        params["url"] = self.yyt_url + "/order/getOrderFreight"
        params = self.sort_params(params)
        result = requests.get(self.url, data=params)
        data = result.json()
        return data



if __name__ == '__main__':
    yiyatong = Yiyatong()
    # data = yiyatong.getSpuIdList()  # 获取商品SpuId列表
    # data = yiyatong.getSpuDetail('116997,116998')  #  查询SPU详情
    # data = yiyatong.getSkuListDetailBySpuId("116997")  # 根据SPUID 查询SKU信息
    # data = yiyatong.findBrandList()  # 查询品牌列表
    # data = yiyatong.getAddressInfo("广东省", "广州市", "黄埔区")  # 查询地址信息
    # data = yiyatong.findProdCategory()  # 查询分类信息
    # data = yiyatong.findSkuInventory("SL-ECP-37234")  # 查询商品库存
    # data = yiyatong.findSkuSalePrice("SL-ECP-37234")  # 查询商品价格
    # data = yiyatong.preHoldSkuInventory('4524130,4524131,4524138','2019102611543881','[{"code": "SL-ECP-37234","quantity": "2"}]')  # 预占商品库存
    # data = yiyatong.addOrder(outOrderNo='2019102611543889',
    #                          receiverAreaName='广东省,广州市,黄埔区',
    #                          receiverAddr='伴河路118号',
    #                          receiverAreaId='4524130,4524131,4524138',
    #                          receiver='渣伟',
    #                          receiverPhone='18611111111',
    #                          skuList='[{"code": "SL-ECP-37234","quantity": "2"}]',
    #                          )  # 订单下单
    data = yiyatong.findOrderByOrderSn("323387823")  # 订单详情
    # data = yiyatong.findExpressInfoByOrderSn("323387823")  # 订单物流信息
    # data = yiyatong.getOrderFreight("4524138", "伴河路118号",'[{"code": "SL-ECP-37234","quantity": "2"}]')  # 订单运费查询
    print(data,type(data))
    """
    商品code：SL-ECP-37234
    areaId：'areaId': '4524130,4524131,4524138'
    {'code': 0, 'data': [{'statusName': '待发货', 'orderSn': '323386613', 'skuList': [{'price': '99.44', 'spuId': '116997', 'quantity': 2, 'code': 'SL-ECP-37234', 'skuId': '37234', 'prodName': '狮子座天使（Leo Angel）婴儿超薄绵柔纸尿裤 M62片（6-11kg）'}], 'status': '20'}], 'message': 'success'}
    """

