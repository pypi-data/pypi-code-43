# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import logging
import queue
import os
import threading
import requests
from timeit import default_timer as timer
import ujson
from utail_base import web_support

# from .coinCommons import CoinCommons as CC
from .sparklineWriter import SparklineWriter
from .coinSummary import CoinSummary
from .s3Interface import S3Interface
from .priceInExchange import PriceInExchange
from .ssfixedJobs import SSFixedJobs
from .utils.web_requests_async import async_get

log = logging.getLogger('coininfo_collector')

api_prefix = 'https://api.coingecko.com/api/v3/'

class CoinSchedulerBaseClass:
	pass

class CoinSchedulerSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(CoinSchedulerSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class CoinScheduler(CoinSchedulerBaseClass, metaclass=CoinSchedulerSingleton):
    limitRequestsPerMin = int(os.environ['limitRequestsPerMin']) if 'limitRequestsPerMin' in os.environ else 100.0

    requestCostTime = float(60) / float(limitRequestsPerMin)

    costAdj = 1.0 / 100.0 * float(limitRequestsPerMin)

    # coins/markets
    fixedrp_coins_markets = 60.0 / costAdj
    # global
    fixedrp_global = 180.0 / costAdj
    # market_chart, coin
    fixedrp_market_chart = 7.0 / costAdj
    
    
    # 아래는 ticker 장비가 많아지면 제거합니다.
    # (제거)비트코인가격은(fixedrp_bitcoin) ticker 가 많아지면 제거합시다.
    fixedrp_bitcoin = 60.0 / costAdj

    # (제거) ticker 장비가 많아지면 거래소별 상위 코인 가격정보는 ticker 작업에서 처리합니다.
    fixedrp_coinPriceMarket = 180.0 / costAdj



    def __init__(
        self,
        loggerName='coininfo_collector',
        sparklineType = None,
        webdriverPath = None,
        aws_access_key_id = None,
        aws_secret_access_key = None,
        sparklineS3BucketName = None,
        sparklineOutputPrefix = None,
        jobCoinSumarry=None,
        jobPriceInExchange=None,
        ):

        self._log = logging.getLogger(loggerName)

        # job coins q
        self._coinQ = queue.Queue()
        # job tickers q
        self._exchangeQ = queue.Queue()
        # job fixedFq q
        self._fixedQ = queue.Queue()
        # job fixedFq q
        self._fixedOnceQ = queue.Queue()

        #
        self._lockExchanges = threading.Lock()
        # 거래ㅇ 상세 정보
        self._exchanges = list()

        self._tickCnt = 0


        # 거래소 정보
        log.info('CoinScheduler exchangesUpdate')
        self._exchangesUpdate()

        # 작업 쓰레드 시작
        t = threading.Thread(
            target=self._runTask,
            # args=[self._pjs, threadName, i], 
            name='coinScheduler'
        )             
        t.setDaemon(False)
        t.start()


        # Sparkline
        if sparklineType is None:
            self._sparklineWriter = None
        else:
            ts = threading.Thread(
                target=self._initSparkline,
                args=[
                    aws_access_key_id,
                    aws_secret_access_key,
                    webdriverPath,
                    sparklineS3BucketName,
                    sparklineOutputPrefix,
                ], 
                name='_initSparkline'
            )             
            ts.setDaemon(False)
            ts.start()
            # self._initSparkline(
            #     aws_access_key_id,
            #     aws_secret_access_key,
            #     webdriverPath,
            #     sparklineS3BucketName,
            #     sparklineOutputPrefix,
            # )

        # coinSummary
        if jobCoinSumarry:
            self._initCoinSummary()

        # priceInExchange
        if jobPriceInExchange:
            self._initPriceInExchange()


        # FixedJob
        SSFixedJobs.setReportURL(
            url_data_svc = os.environ['url_data_svc'],
        )

        timer = BackgroundScheduler()
        timer.start()
        timer.add_job(self._tick, 'interval', seconds=1, id="CoinSchedulerTick")

    def _initSparkline(self,
        aws_access_key_id,
        aws_secret_access_key,
        webdriverPath,
        sparklineS3BucketName,
        sparklineOutputPrefix,
    ):
        self._sparklineWriter = SparklineWriter()
        self._sparklineWriter.initSparklineWriter(
            ACCESS_KEY=aws_access_key_id,
            SECRET_KEY=aws_secret_access_key,
            webdriverPath=webdriverPath,
            sparklineS3BucketName=sparklineS3BucketName,
            sparklineOutputPrefix=sparklineOutputPrefix,
        )
        # if sparklineType == 'primaryCoins':
        #     pass
        # elif sparklineType == 'allCoins':
        #     pass


    def _initCoinSummary(self):
        log.info('init S3Interface')
        S3Interface().S3InterfaceInit(
            ACCESS_KEY=os.environ.get('aws_access_key_id'),
            SECRET_KEY=os.environ.get('aws_secret_access_key'),
        )

        log.info('init CoinSummary')
        self._coinSummary = CoinSummary()
        self._coinSummary.initCoinSummary(
            os.environ.get('dbConnString'),
        )

    def _initPriceInExchange(self):
        log.info('init PriceInExchange')
        PriceInExchange().initPriceInExchange(
            os.environ.get('dbConnString'),
        )

    def _tick(self):
        self._tickCnt += 1

        CoinSummary().tick()
        PriceInExchange().tick()

        if self._tickCnt >= 86400:
            self._tickCnt = 0

            t = threading.Thread(
                target=self._exchangesUpdate,
                name='exchageUpdateTick'
            )             
            t.setDaemon(True)
            t.start()


    def _runTask(self):
        #loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        asyncio.ensure_future(self._getJobFixedFreq())
        asyncio.ensure_future(self._getJobCoinList())
        asyncio.ensure_future(self._getExchangeJobList())

        loop.run_forever()

        print('broken task')


    def ping(self):
        pass

    def _exchangesUpdate(self):
        response = requests.request(
            'GET',
            'https://api.coingecko.com/api/v3/exchanges',
            headers={'cache-control': 'no-cache'},
        )

        if 200 != response.status_code:
            web_support.raiseHttpError(log, response.status_code, 'failed _exchangesUpdate')

        jo = ujson.loads(response.text)

        with self._lockExchanges:

            self._exchanges.clear()

            #print(ujson.dumps(jo, ensure_ascii=False))
            for ent in jo:
                self._exchanges.append(ent)


    async def _getJobFixedFreq(self):
        elapsed_coins_markets = 0.0
        elapsed_market_chart = 0.0
        elapsed_global = 0.0
        elapsed_bitcoin = 0.0
        elapsed_coinPriceMarket = 0.0

        sleepTimeUnit = 1.0

        try:
            while True:
                startTime = timer()

                await asyncio.sleep(sleepTimeUnit)

                if self._fixedQ.qsize() > 100:
                    log.error('Process the fixed-Q quickly. qsize:{}'.format(self._fixedQ.qsize()))
                    continue

                if CoinScheduler.fixedrp_coins_markets <= elapsed_coins_markets:
                    elapsed_coins_markets = 0.0
                    self._fixedOnceQ.put({'job':'coins_markets'})

                if CoinScheduler.fixedrp_market_chart <= elapsed_market_chart:
                    elapsed_market_chart = 0.0

                    if self._coinQ.empty() is False:
                        coinId = self._coinQ.get()
                        self._fixedQ.put({'job':'market_chart', 'id':coinId})

                        # ticker 클라이언트가 많아지면
                        # coins 잡 횟수를 줄여도 됩니다.
                        self._fixedQ.put({'job':'coins', 'id':coinId})
                    else:
                        log.error('coinQ is empty')

                if CoinScheduler.fixedrp_global <= elapsed_global:
                    elapsed_global = 0.0
                    self._fixedQ.put({'job':'global'})

                if CoinScheduler.fixedrp_bitcoin <= elapsed_bitcoin:
                    elapsed_bitcoin = 0.0
                    self._fixedOnceQ.put({'job':'bitcoin'})

                if CoinScheduler.fixedrp_coinPriceMarket <= elapsed_coinPriceMarket:
                    elapsed_coinPriceMarket = 0.0
                    self._fixedOnceQ.put({'job':'coinPriceMarket', 'id':'binance'})
                    self._fixedOnceQ.put({'job':'coinPriceMarket', 'id':'upbit'})
                    self._fixedOnceQ.put({'job':'coinPriceMarket', 'id':'bithumb'})
                

                elapsed = timer() - startTime

                elapsed_coins_markets += elapsed
                elapsed_market_chart += elapsed
                elapsed_global += elapsed
                elapsed_bitcoin += elapsed
                elapsed_coinPriceMarket += elapsed

        except Exception as inst:
            log.error('exception in _getJobFixedFreq. msg:{}'.format(inst.args))
                
                
    async def _getJobCoinList(self):
        while True:
            try:
                if 1000 <= self._coinQ.qsize():
                    await asyncio.sleep(1)
                    continue

                startTime = timer()

                respJson = await async_get(
                    log,
                    'https://api.coingecko.com/api/v3/coins/list',
                    headers={'cache-control': 'no-cache'},
                )

                if respJson is not None:
                    for ent in respJson:
                        self._coinQ.put(str(ent['id']))

            except Exception as inst:
                log.error('exception in _getJobCoinList. msg:{}'.format(inst.args))

            elapsed = timer() - startTime
            if float(CoinScheduler.requestCostTime) > (elapsed):
                await asyncio.sleep(float(CoinScheduler.requestCostTime) - float(elapsed))

    async def _getExchangeJobList(self):
        await asyncio.sleep(1)

        while True:
            try:
                if 15 <= self._exchangeQ.qsize():
                    await asyncio.sleep(0.1)
                    continue

                startTime = timer()

                respJson = async_get(
                    log,
                    api_prefix + 'exchanges',
                    headers={'cache-control': 'no-cache'},
                )

                if respJson is not None:
                    for ent in jo:
                        self._exchangeQ.put(str(ent['id']))

            except Exception as inst:
                log.error('exception in _getExchangeJobList. msg:{}'.format(inst.args))

            elapsed = timer() - startTime
            if float(CoinScheduler.requestCostTime) > (elapsed):
                await asyncio.sleep(float(CoinScheduler.requestCostTime) - float(elapsed))


    def _popTickerJob(self, cnt=10):
        outList = list()

        for _ in range(cnt):
            if self._exchangeQ.empty():
                break

            outList.append(
                {
                    'job':'ticker',
                    'id':self._exchangeQ.get()
                }
            )
        return outList


    def allocJob(self, jobs:list):
        output = list()

        if self._fixedOnceQ.empty() is False:
            fixedJob = self._fixedOnceQ.get()
            output.append(fixedJob)
            return output

        jobCnt = 0

        
        while True:
            if self._fixedQ.empty() is True:
                break
            fixedJob = self._fixedQ.get()
            output.append(fixedJob)
            jobCnt += 1

        requestUnit = 5
        if jobCnt >= requestUnit:
            return output

        # if 'jobCoin' in jobs:
        #     output.extend( self._popCoinJob(requestUnit - jobCnt) )

        if 'jobTicker' in jobs:
            output.extend( self._popTickerJob(requestUnit - jobCnt) )

        return output


    def updateSparkline(self, geckoIdList):
        if self._sparklineWriter is None:
            return

        self._sparklineWriter.updateSparkline(geckoIdList)

    def setCoinInfo(self, *args, **kwargs):
        CoinSummary().setCoinInfo(args, kwargs)

    def getCoinInfo(self, coin_id):
        return CoinSummary().getCoinInfoByCoinId(coin_id)

    def recvFj(self, jobName, output, id):
        SSFixedJobs.recvResponse(jobName, output, id)