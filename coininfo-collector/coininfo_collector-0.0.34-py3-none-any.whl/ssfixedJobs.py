# -*- coding: utf-8 -*-
# SSFixedJob
import logging
import requests
import ujson

import os
from time import time

from .coinSummary import CoinSummary
from .priceInExchange import PriceInExchange
#from .marketPairs import MarketPairs
from .sparklineWriter import SparklineWriter


log = logging.getLogger('coininfo_collector')

class SSFixedJobs:
    reportURL_coins = '' #"coinGeckoReportURL":"http://1.234.63.171:5000/coin/set",

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def setReportURL(
        url_data_svc
    ):
        SSFixedJobs.reportURL_coins = url_data_svc + '/coin/set'
        SSFixedJobs.reportURL_coinMarketPrice = url_data_svc + '/exchange/coins'
        SSFixedJobs.reportURL_coins_markets = url_data_svc + '/coin/markets'
        SSFixedJobs.reportURL_global = url_data_svc + '/coin/stats/global_gecko'
        SSFixedJobs.reportURL_market_chart = url_data_svc + '/coin/market/chart'
        SSFixedJobs.reportURL_exchange_coins_ex = url_data_svc + '/exchange/coins_ex'
        


    @staticmethod
    def recvResponse(jobName, output, id):
        if jobName == 'coins':
            SSFixedJobs.reportCoins(output['data'])
            SSFixedJobs.updateCoins(output['data'])
        elif jobName == 'coins_markets':
            SSFixedJobs.reportCoinsMarket(output['data'])
        elif jobName == 'global':
            SSFixedJobs.reportGlobal(output['data'])
        elif jobName == 'market_chart':
            SSFixedJobs.reportMarketChart(output['data'])
        elif jobName == 'ticker':
            SSFixedJobs.reportTicker(id, output)

        elif jobName == 'coinPriceMarket':
            SSFixedJobs.reportCoinPriceMarket(output, id)




    @staticmethod
    def reportCoins(data):
        try:
            reportResult = requests.put(SSFixedJobs.reportURL_coins, verify=False, json=data)
            if reportResult.status_code == 200:
                log.debug('reported coins. url:{} coinId: {}'.format(
                    SSFixedJobs.reportURL_coins,
                    data['id']
                ))
            else:
                log.error('report failed coins. coinId:{} code:{} url:{} msg:{}'.format(
                    data['id'],
                    reportResult.status_code,
                    SSFixedJobs.reportURL_coins,
                    reportResult.text,
                    ))

        except Exception as inst:
            log.error('exception in reportCoins. msg:{}'.format(inst.args))

    @staticmethod
    def reportCoinsMarket(data):
        perPage = 250

        marketsCnt = len(data)
        
        curIdx = 0
        curPage = 0

        while True:
            isLagePage = True if (curIdx+perPage) >= marketsCnt else False
            objectData = {"data":data[curIdx:curIdx+perPage], "page":curPage, "lastPage":isLagePage}

            for i in range(3):
                reportResult = requests.put(
                    SSFixedJobs.reportURL_coins_markets,
                    verify=False,
                    json=objectData
                )
                if 200 == reportResult.status_code:
                    log.debug('reported reportCoinsMarket. curIDX:{} curPage:{}'.format(curIdx, curPage))
                    break
                else:
                    log.error('failed reportCoinsMarket. code:{} msg:{}'.format(
                        reportResult.status_code,
                        reportResult.text,
                    ))

            if isLagePage is True:
                break

            curIdx = curIdx + perPage
            curPage = curPage + 1


    @staticmethod
    def reportTicker(exchangeId, output):
        tickers = output['tickers']
        if 0 >= len(tickers):
            log.error('reportTicker(). empty tickers')
            return True

        try:
            reportResult = requests.put(
                SSFixedJobs.reportURL_exchange_coins_ex,
                verify=False,
                json={
                    'name':exchangeId,
                    'tickers':tickers,
                    'mts':int(round(time() * 1000))
                    }
                )
            if 200 == reportResult.status_code:
                log.debug('reported tickers. exchange:{}'.format(exchangeId))
            else:
                log.error('failed reportTicker. code:{} url:{} msg:{}'.format(
                    reportResult.status_code,
                    SSFixedJobs.reportURL_exchange_coins_ex,
                    reportResult.text,
                ))
        except Exception as inst:
            log.error('exception reportTicker. url:{} msg:{}'.format(
                SSFixedJobs.reportURL_exchange_coins_ex, inst.args
            ))

        
        # cpu 부하가 많아서 pair 정보는 업데이트는 보류..
        # SSFixedJobs.reportPairs()


    # @staticmethod
    # def reportPairs(exchange_id, tickers):
    #     #exchange_id = tickers[0]['market']['identifier']
    #     pairSet = set()

    #     for ticker in tickers:
    #         pairSet.add(
    #             ticker['base'] + '|' + ticker['target']
    #         )

    #     pairs = list(pairSet)
    #     pairs.sort(reverse=False)

    #     # pair update.
    #     MarketPairs().setMarketPairs(exchange_id, pairs)
    #     return True

    
    @staticmethod
    def reportGlobal(data):
        data['mts'] = int(round(time() * 1000))

        reportResult = requests.put(
            SSFixedJobs.reportURL_global,
            verify=False,
            json=data
        )

        if 200 == reportResult.status_code:
            log.debug('reported reportGlobal.')
        else:
            log.error('failed reportGlobal. code:{} url:{} msg:{}'.format(
                reportResult.status_code,
                SSFixedJobs.reportURL_global,
                reportResult.text,
            ))

    @staticmethod
    def reportMarketChart(data):
        reportResult = requests.put(
            SSFixedJobs.reportURL_market_chart,
            verify=False,
            json=data
        )

        if 200 == reportResult.status_code:
            log.debug('reported reportMarketChart.')
        else:
            log.error('failed reportMarketChart. code:{} url:{} msg:{}'.format(
                reportResult.status_code,
                SSFixedJobs.reportURL_market_chart,
                reportResult.text,
            ))


    @staticmethod
    def updateCoins(data):
        # 게코넘버
        gecko_num = 0
        try:
            thumbURL = data['image']['thumb']
            idxStart = thumbURL.find('images/') + 7
            endIDX = thumbURL.find('/', idxStart)
            gecko_num = int(thumbURL[idxStart:endIDX])
        except Exception as inst:
            log.error('updateCoins failed get geckoNumber. id:{} msg:{} thumbURL:{}'.format(
                data['id'],
                inst.args,
                thumbURL,
                ))
            return

        trade_url = ''
        # for ticker in data['tickers']:
        #     if 'trade_url' not in ticker:
        #         continue

        #     if ticker['trade_url'] == None:
        #         continue

        #     trade_url = ticker['trade_url']
        #     break

            
        image_thumb = ''
        image_small = ''
        image_large = ''
        try:
            image_thumb = data['image']['thumb']
            image_small = data['image']['small']
            image_large = data['image']['large']
        except Exception as inst:
            log.error('updateCoins no field. error:{}'.format(inst.args))
            return

        
        # coinObj = {
        #     'coin_id' : data['id'],
        #     'gecko_id' : int(gecko_num),
        #     'symbol' : data['symbol'],
        #     'name_en' : data['localization']['en'],
        #     'name_ko' : data['localization']['ko'],
        #     'image_thumb' : image_thumb,
        #     'image_small' : image_small,
        #     'image_large' : image_large,
        #     'trade_url' : trade_url,
        # }
        try:
            CoinSummary().setCoinInfo(
                data['id'],
                int(gecko_num),
                data['symbol'],
                data['localization']['en'],
                data['localization']['ko'],
                image_thumb,
                image_small,
                image_large,
                trade_url,
            )
        except Exception as inst:
            log.error('failed updateCoins setCoinInfo. error:{}'.format(inst.args))


    @staticmethod
    def reportCoinPriceMarket(output, marketId):
        # 모든 ticker 정보의 거래량 합산
        addedInfoMap = dict()
        exchangeList = list()
        volumeDic = dict()

        for ticker in output['tickers']:
            #print(ujson.dumps(ticker))
            if 'coin_id' not in ticker:
                log.debug('no coinid. content:{}'.format(ujson.dumps(ticker)))
                continue

            currentPrice = float(ticker['converted_last']['usd'])
            currentVolume = float(ticker['volume'])
            
            if str(ticker['coin_id']) not in addedInfoMap:
                sigPrice = currentPrice
                maxVolume = currentVolume

                addedInfoMap[str(ticker['coin_id'])] = (
                    sigPrice,       # 대표 가격.
                    ticker['trade_url'],
                    maxVolume,      # 최대 거래량.
                )

                volumeDic[str(ticker['coin_id'])] = currentPrice * currentVolume

            else:
                prevValues = addedInfoMap[str(ticker['coin_id'])]

                if currentVolume > prevValues[2]:
                    sigPrice = currentPrice
                    maxVolume = currentVolume

                    addedInfoMap[str(ticker['coin_id'])] = (
                        sigPrice,       # 대표 가격
                        ticker['trade_url'],
                        maxVolume,      # 최대 거래량
                    )

                volumeDic[str(ticker['coin_id'])] += currentPrice * currentVolume

        for k, v in volumeDic.items():
            exchangeList.append(
                [
                    v, 
                    k,
                ]
            )

        exchangeList.sort(reverse=True)

        # pre-check
        coinObjList = list()

        for coin in exchangeList:
            coinObj = CoinSummary().getCoinInfoByCoinId(coin[1])
            if coinObj is None:
                log.error('none of coininfo. coin:{}'.format(coin))
            else:
                coinObjList.append((coin, coinObj))

            if 10 <= len(coinObjList):
                break

        if 10 > len(coinObjList):
            log.error('다음 페이지를 읽어들여서 합산해야 함.')

       
        geckoIdList = list()

        # 보고용 자료 생성
        for rank, coinPair in enumerate(coinObjList):
            coin = coinPair[0]
            coinObj = coinPair[1]
            current_price = float(addedInfoMap[coin[1]][0])

            price1d = PriceInExchange().getPrice1day(marketId, coinObj['coin_id'])
            if price1d is None:
                # 어제 가격 정보가 없음
                price_change = 0.0
            else:
                if price1d == 0:
                    price_change = 0.0
                else:
                    price_change = ((current_price / price1d) - 1.0) * 100.0

            output['data'].append( 
                {
                    'rank':rank,
                    'id':coinObj['coin_id'],
                    'name_en':coinObj['name_en'],
                    'name_ko':coinObj['name_ko'],
                    'current_price':current_price,
                    'price_change_percentage_24h':price_change,
                    'symbol':coinObj['symbol'],
                    'total_volume':coin[0],
                    'img_num': int(coinObj['gecko_id']),
                    'trade_url': addedInfoMap[coin[1]][1],
                    'image_thumb' : coinObj['image_thumb'],
                    'image_small' : coinObj['image_small'],
                    'image_large' : coinObj['image_large'],
                }
            )

            geckoIdList.append(int(coinObj['gecko_id']))


        # 보관하던 tickers 삭제
        del output['tickers']
        #log.debug('getCoinPriceMarket output:{}'.format(ujson.dumps(output)))


        try:
            reportResult = requests.put(
                SSFixedJobs.reportURL_coinMarketPrice,
                verify=False,
                json=output
            )
            
            if reportResult.status_code == 200:
                log.debug('reported CoinPriceMarket. exchageID:{}'.format(
                    marketId
                ))
            else:
                log.error('report failed CoinPriceMarket. exchageID:{} code:{} url:{} msg:{}'.format(
                    marketId,
                    reportResult.status_code,
                    SSFixedJobs.reportURL_coinMarketPrice,
                    reportResult.text,
                ))
        except Exception as inst:
            log.error('exception in CoinPriceMarket. msg:{}'.format(inst.args))

        
        # 거래소-코인 가격정보 저장
        PriceInExchange().saveCoinPrice(marketId, addedInfoMap)

        # update Sparkline
        if 'sparklineWriter' in os.environ and os.environ['sparklineWriter'] == 'no':
            pass
        else:
            SparklineWriter().updateSparkline(geckoIdList)

        return True
        