#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

import pandas as pd
from functools import wraps 

# --------------------
# BLOCK 除錯
# --------------------
class OwlError():
    _dicts = {
                'YearError':'日期格式錯誤，請重新輸入。格式:yyyy',
                'SeasonError':'日期格式錯誤，請重新輸入。格式:yyyyqq',
                'SeasonError2':'日期格式錯誤，季別應在 01 至 04 之間',
                'MonthError':'日期格式錯誤，請重新輸入。格式:yyyymm',
                'DayError':'日期格式錯誤，請重新輸入。格式:yyyymmdd',
                'DateError':'資料日期輸入錯誤，請確認：起日期<迄日期',
                'YQMError':"欲查詢季資料，請輸入'Q'；年資料，請輸入'Y'；月資料，請輸入'M'",
                'SidError':'請重新確認您的股票代號是否輸入正確',
                'ColumnsError':'請重新確認您的欄位名稱是否輸入正確',
                'ValueError':'日期規則錯誤，請重新確認!!',
                'PdError':'請至數據貓頭鷹網站開啟/購買該商品使用權限',
                'ExError':'操作錯誤，請重新再輸入',
                'CannotFind':'指定日期不在範圍內'
                }

    _http_error = {
        # 200 : '接受請求並回復結果',
        400 : '請求的網址參數不合法，請確認請求資料的正確性',
        401 : '尚未認證或驗證碼已過期不合法，請重新認證',
        403 : '無權存取指定請求，請確認有相關使用權限',
        404 : '指定的請求不存在，請確認請求網址的正確性',
        500 : '內部系統錯誤，請稍後再試'
    }
    
    def __init__(self):
        '''
        錯誤狀況的提示訊息對應表

        [NOTES]
        ----------
            - 記錄各種操作錯誤情況
            - 包含 http 與 自訂錯誤
        '''
    @classmethod
    def table(cls):    
        return pd.Series(cls._dicts)
    
    @classmethod
    def http(cls):
        return pd.Series(cls._http_error)
    
    def _check_dt(di = 'd'):
        def inner_function(func):
            @wraps(func)
            def wrap(self, dt, colist = None):
                season = ['05','06','07','08','09','10','11','12']
                
                if di.lower() == 'y':
                    if len(dt) != 4:
                        print('YearError:',OwlError._dicts['YearError'])
                        return None
                    try:
                        dts = pd.to_datetime(dt, format = '%Y')             
                    except ValueError:
                        print('ValueError:', OwlError._dicts["ValueError"])
                        return None
                    
                elif di.lower() == 'm':
                    if len(dt) != 6:
                        print('MonthError:',OwlError._dicts['MonthError'])
                        return None
                    try:
                        dts = pd.to_datetime(dt, format = '%Y%m')              
                    except ValueError:
                        print('ValueError:', OwlError._dicts["ValueError"])
                        return None
                    
                elif di.lower() == 'q':
                    if len(dt) != 6:
                        print('SeasonError:',OwlError._dicts['SeasonError'])
                        return None
                    if dt[4:6] in season:
                        print('SeasonError2:',OwlError._dicts['SeasonError2'])
                        return None
                    
                elif di.lower() == 'd':  
                    if len(dt) != 8:
                        print('DayError:',OwlError._dicts['DayError'])
                        return None
                    
                    try:
                        dts = pd.to_datetime(dt)
                    except ValueError:
                        print('ValueError:', OwlError._dicts["ValueError"])
                        return None
                return func(self, dt, colist)
            return wrap
        return inner_function
    
    def _check_di(func):
        @wraps(func)
        def wrap(self, di, dt, colist = None):
            
            season = ['05','06','07','08','09','10','11','12']
            
            if di.lower() == 'y':
                if len(dt) != 4:
                    print('YearError:',OwlError._dicts['YearError'])
                    return None
                try:
                    dts = pd.to_datetime(dt, format = '%Y')             
                except ValueError:
                    print('ValueError:', OwlError._dicts["ValueError"])
                    return None
   
            elif di.lower() == 'm':
                if len(dt) != 6:
                    print('MonthError:',OwlError._dicts['MonthError'])
                    return None
                try:
                    dts = pd.to_datetime(dt, format = '%Y%m')              
                except ValueError:
                    print('ValueError:', OwlError._dicts["ValueError"])
                    return None

            elif di.lower() == 'q':
                if len(dt) != 6:
                    print('SeasonError:',OwlError._dicts['SeasonError'])
                    return None
                if dt[4:6] in season:
                    print('SeasonError2:',OwlError._dicts['SeasonError2'])
                    return None
                
            elif di.lower() == 'd':  
                if len(dt) != 8:
                    print('DayError:',OwlError._dicts['DayError'])
                    return None 
                try:
                    dts = pd.to_datetime(dt)
                except ValueError:
                    print('ValueError:', OwlError._dicts["ValueError"])
                    return None
            return func(self, di, dt, colist)
        return wrap
