#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

import datetime
import pandas as pd
from pandas.tseries.offsets import MonthEnd, QuarterEnd, YearEnd
from ._owlerror import OwlError

# --------------------
# BLOCK 商品資訊與時間表
# --------------------
# 取得函數與商品對應表
class _DataID():
    def __init__(self):
        # 商品表
        #self._fp 付費版函數對應商品
        
        #self._test 免費版函數對應商品
        
        # 商品時間對照表
        self._table_code ={
            'd':'PYCtrl-14806a/',
            'm':'PYCtrl-14809a/',
            'q':'PYCtrl-14810a/',
            'y':'PYCtrl-14811a/'            
            }
        
        # 商品時間表
        self._table = {}
        
    # 取得函數與商品對應表
    def _pdid_map(self):
        '''
        擷取商品函數與商品ID表
        Returns
        ----------
        :DataFrame:
            FuncID          pdid
            ssp 	PYPRI-14776a
            msp 	PYPRI-14777b
            sby		PYBAL-14782a
            sbq		PYBAL-14780a
        
        [Notes]
        ----------
        FuncID: ssp-個股股價, msp-多股股價, sby-年度資產負債表(個股), sbq-季度資產負債表(個股)
        pdid: 商品對應的ID
        '''
        # 付費版資料表 url
        get_data_url = self._token['data_url'] + self._token['pythonmap']
        self._fp = self._data_from_owl(get_data_url).set_index("FuncID")
        
        # 免費版資料表 url
        get_data_url = self._token['data_url'] + self._token['testmap']
        self._test = self._data_from_owl(get_data_url).set_index("FuncID")

    # 取得付費版函數對應商品
    def _get_pdid(self, funcname:str):
        return self._fp.loc[funcname][0]
    
    # 取得免費版函數對應商品
    def _get_pdid_test(self, funcname:str):
        return self._test.loc[funcname][0]
    
    # 商品時間
    def _date_table(self, freq:str):
        get_data_url = self._token['data_url'] + self._table_code[freq.lower()]
        data = self._data_from_owl(get_data_url)
        if freq.lower() == 'd':
            get_data_url = get_data_url + '/TWA00/9999'
        return self._data_from_owl(get_data_url)
    
    # 新增時間對應表
    def _get_table(self, freq:str):
        if freq not in self._table.keys():
            self._table[freq] = self._date_table(freq)

    # 商品時間頻率
    def _date_freq(self, start:str, end:str, freq = 'd'):
        season = ['05','06','07','08','09','10','11','12']

        if freq.lower() == 'y':
            if len(start) != 4 or len(end) != 4:
                print('YearError:',OwlError._dicts['YearError'])
                return 'error'
            try:
                dt = pd.to_datetime(start, format = '%Y')
                dt = pd.to_datetime(end, format = '%Y')

            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        elif freq.lower() == 'm':
            if len(start) != 6 or len(end) != 6:
                print('MonthError:',OwlError._dicts['MonthError'])
                return 'error'
            try:
                dt = pd.to_datetime(start, format = '%Y%m')
                dt = pd.to_datetime(end, format = '%Y%m')
                         
            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        elif freq.lower() == 'q':
            if len(start) != 6 or len(end) != 6:
                print('SeasonError:',OwlError._dicts['SeasonError'])
                return 'error'

            if start[4:6] in season or end[4:6] in season:
                print('SeasonError2:',OwlError._dicts['SeasonError2'])
                return 'error'

        elif freq.lower() == 'd':
            if len(start) != 8 or len(end) != 8:
                print('DayError:',OwlError._dicts['DayError'])
                return 'error'
            
            try:
                dt = pd.to_datetime(start)
                dt = pd.to_datetime(end)
                
            except ValueError:
                print('ValueError:', OwlError._dicts["ValueError"])
                return 'error'

        if int(start) > int(end):
            print('DateError:',OwlError._dicts['DateError'])
            return 'error'
        
        temp = self._table[freq.lower()].copy()
        temp = temp[temp[temp.columns[0]].between(start, end)]
        
        if len(temp) == 0:
            print('CannotFind:', OwlError._dicts["CannotFind"])
            return 'error'
        return str(len(temp))

    def _time_format(self, start:str, end:str, freq = 'd'):
        '''轉換日期格式'''
        if freq == 'd':
            pass
                
        elif freq == 'm':
            start = pd.to_datetime(start,format='%Y%m')+MonthEnd(1)
            end = pd.to_datetime(end,format='%Y%m')+MonthEnd(1)

        elif freq == 'q':
            start = start[0:4]+start[4:6].replace('0','Q')
            start = pd.to_datetime(start)+QuarterEnd(1)
            
            end = end[0:4]+end[4:6].replace('0','Q')
            end = pd.to_datetime(end)+QuarterEnd(1)

        elif freq == 'y':
            start = pd.to_datetime(start)+YearEnd(1)
            end = pd.to_datetime(end)+YearEnd(1)
        return start,end
