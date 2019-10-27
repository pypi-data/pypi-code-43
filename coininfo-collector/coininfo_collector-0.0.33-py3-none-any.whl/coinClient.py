# -*- coding: utf-8 -*-
import asyncio
import copy
import logging
import queue
import os
import threading
import requests
from time import sleep
import ujson
from utail_base import web_support, threading_support

from .coinSummary import CoinSummary

# from .coinCommons import CoinCommons as CC
from .ijMarketPriceGlobal import IJMarketPriceGlobal

log = logging.getLogger('coininfo_collector')

api_prefix = 'https://api.coingecko.com/api/v3/'

limitRequestsPerMin = int(os.environ['limitRequestsPerMin']) if 'limitRequestsPerMin' in os.environ else 100
# self._requestDurationForOneRequest = float(limitRequestsPerMin) / 60.0

requestCostTime = float(60) / float(limitRequestsPerMin)


class CoinClientBaseClass:
	pass

class CoinClientSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(CoinClientSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class CoinClient(CoinClientBaseClass, metaclass=CoinClientSingleton):
    def __init__(
        self, loggerName='coininfo_collector', 
        keepJobsInQ = 5,
        aliveURL='http://127.0.0.1:6000/coininfo/coinAlive',
        requestURL='http://127.0.0.1:6000/coininfo/coinJobRequest',
        requestGetCoinInfoURL='http://127.0.0.1:6000/coininfo/get_coin_info',
        reportURL='http://127.0.0.1:6000/coininfo/coinJobReport',
        logURL='http://127.0.0.1:6000/coininfo/coinJobReport',
        schudulerURLPrefix='http://127.0.0.1:6000/coininfo',
        jobCoin=True,
        jobTicker=True,
    ):
        self._log = logging.getLogger(loggerName)
        self._keepJobsInQ = keepJobsInQ

        self._aliveURL = aliveURL
        self._requestURL = requestURL
        self._reportURL = reportURL
        self._logURL = logURL

        self._jobCoin = jobCoin
        self._jobTicker = jobTicker


        # job q
        self._jobQ = queue.Queue()
        self._reportQ = queue.Queue()
        self._injectQ = queue.Queue()

        self._requestJobList = list()

        # make Job List.
        self._makeJobList()

        self._tickerPage = 1
        self._coinsMarketPage = 1

        self._tickerList = list()


        # priceGlobal
        IJMarketPriceGlobal.setURL(
            os.environ['url_data_svc'] + '/exchange/coins',
            'http://' + os.environ['schudulerURLPrefix'],
            requestGetCoinInfoURL,
        )

        # 보고 쓰레드 시작
        treport = threading.Thread(
            target=self._reportTask,
            name='coinReport'
        )             
        treport.setDaemon(False)
        treport.start()

        
        # 요청 쓰레드 시작
        trequest = threading.Thread(
            target=self._requestTask,
            name='coinRequest'
        )             
        trequest.setDaemon(False)
        trequest.start()

        # 작업 쓰레드 시작
        t = threading.Thread(
            target=self._runTask,
            # args=[self._pjs, threadName, i], 
            name='coinClient'
        )             
        t.setDaemon(True)
        t.start()


        # ij 쓰레드
        t2 = threading.Thread(
            target=self._runTaskInjected,
            name='coinClientInjected'
        )             
        t2.setDaemon(True)
        t2.start()
        

    def _makeJobList(self):
        if self._jobCoin is False \
            and self._jobTicker is False:
            web_support.raiseHttpError(log, 0, 'None jobs..')

        if self._jobCoin is True:
            self._requestJobList.append('jobCoin')
        if self._jobTicker is True:
            self._requestJobList.append('jobTicker')


    def _reportTask(self):
        while True:
            try:
                if self._reportQ.empty() is True:
                    sleep(1)
                    continue

                job, target_id, output = self._reportQ.get()

                response = requests.post(
                    self._reportURL,
                    verify=False,
                    json={
                        'job':job,
                        'id':target_id,
                        'output':output,
                    },
                )

                if response.status_code != 200:
                    log.error('failed report. code:{} url:{} msg:{}'.format(
                        response.status_code, self._reportURL, response.text))
                    sleep(1)
                    continue

            except Exception as inst:
                log.error('exception in _reportTask. msg:{}'.format(inst.args))


    def _requestTask(self):

        while True:
            try:
                if requests.post(self._aliveURL).status_code == 200:
                    break

                sleep(1)
                
            except:
                log.debug('connecting to coin-scheduler. url:{}'.format(self._aliveURL))
                sleep(1)
                continue
        
        while True:
            try:
                if self._keepJobsInQ <= self._jobQ.qsize():
                    sleep(1)
                    continue

                response = requests.post(
                    self._requestURL,
                    verify=False,
                    json={
                        'jobs':self._requestJobList,
                    },
                )

                if response.status_code != 200:
                    log.error('failed _getJobCoinList. code:{} msg:{}'.format(response.status_code, response.text))

                    sleep(1)
                    continue

                jo = ujson.loads(response.text)
                #print(ujson.dumps(jo, ensure_ascii=False))

                for job in jo['jobs']:
                    self._jobQ.put(job)

                if 0 == len(jo['jobs']):
                    sleep(3)

            except Exception as inst:
                log.error('failed _getJobCoinList. msg:{}'.format(inst.args))
                sleep(3)

    def _runTask(self):
        while True:
            try:
                if self._jobQ.empty():
                    sleep(1)
                    continue

                job = self._jobQ.get()
                if 'id' not in job:
                    job['id'] = 0

                #print(job)

                endJob = False
                self._tickerPage = 1
                self._coinsMarketPage = 1
                self._coinPriceMarketPage = 1
                output = {}

                while endJob is False:
                    if job['job'] == 'coins_markets':
                        if 'data' not in output:
                            output['data'] = list()
                        endJob = self._requestCoinsMarkets(output)
                    elif job['job'] == 'market_chart':
                        endJob = self._requestMarketChart(job['id'], output)
                    elif job['job'] == 'coins':
                        endJob = self._requestCoins(job['id'], output)
                    elif job['job'] == 'global':
                        endJob = self._requestGlobal(output)
                    elif job['job'] == 'ticker':
                        if 'tickers' not in output:
                            output['tickers'] = list()
                        endJob = self._requestTicker(job['id'], output)
                    elif job['job'] == 'bitcoin':
                        endJob = self._requestBitcoin(output)
                    elif job['job'] == 'coinPriceMarket':
                        if 'data' not in output:
                            output['data'] = list()
                            output['tickers'] = list()

                        endJob = self._requestCoinPriceMarket(output, job['id'])
                        

                self._reportQ.put((
                    job['job'],
                    job['id'],
                    output
                ))

            except Exception as inst:
                log.error('exception in _runTask. job:{} msg:{}'.format(job, inst.args))


    
    def _runTaskInjected(self):
        while True:
            try:
                if self._injectQ.empty():
                    sleep(1)
                    continue

                job = self._injectQ.get()
                jobName = job['jobName']

                if jobName == 'marketPriceGlobal':
                    # 주요 암호화폐 시세(글로벌)
                    # report to datasvc
                    IJMarketPriceGlobal.reportCoinPriceGlobal(
                        jobName,
                        job['data'],
                    )

                    # report to scheduler
                    self._reportQ.put((
                        'coins_markets_global', # job name
                        'coins_markets_global', # id. not using in this job
                        job['data']
                    ))

            except Exception as inst:
                log.error('exception in _runTaskInjected. job:{} msg:{}'.format(jobName, inst.args))



    @threading_support.timeDuration(log, requestCostTime)
    def _requestCoinsMarkets(self, output):
        perPage = 250
        # order=volume_desc
        # order=market_cap_desc
        response = requests.request(
            "GET",
            api_prefix + 'coins/markets?vs_currency=usd&per_page={}&page={}&order=market_cap_desc&price_change_percentage=1h,24h,7d'.format(
                perPage, self._coinsMarketPage
            ),
            data='', 
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)


        jo = ujson.loads(response.text)

        if self._coinsMarketPage == 1:

            # 코인 한글이름 찾아넣기
            for coin in jo:
                coinObj = CoinSummary().getCoinInfoByCoinId(coin['id'])
                if coinObj is None:
                    coin['name_ko'] = coin['id']
                else:
                    coin['name_ko'] = coinObj['name_ko']

            # 주요 암호화폐 시세(글로벌)
            self._injectQ.put({
                'jobName':'marketPriceGlobal',
                'data':copy.deepcopy(jo),
            })

        try:
            arraySize = 0
            for ent in jo:
                arraySize += 1
                output['data'].append(ent)

            self._coinsMarketPage += 1

            return perPage > arraySize
            
        except Exception as inst:
            web_support.raiseHttpError(
                log, 
                response.status_code, 
                'exception in _requestCoinsMarkets. msg:{}. page:{}'.format(
                inst.args, self._coinsMarketPage)
            )

    @threading_support.timeDuration(log, requestCostTime)
    def _requestCoinPriceMarket(self, output, exchange_id):
        response = requests.request(
            "GET",
            api_prefix + 'exchanges/{}/tickers?page={}&order=volume_desc'.format(
                exchange_id, self._coinPriceMarketPage),
            data='', 
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)


        jo = ujson.loads(response.text)

        try:
            self._coinPriceMarketPage += 1

            output['tickers'].extend(jo['tickers'])

            # ticker 갯수가 100개 미만일 경우 마지막 페이지임.
            if 100 <= len(jo['tickers']):
                return False

        except Exception as inst:
            web_support.raiseHttpError(
                log, 0,
                'exception in _requestCoinPriceMarket. msg:{}. page:{}'.format(
                    inst.args, self._coinPriceMarketPage,
            ))

        # 거래소 이름
        output['market_name'] = jo['name']

        return True


    @threading_support.timeDuration(log, requestCostTime)
    def _requestMarketChart(self, target_id, output):
        response = requests.request(
            "GET",
            api_prefix + 'coins/{}/market_chart?vs_currency=usd&days=1'.format(
                target_id,
            ),
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)

        jo = ujson.loads(response.text)
        jo['cid'] = str(target_id)
        jo['days'] = 1

        output['data'] = jo
        return True

    @threading_support.timeDuration(log, requestCostTime)
    def _requestCoins(self, target_id, output):
        response = requests.request(
            "GET",
            api_prefix + 'coins/{}?tickers=true&market_data=true&community_data=true&developer_data=true&sparkline=true'.format(target_id),
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)

        jo = ujson.loads(response.text)
        
        output['data'] = jo
        return True

    @threading_support.timeDuration(log, requestCostTime)
    def _requestGlobal(self, output):
        response = requests.request(
            "GET",
            api_prefix + 'global',
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)

        jo = ujson.loads(response.text)

        output['data'] = jo
        return True

    
    def _requestBitcoin(self, output):
        exchange_ids_bitcoin = ['binance', 'bitfinex', 'upbit']

        for exchange_id in exchange_ids_bitcoin:
            response = requests.request(
                "GET",
                api_prefix + 'coins/bitcoin/tickers?exchange_ids={}&page=1'.format(exchange_id),
                headers={'cache-control': 'no-cache'},
            )

            if 200 != response.status_code:
                log.error('failed _requestBitcoin. exchangeID:{} code:{}'.format(
                    exchange_id, response.status_code
                ))
                continue

            jo = ujson.loads(response.text)

            jo['id'] = 'bitcoin'
            reportResult = requests.put(
                os.environ['url_data_svc'] + '/coin/tickers',
                verify=False,
                json=jo
            )
            if reportResult.status_code == 200:
                log.debug('reported. _requestBitcoin exchange_id: {}'.format(exchange_id))
            else:
                log.error('report failed _requestBitcoin. exchange_id:{}'.format(exchange_id))
        
        return True



    @threading_support.timeDuration(log, requestCostTime )
    def _requestTicker(self, target_id, output):
        response = requests.request(
            "GET",
            api_prefix + 'exchanges/{}/tickers?page={}&order=volume_desc'.format(
                target_id, self._tickerPage
            ),
            data='', 
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, response.text)

        self._tickerPage += 1

        jo = ujson.loads(response.text)

        try:
            output['tickers'].extend(jo['tickers'])
        except Exception as inst:
            web_support.raiseHttpError(
                log, 
                response.status_code, 
                '_requestTicker. no tickers. msg:{}. target_id:{}'.format(
                inst.args, target_id)
            )

        if len(output['tickers']) == 0:
            web_support.raiseHttpError(
                log, 
                0, 
                '_requestTicker. no tickers. (not error). exchange:{}'.format(
                target_id)
            )

        # ticker 갯수가 100개 미만일 경우 마지막 페이지 입니다.
        return 100 > len(jo['tickers'])
