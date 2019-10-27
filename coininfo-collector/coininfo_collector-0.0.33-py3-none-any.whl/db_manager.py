# -*- coding: utf-8 -*-
# db_manager
import logging
import os
import pymysql

log = logging.getLogger('coininfo_collector')


class DBManager:
    def __init__(self, dbConnString, idx=0):
        self._connStr = dbConnString.split(':')
        self._db = None
        self._idx = idx

    def __getDB(self):
        try:
            self._db = pymysql.connect(host=self._connStr[0], 
             port=int(self._connStr[1]), 
             user=self._connStr[2],
             passwd=self._connStr[3], 
             db=self._connStr[4], 
             charset='utf8mb4', 
             autocommit=True
            )
        except Exception as inst:
            log.error('failed getDB. msg:{}'.format(inst.args))
            self._db = None

        return self._db


    def funcTempalte(self, func, *args):
        retValue = False
        self.__getDB()

        try:
            if self._db is not None:
                func(*args)
                retValue = True

        except Exception as inst:
            # log the exception
            err = "There was an exception in {}. msg:{}".format(func.__name__, inst.args)
            log.error(err)
            retValue = False
        finally:
            if self._db is not None:
                self._db.close()
            return retValue

    def funcTempalteSelect(self, func, *args):
        retValue = None
        self.__getDB()

        try:
            if self._db is not None:
                retValue = func(*args)
                
        except:
            # log the exception
            err = "There was an exception in  "
            err += func.__name__
            log.error(err)
        finally:
            if self._db is not None:
                self._db.close()
            return retValue



    def selectGeckoCoinList(self):
        return self.funcTempalteSelect(self.__selectGeckoCoinList)
        
    def insertGeckoCoinList(self, coinDic):
        return self.funcTempalte(self.__insertGeckoCoinList, coinDic)

    def insertGeckoCoin(self, coinObj):
        return self.funcTempalte(self.__insertGeckoCoin, coinObj)

    def updateGeckoCoin(self, coinObj):
        return self.funcTempalte(self.__updateGeckoCoin, coinObj)

    def insertCoinPriceList(self, priceObjList): # market_no, coin_id, price
        return self.funcTempalte(self.__insertCoinPriceList, priceObjList)

    def selectPriceList(self):
        return self.funcTempalteSelect(self.__selectPriceList)

    def insertMarketPairs(self, pairObjList):
        return self.funcTempalte(self.__insertMarketPairs, pairObjList)

    def selectMarketPairsList(self):
        return self.funcTempalteSelect(self.__selectMarketPairsList)

    def clearPriceList(self, endTs):
        return self.funcTempalte(self.__clearPriceList, endTs)

        

    def __insertGeckoCoinList(self, coinDic):
        with self._db.cursor() as cursor:
            for k, v in coinDic.items():
                sql = 'INSERT INTO tbl_coingecko_coin (coin_id, gecko_id, symbol, name_en, name_ko, \
                    image_thumb, image_small, image_large)\
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (
                    str(v['coin_id']),
                    int(v['gecko_id']),
                    str(v['symbol']),
                    str(v['name_en']),
                    str(v['name_ko']),
                    str(v['image_thumb']),
                    str(v['image_small']),
                    str(v['image_large']),
                ))
        self._db.commit()

    def __insertGeckoCoin(self, coinObj):
        with self._db.cursor() as cursor:
            sql = 'INSERT INTO tbl_coingecko_coin (coin_id, gecko_id, symbol, name_en, name_ko, \
                image_thumb, image_small, image_large)\
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (
                str(coinObj['coin_id']),
                int(coinObj['gecko_id']),
                str(coinObj['symbol']),
                str(coinObj['name_en']),
                str(coinObj['name_ko']),
                str(coinObj['image_thumb']),
                str(coinObj['image_small']),
                str(coinObj['image_large']),
            ))
        self._db.commit()

    def __insertCoinPriceList(self, priceObjList):
        with self._db.cursor() as cursor:
            for priceObj in priceObjList:
                sql = 'INSERT INTO tbl_coingecko_price (market_no, coin_id, price, created_ts)\
                        VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, (
                    int(priceObj['market_no']),
                    str(priceObj['coin_id']),
                    float(priceObj['price']),
                    int(priceObj['created_ts']),
                ))
        self._db.commit()

    def __updateGeckoCoin(self, coinObj):
        with self._db.cursor() as cursor:
            sql = 'update tbl_coingecko_coin set coin_id=%s, symbol=%s, name_en=%s, name_ko=%s, \
                image_thumb=%s, image_small=%s, image_large=%s where gecko_id=%s'
            cursor.execute(sql, (
                str(coinObj['coin_id']),
                str(coinObj['symbol']),
                str(coinObj['name_en']),
                str(coinObj['name_ko']),
                str(coinObj['image_thumb']),
                str(coinObj['image_small']),
                str(coinObj['image_large']),
                int(coinObj['gecko_id']),
            ))
        self._db.commit()

    def __insertMarketPairs(self, pairObjList):
        with self._db.cursor() as cursor:
            for pairObj in pairObjList:
                sql = 'INSERT INTO tbl_coingecko_pairs (exchange_id, pairs, last_updated_ts)\
                        VALUES (%s, %s, %s) \
                         ON DUPLICATE KEY UPDATE \
                             pairs = %s,\
                             last_updated_ts = %s'
                cursor.execute(sql, (
                    str(pairObj['exchange_id']),
                    str(pairObj['pairs']),
                    int(pairObj['last_updated_ts']),
                    str(pairObj['pairs']),
                    int(pairObj['last_updated_ts']),
                ))
        self._db.commit()

    def __selectMarketPairsList(self):
        with self._db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = 'SELECT * FROM tbl_coingecko_pairs ORDER BY id ASC'
            cursor.execute(sql)
            return cursor.fetchall()

    def __selectGeckoCoinList(self):
        with self._db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = 'SELECT * FROM tbl_coingecko_coin'
            cursor.execute(sql)
            return cursor.fetchall()

    def __selectPriceList(self):
        with self._db.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = 'SELECT * FROM tbl_coingecko_price ORDER BY id ASC'
            cursor.execute(sql)
            return cursor.fetchall()

    def __clearPriceList(self, endTs):
        with self._db.cursor() as cursor:
            sql = "delete from tbl_coingecko_price where created_ts < %s"
            cursor.execute(sql, (
                int(endTs),
            ))
    

if __name__ == "__main__":
    dbm = DBManager(
        os.environ.get('dbConnString')
    )

    pairObjList = list()
    
    pairObjList.append({
        'exchange_id':'upbit',
        'pairs':'contents~',
        'last_updated_ts':123
    })

    pairObjList.append({
        'exchange_id':'upbit2',
        'pairs':'contents~',
        'last_updated_ts':1232
    })

    pairObjList.append({
        'exchange_id':'upbit2',
        'pairs':'contents~',
        'last_updated_ts':33
    })

    dbm.insertMarketPairs(pairObjList)
