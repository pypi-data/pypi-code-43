#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

import requests
import json
import time
import pandas as pd
from pandas.tseries.offsets import MonthEnd, QuarterEnd, YearEnd

from ._owlerror import OwlError
from ._owltime import _DataID

# --------------------
# BLOCK API擷取資料
# --------------------
# 核心程式
class OwlData(_DataID):
    def __init__(self, auid:str, ausrt:str):
        '''
        請輸入個人數據貓頭鷹相關資料，以便登入取得財經數據
        
        Parameters
        ----------
        :param auid: str 
        
            - 請輸入數據貓頭鷹 AppID
            
        :param ausrt: str
        
            - 請輸入數據貓頭鷹 應用程式密鑰
            
        '''
        self._token = {
            'token_url':"https://owl.cmoney.com.tw/OwlApi/auth",
            'token_params':"appId=" + auid + "&appSecret=" + ausrt,
            'token_headers':{'content-type': "application/x-www-form-urlencoded"},  #POST表單，預設的編碼方式 (enctype)
            'data_url':"https://owl.cmoney.com.tw/OwlApi/api/v2/json/",
            'testmap':"PYCtrl-14881b",
            'pythonmap':"PYCtrl-14882b"
            }
        
        # 取得 TOKEN 結果
        self._token_result = ''
        
        # Data Token
        self._data_headers = {}
        
        # 連線進入並輸出連線狀態
        self.status_code = self._request_token_authorization()
        
        # OwlTime Class
        super().__init__()
        
    def __repr__(self):
        return '貓頭鷹資料庫連線狀態: {}'.format(str(self.status_code))
    
    def _request(self,*args,**kargs):
        '''當連線出現異常時，重新啟動下載機制'''
        i=3
        while i >=0:
            try:
                return requests.request(*args,**kargs)
            except:
                time.sleep(3)
            i-=1

    # Token 取得
    def _request_token_authorization(self) -> int:
        '''請求權限交換'''
        self._token_result = self._request("POST",self._token['token_url'],
                                        data = self._token['token_params'],
                                        headers = self._token['token_headers'])

        if (self._token_result.status_code == 200):    
            token = json.loads(self._token_result.text).get("token")
            self._data_headers = {'authorization':'Bearer ' + token}
            self._pdid_map()
            return self._token_result.status_code

        elif(self._token_result.status_code in OwlError._http_error.keys()):
            print('錯誤代碼: {} '.format(str(self._token_result.status_code)),OwlError._http_error[self._token_result.status_code])
        
        else:
            print("連線錯誤，請洽業務人員")
            
    # 呼叫 OwlData 資料下載
    def _data_from_owl(self, url:str) -> pd.DataFrame:
        '''
        輸入API網址，獲取對應的數據資料
        
        Parameters
        ------------
        :param url: str

            - 在url的地方輸入API網址，回傳數據資料 - 個股/多股
        
        Returns
        --------
        :DataFrame: 輸出分別為個股與多股

        Examples
        ---------
        個股/多股: 輸出帶有DataFrame的資料格式
        
            個股: 
                日期     股票名稱   開盤價   最高價  最低價  ...
            0  20171229     台泥     36.20   36.80   36.10  ...
            1  20171228     台泥     36.10   36.25   36.00  ...
            2  20171227     台泥     36.10   36.45   36.00  ...
            3  20171226     台泥     36.10   36.50   35.95  ...
            4  20171225     台泥     35.30   36.25   35.10  ...
            
            多股: 
                股票代號    股票名稱     日期     開盤價  ...
            0    1101        台泥    20171229   36.20  ...
            1    1102        亞泥    20171229   27.80  ...
            2    1103        嘉泥    20171229   12.85  ...
            3    1104        環泥    20171229   22.85  ...

        Notes
        -------
        先請求網址回覆200後，才會抓取資料(網址輸入錯誤，才會撈不到資料)
        個股: 假設基準日: 20190701、股票代號: 1101、期數: 20，則會獲取自20190701往前20筆 1101的資料
        多股: 取指定日期當天，各檔的數據資料
        '''
        data_result = self._request("GET", url, headers = self._data_headers)
        
        # 若逾時連線，則重新再次連線一次
        try:
            if data_result.status_code == 200:
                pass
        except:
            data_result = self._request("GET", url, headers = self._data_headers)
        
        # status code 下載判別狀態
        try:
            if data_result.status_code == 200:
                data=json.loads(data_result.text)
                return pd.DataFrame(data.get('Data'), columns = data.get('Title'))

            elif data_result.status_code in OwlError._http_error.keys():
                print('錯誤代碼: {:s} '.format(str(self._token_result.status_code)),
                      OwlError._http_error[self._token_result.status_code])
                return 'error'
        except:
            return 'error'

    # 修正資料
    def _check(self, result:pd.DataFrame, freq=None, num_col=2, colists=None, pd_id=None) -> pd.DataFrame:
        '''
        商品檢查點
        Parameters
        ----------
        :param result: DataFrame

            - 輸入原始表格
            
        :param freq: str

            - 表格頻率
            
        :param num_col: int

            - 數值化資料欄位起點
            
        :param colists: list, default None

            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
            
        :param pd_id: str

            - 商品代碼
            
        Returns
        ----------
        DataFrame
        '''
        try:
            if result.empty:
                print('SidError:',OwlError._dicts["SidError"])
                return result
            
            if result is not 'error':
                # 日期修正
                if freq == 'd':
                    result['日期'] = [pd.to_datetime(i) if i !='' else '' for i in result['日期']]
                    if '股票代號' not in result.columns:
                        result.sort_values('日期', inplace = True)
                        result.reset_index(drop = True, inplace = True)
                        
                elif freq == 'm':
                    result['年月'] = [pd.to_datetime(i,format='%Y%m')+MonthEnd(1) if i !='' else '' for i in result['年月']]
                    if '股票代號' not in result.columns:
                        result.sort_values('年月', inplace = True)
                        result.reset_index(drop = True, inplace = True)
                    
                elif freq == 'q':
                    result['年季'] = result['年季'].apply(lambda x: x[0:4]+x[4:6].replace('0','Q'))
                    result['年季'] = [pd.to_datetime(i)+QuarterEnd(1) if i !='' else '' for i in result['年季']]
                    if '股票代號' not in result.columns:
                        result.sort_values('年季', inplace = True)
                        result.reset_index(drop = True, inplace = True)
                    
                elif freq == 'y':
                    result['年度'] = [pd.to_datetime(i)+YearEnd(1) if i !='' else '' for i in result['年度']]
                    if '股票代號' not in result.columns:
                        result.sort_values('年度', inplace = True)
                        result.reset_index(drop = True, inplace = True)
                
                # 數值化
                if num_col != None:
                    result.iloc[:,num_col:] = result.iloc[:,num_col:].apply(pd.to_numeric)
                
                # 欄位選擇
                if colists != None:
                    result = result[colists].copy()
                    
                elif colists == []:
                    print('ColumnsError: 請輸入欄位')
                    return None

                return result

        except ValueError:
            print('ValueError:', OwlError._dicts["ValueError"])
        except KeyError:
            print('ColumnsError:', OwlError._dicts["ColumnsError"])
        # except AttributeError:
        #     print('CannotFind:', OwlError._dicts['CannotFind'])                  
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 個股日收盤行情 (Single Stock Price)
    def ssp(self, sid:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依指定日期區間，獲取指定股票代號的股價資訊
        
        Parameters
        ----------
        
        :param sid: str
        
            - 台股股票代號
            
        :param bpd: str
        
            - 起始日，格式:yyyymmdd 8碼
            
        :param epd: str
        
            - 結束日，格式:yyyymmdd 8碼
            
        :param colist: list
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
            
        Returns
        ----------
        DataFrame

        Notes
        ----------
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載時間對應表
            self._get_table('d')
            dt = self._date_freq(bpd, epd, 'd')
            
            # 下載付費版
            if (dt != 'error'):
                pdid = self._get_pdid("ssp")
                get_data_url = self._token['data_url']+"date/" + epd + "/" + pdid + "/" + sid + "/" + dt
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    pdid = self._get_pdid_test("ssp")
                    get_data_url = self._token['data_url']+pdid+"/"+sid+"/"+'500'
                    result = self._data_from_owl(get_data_url)
                    

            # 資料修正
            temp = self._check(result = result, freq = 'd', num_col = 2, colists = colist, pd_id = pdid)
            temp = temp[temp['日期'].isin(self._table['d']['日期'])]
            temp = temp[temp[temp.columns[0]].between(bpd, epd)]
            temp.reset_index(drop=True,inplace=True)
            return temp

        except:
            print('PdError:', OwlError._dicts["PdError"])
   
    # 多股每日收盤行情 (Multi Stock Price)
    @OwlError._check_dt(di = 'd')
    def msp(self, dt:str, colist=None) -> pd.DataFrame:
        '''
        依指定日期，獲取全上市櫃台股的股價資訊
        
        Parameters
        ----------
        
        :param dt: str
        
            - 指定一個交易日期，格式:yyyymmdd，8碼
            
        :param colist: list
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空

        '''
        try:
            # 下載付費版
            pdid = self._get_pdid("msp")
            get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
            result = self._data_from_owl(get_data_url)
                
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("msp")
                get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, freq = 'd', num_col = 3, colists = colist, pd_id = pdid)
            return temp
            
        except:
            print('PdError:', OwlError._dicts["PdError"])

    # 個股財務簡表 (Financial Statements Single )
    def fis(self, sid:str, di:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依據 di 決定查詢資料頻率，並依股票代號，獲取指定區間的財務報表資訊
        
        Parameters
        ----------         
        :param sid: str
        
            - 台股股票代號
            
        :param di: str
        
            - 查詢資料時間頻率，y = 年度, q = 季度, m = 月份
            
                - Y : 年度, 格式 : yyyy
                - Q : 季度, 格式 : yyyyqq
                - M : 月, 格式 : yyyymm    
            
        :param bpd: str
        
            - 指定一個交易起始日
            
        :param epd: str
        
            - 指定一個交易結束日
            
        :param colist: list
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 季度日期格式 yyyqq, 其中 qq 請輸入 01 - 04, 分別表示為第一季至第四季 
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空 
        - 參數 di 大小寫無異
        - y(年)、 q(季) 是獲取財務報表資訊; m(月) 是獲取營收相關資訊
        
        '''
        try:
            if di.lower() == 'y':
                pdid = self._get_pdid("sby")
                self._get_table('y')
                dt = self._date_freq(bpd, epd, di.lower())
                get_data_url=self._token['data_url']+"date/"+epd+"0101/"+pdid+"/"+sid+"/"+dt
            
            elif di.lower() == 'q':
                pdid = self._get_pdid("sbq")
                self._get_table('q')
                dt = self._date_freq(bpd, epd, di.lower())
                get_data_url=self._token['data_url']+"date/"+epd+"01/"+pdid+"/"+sid+"/"+dt
                
            elif di.lower() == 'm':
                pdid = self._get_pdid("sbm")
                self._get_table('m')
                dt = self._date_freq(bpd, epd, di.lower())
                get_data_url=self._token['data_url']+"date/"+epd+"01/"+pdid+"/"+sid+"/"+dt

            if (dt != 'error'):
                # 下載付費版
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    if di.lower() == 'y':
                        pdid = self._get_pdid_test("sby")
                        get_data_url=self._token['data_url']+pdid+"/"+sid+"/"+'2'
                        bpd,epd = self._time_format(bpd,epd,'y')
                    
                    elif di.lower() == 'q':
                        pdid = self._get_pdid_test("sbq")
                        get_data_url=self._token['data_url']+pdid+"/"+sid+"/"+'8'
                        bpd,epd = self._time_format(bpd,epd,'q')

                    elif di.lower() == 'm':
                        pdid = self._get_pdid_test("sbm")
                        get_data_url=self._token['data_url']+pdid+"/"+sid+"/"+'24'
                        bpd,epd = self._time_format(bpd,epd,'m')
                        
                    result = self._data_from_owl(get_data_url)
                
                temp = self._check(result = result, freq = di.lower(), num_col = 1, colists = colist, pd_id = pdid)
                temp = temp[temp[temp.columns[0]].between(bpd, epd)]
                temp.reset_index(drop=True,inplace=True)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 多股財務簡表 (Financial Statements Multi)
    @OwlError._check_di
    def fim(self, di:str, dt:str , colist=None) -> pd.DataFrame:
        '''
        依據 di 決定查詢資料頻率，並依指定區間，獲取全上市櫃台股的財務報表資訊
        y(年)、 q(季) 是獲取財務報表資訊；m(月) 是獲取營收相關資訊        
        
        Parameters
        ----------
        :param di: str
        
            - 查詢資料時間頻率，y = 年度, q = 季度, m = 月

        :param dt: str
        
            - 指定一個交易日期，受時間頻率選擇影響
            
                - y : yyyy, 4 碼
                - q : yyyyqq, 6 碼, qq 範圍為 01 - 04, 表示為第一季至第四季
                - m : yyyymm, 6 碼

        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
            - y and q : ['年度', '流動資產', '非流動資產', '資產總計', '流動負債', '非流動負債', '負債總計', '權益總計', '公告每股淨值', '營業收入(千)', '營業成本(千)', '營業毛利(千)', '營業費用(千)', '營業利益(千)', '營業外收入及支出(千)', '稅前純益(千)', '所得稅(千)', '稅後純益歸屬(千)', '每股盈餘(元)', '營業活動現金流量(千)', '投資活動現金流量(千)', '籌資活動現金流量(千)', '本期現金及約當現金增減數(千)', '期末現金及約當現金餘額(千)', '自由現金流量(千)']
            - m : ['股票代號','股票名稱','年月','單月合併營收(千)','去年同期(千)','單月合併營收年成長(%)','單月合併營收月變動(%)','累計合併營收(千)','去年同期(千)1','累計合併營收成長(%)']
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        - 季度日期格式 yyyqq, 其中 qq 請輸入 01 - 04, 分別表示為第一季至第四季 
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空 
        - 參數 di 大小寫無異
        
        '''
        try:
            if di.lower() == 'y':
                pdid = self._get_pdid("mby")
                get_data_url=self._token['data_url']+"date/"+dt+"0101/"+pdid
            
            elif di.lower() == 'q':
                pdid = self._get_pdid("mbq")
                self._get_table('q')

                if int(dt[4:6]) == 1:
                    pass
                elif int(dt[4:6]) == 2:
                    dt = str(int(dt)+2)
                elif int(dt[4:6]) == 3:
                    dt = str(int(dt)+4)
                elif int(dt[4:6]) == 4:
                    dt = str(int(dt)+6)
                
                get_data_url=self._token['data_url']+"date/"+dt+"01/"+pdid
                
            elif di.lower() == 'm':
                pdid = self._get_pdid("mbm")
                self._get_table('m')
                get_data_url=self._token['data_url']+"date/"+dt+"01/"+pdid
                
            # 下載付費版
            if get_data_url:
                result = self._data_from_owl(get_data_url)


                # 下載不到付費板時
                if type(result) == str:
                    if di.lower() == 'y':
                        pdid = self._get_pdid_test("mby")
                        get_data_url=self._token['data_url']+"date/"+dt+"0101/"+pdid
                    
                    elif di.lower() == 'q':
                        pdid = self._get_pdid_test("mbq")
                        get_data_url=self._token['data_url']+"date/"+dt+"01/"+pdid
                        
                    elif di.lower() == 'm':
                        pdid = self._get_pdid_test("mbm")
                        get_data_url=self._token['data_url']+"date/"+dt+"01/"+pdid

                    # 下載免費版
                    result = self._data_from_owl(get_data_url)

                temp = self._check(result = result, freq = di.lower(), num_col = 3, colists = colist, pd_id = pdid)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
        
    # 法人籌碼個股歷史資料 (Corporate Chip Single)
    def chs(self, sid:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依指定日期區間，獲取指定股票的三大法人買賣狀況和該股票的融資券狀況
        
        Parameters
        ----------
        :param sid: str
        
            - 台股股票代號
            
        :param bpd: str
        
            - 指定一個交易起始日，格式:yyyymmdd 8碼
            
        :param epd: str
        
            - 指定一個交易結束日，格式:yyyymmdd 8碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
            
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載時間對應表
            self._get_table('d')
            dt = self._date_freq(bpd, epd, 'd')
            
            if (dt != 'error'):
                # 下載付費版
                pdid = self._get_pdid("sch")
                get_data_url = self._token['data_url']+"date/" + epd + "/" + pdid + "/" + sid + "/" + dt
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    pdid = self._get_pdid_test("sch")
                    get_data_url = self._token['data_url']+pdid+"/"+sid+"/"+'500'
                    result = self._data_from_owl(get_data_url)

                temp = self._check(result = result, freq = 'd', num_col = 1, colists = colist, pd_id = pdid)
                temp = temp[temp[temp.columns[0]].between(bpd, epd)]
                temp.reset_index(drop=True,inplace=True)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])

    # 法人籌碼多股歷史資料 (Corporate Chip Multi)
    @OwlError._check_dt(di = 'd')
    def chm(self, dt:str, colist=None) -> pd.DataFrame:
        '''
        查詢指定日期，全上市櫃台股的三大法人買賣狀況和融資券狀況
        
        Parameters
        ----------
        :param dt: str
        
            - 指定一個交易日期，格式:yyyymmdd，8碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載付費版
            pdid = self._get_pdid("mch")
            get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
            result = self._data_from_owl(get_data_url)
            
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("mch")
                get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, freq = 'd', num_col = 3, colists = colist, pd_id = pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
                       
    # 技術指標 個股 (Technical indicators Single)
    def tis(self, sid:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依指定日期區間，獲取指定股票的技術指標數值
        
        Parameters
        ----------
        
        :param sid: str
        
            - 台股股票代號
            
        :param bpd: str
        
        - 指定一個交易起始日，格式:yyyymmdd 8碼
            
        :param epd: str
        
            - 指定一個交易結束日，格式:yyyymmdd 8碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載時間對應表
            self._get_table('d')
            dt = self._date_freq(bpd, epd, 'd')
            
            if (dt != 'error'):
                # 下載付費版
                pdid=self._get_pdid("sth")
                get_data_url = self._token['data_url']+"date/" + epd + "/" + pdid + "/" + sid + "/" + dt
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    pdid=self._get_pdid_test("sth")
                    get_data_url = self._token['data_url']+pdid+"/"+sid+"/"+'500'
                    result = self._data_from_owl(get_data_url)

                temp = self._check(result = result, freq = 'd', num_col = 1, colists = colist, pd_id = pdid)
                temp = temp[temp[temp.columns[0]].between(bpd, epd)]
                temp.reset_index(drop=True,inplace=True)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
   
    # 技術指標 多股 (Technical indicators Multi) 
    @OwlError._check_dt(di = 'd')
    def tim(self, dt:str, colist=None) -> pd.DataFrame:
        '''
        查詢指定日期，全上市櫃台股的技術指標數值
        
        Parameters
        ----------
        
        :param dt: str
        
            - 指定一個交易日期，格式:yyyymmdd，8碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            pdid = self._get_pdid("mth")
            get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
            result = self._data_from_owl(get_data_url)
            
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("mth")
                get_data_url = self._token['data_url'] + 'date/' + dt + '/' + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, freq = 'd', num_col = 3, colists = colist, pd_id = pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 公司基本資料 多股 (Company information Multi)
    def cim(self, colist=None) -> pd.DataFrame:
        '''
        獲取上市櫃台股的公司基本資料
        
        Parameters
        ----------
        
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame
        
        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載付費版
            pdid = self._get_pdid("mcm")
            get_data_url = self._token['data_url']  + pdid
            result = self._data_from_owl(get_data_url)
            
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("mcm")
                get_data_url = self._token['data_url']  + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, num_col = -1, colists = colist, pd_id = pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 股利政策 個股 (Dividend Policy Single)
    def dps(self, sid:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依據指定年度區間，獲取指定股票的配發股利狀況表
        
        Parameters
        ----------
        :param sid: str
        
            - 台股股票代號
            
        :param bpd: str
        
        - 指定一個交易起始日，格式:yyyy 4碼
            
        :param epd: str
        
            - 指定一個交易結束日，格式:yyyy 4碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空
        
        '''
        try:
            # 下載時間對應表
            self._get_table('y')
            dt = self._date_freq(bpd, epd, 'y')
            
            if (dt != 'error'):
                # 下載付費版
                pdid = self._get_pdid("scm1")
                get_data_url = self._token['data_url']+"date/" + epd + '0101' + "/" + pdid + "/" + sid + "/" + dt
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    pdid = self._get_pdid_test("scm1")
                    get_data_url = self._token['data_url']+pdid+"/"+sid+"/"+'2'
                    result = self._data_from_owl(get_data_url)
                    bpd,epd = self._time_format(bpd,epd,'y')

                temp = self._check(result = result, freq = 'y', num_col = 3, colists = colist, pd_id = pdid)
                temp = temp[temp[temp.columns[0]].between(bpd, epd)]
                temp.reset_index(drop=True,inplace=True)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 股利政策 多股 (Dividend Policy Multi)
    @OwlError._check_dt(di = 'y')
    def dpm(self, dt:str, colist=None) -> pd.DataFrame:
        '''
        依指定年度，獲取全上市櫃台股的配發股利狀況表
        
        Parameters
        ----------
        :param dt: str
        
            - 指定一個交易日期，格式:yyyy 4碼
        
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame
        
        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空

        '''
        try:
            pdid = self._get_pdid("mcm1")
            get_data_url = self._token['data_url'] + 'date/' + dt + '1231/' + pdid
            result = self._data_from_owl(get_data_url)
            
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("mcm1")
                get_data_url = self._token['data_url'] + 'date/' + dt + '1231/' + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, freq = 'y', num_col = 5, colists = colist, pd_id = pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])

    # 除權除息 個股 (Exemption Dividend Policy Single)
    def edps(self, sid:str, bpd:str, epd:str, colist=None) -> pd.DataFrame:
        '''
        依據指定年度區間，獲取指定股票的股東會日期及停止過戶的相關日期
        
        Parameters
        ----------
        :param sid: str
        
            - 台股股票代號
            
        :param bpd: str
        
            - 指定一個交易起始日，格式:yyyy 4碼
            
        :param epd: str
        
            - 指定一個交易結束日，格式:yyyy 4碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
            
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空 
        
        '''
        try:
            # 下載時間對應表
            self._get_table('y')
            dt = self._date_freq(bpd, epd, 'y')
            
            if (dt != 'error'):
                # 下載付費版
                pdid = self._get_pdid("scm2")
                get_data_url = self._token['data_url']+"date/" + epd + '0101' + "/" + pdid + "/" + sid + "/" + dt
                result = self._data_from_owl(get_data_url)
                
                # 下載不到付費板時
                if type(result) == str:
                    pdid = self._get_pdid_test("scm2")
                    get_data_url = self._token['data_url']+pdid+"/"+sid+"/"+'2'
                    result = self._data_from_owl(get_data_url)
                    bpd,epd = self._time_format(bpd,epd,'y')

                temp = self._check(result = result, freq = 'y', num_col = None, colists = colist, pd_id = pdid)
                temp = temp[temp[temp.columns[0]].between(bpd, epd)]
                temp.reset_index(drop=True,inplace=True)
                return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 除權除息 多股 (Exemption Dividend Policy Multi)
    @OwlError._check_dt(di = 'y')   
    def edpm(self, dt:str, colist=None) -> pd.DataFrame:
        '''
        依指定日期，獲取全上市櫃台股的股東會日期及停止過戶的相關日期
        
        Parameters
        ----------
        :param dt: str
        
            - 輸入某一天日期代碼，格式:yyyy 4碼
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空 
        
        '''
        try:
            # 下載付費版
            pdid = self._get_pdid("mcm2")
            get_data_url = self._token['data_url'] + 'date/' + dt + '0101/' + pdid
            result = self._data_from_owl(get_data_url)
            
            # 下載不到付費板時
            if type(result) == str:
                pdid = self._get_pdid_test("mcm2")
                get_data_url = self._token['data_url'] + 'date/' + dt + '0101/' + pdid
                result = self._data_from_owl(get_data_url)

            temp = self._check(result = result, freq = 'y', num_col = None, colists = colist, pd_id = pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
    
    # 即時報價 (Timely Stock Price)
    def tsp(self, sid:str, colist=None) -> pd.DataFrame:
        '''
        獲取指定股票即時股價資訊
        
        Parameters
        ----------
        :param sid: str
        
            - 台股股票代號
            
        :param colist: list, default None
        
            - 填入欲查看的欄位名稱，未寫輸入則取全部欄位
        
        Returns
        ----------
        DataFrame

        Notes
        ----------
        - 發生錯誤時，會直接顯示錯誤訊息，回傳變數為空 
        
        '''
        try:
            # 下載付費版 (僅只有付費版才能使用這項功能)
            pdid = self._get_pdid("mnp")
            get_data_url = self._token['data_url'] + pdid + "/" + sid
            result = self._data_from_owl(get_data_url)
            temp = self._check(result=result, num_col=3, colists=colist, pd_id=pdid)
            return temp
        except:
            print('PdError:', OwlError._dicts["PdError"])
