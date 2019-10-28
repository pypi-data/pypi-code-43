# -*- coding: utf-8 -*-
# ijMarketPriceGlobal
import logging
import requests
import ujson
from .coinSummary import CoinSummary

log = logging.getLogger('coininfo_collector')

class IJMarketPriceGlobal:
    reportURL_exchange_coins = ''
    reportURL_sparkline = ''
    requestURL_getCoinInfo = ''

    def __init__(self, *args, **kwargs):
        pass
    

    @staticmethod
    def setURL(
        urlExchangeCoins,
        urlSparklinePrefix,
        requestGetCoinInfoURL,
    ):
        IJMarketPriceGlobal.reportURL_exchange_coins = urlExchangeCoins
        IJMarketPriceGlobal.reportURL_sparkline = urlSparklinePrefix + '/updateSparkline'
        IJMarketPriceGlobal.requestURL_getCoinInfo = requestGetCoinInfoURL

    @staticmethod
    def getCoinInfo(coinId):
        try:
            response = requests.post(
                IJMarketPriceGlobal.requestURL_getCoinInfo,
                verify=False,
                json={
                    'coin_id':coinId,
                },
            )
            if response.status_code != 200:
                log.error('failed getCoinInfo. code:{} url:{} msg:{}'.format(
                    response.status_code, IJMarketPriceGlobal.requestURL_getCoinInfo,
                    response.text)
                )
                return None
        except Exception as inst:
            log.error('exception in getCoinPriceGlobal-getCoinInfo. msg:{}'.format(inst.args))
            return None

        return ujson.loads(response.text)


    @staticmethod
    def reportCoinPriceGlobal(jobName, data):
        output = {}
        output['market_name'] = '_global'
        output['data'] = list()

        rank = 0
        geckoIdList = list()

        for coin in data:
            coinObjWrap = IJMarketPriceGlobal.getCoinInfo(coin['id'])
            if coinObjWrap is None or coinObjWrap['coinObj'] is None:
                log.error('none of coininfo. coindID:{}'.format(coin['id']))
                continue

            coinObj = coinObjWrap['coinObj']

            output['data'].append(
                {
                    'rank':rank,
                    'id':coinObj['coin_id'],
                    'name_en':coinObj['name_en'],
                    'name_ko':coinObj['name_ko'],
                    'current_price':float(coin['current_price']),
                    'price_change_percentage_24h':float(coin['price_change_percentage_24h']),
                    'symbol':coinObj['symbol'],
                    'total_volume':float(coin['total_volume']),
                    'img_num': int(coinObj['gecko_id']),
                    'trade_url': coinObj['trade_url'],
                    'image_thumb' : coinObj['image_thumb'],
                    'image_small' : coinObj['image_small'],
                    'image_large' : coinObj['image_large'],
                }
            )

            # for sparkline
            geckoIdList.append(int(coinObj['gecko_id']))

            rank += 1
            if rank >= 10:
                break

        #print('output:{}'.format(ujson.dumps(output)) )
        # report to data-svc
        IJMarketPriceGlobal._report_retry(
            3,
            'getCoinPriceGlobal',
            IJMarketPriceGlobal.reportURL_exchange_coins,# self._urls['urls']['coinPriceReportURL'],
            output
        )

        # update Sparkline
        try:
            # report to scheduler
            response = requests.post(
                IJMarketPriceGlobal.reportURL_sparkline,
                verify=False,
                json={
                    'geckoIdList':geckoIdList,
                },
            )

            if response.status_code != 200:
                log.error('failed report. code:{} url:{} msg:{}'.format(
                    response.status_code, IJMarketPriceGlobal.reportURL_sparkline,
                    response.text)
                )
        except Exception as inst:
            log.error('exception in getCoinPriceGlobal-sparkline. msg:{}'.format(inst.args))



    @staticmethod
    def _report_retry(retyCnt, name, url, output):
        for i in range(retyCnt):
            response = requests.put(
                url,
                verify=False,
                json=output
            
            )
            if 200 == response.status_code:
                log.debug('reported {}. url:{}'.format(name, url))
                break
            else:
                log.error('failed {}. msg:{}'.format(name, response.text))

        if 200 != response.status_code:
            log.error('failed send retry : {}  msg:{}'.format(name, response.text))