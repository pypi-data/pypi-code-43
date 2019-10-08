# encoding=utf-8

import os
import json
import zipfile
import pandas as pd
import numpy as np
import alphalens as al
from datetime import datetime
from dateutil.parser import parse

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.abspath(os.path.dirname(CUR_PATH))




def unzip_news_files(zipfile_dir_path, unzip_to_dir_path='./unzipped_files'):
    """
    zipfile_dir_path: folder path of the original zipped files
    unzip_to_dir_path: defalut './unzipped_files'. destination folder for the unzipped files
    """
    for f in os.listdir(zipfile_dir_path):
        f_path = os.path.join(zipfile_dir_path, f)
        if zipfile.is_zipfile(f_path):
            to_unzip = zipfile.ZipFile(f_path)
            to_unzip.extractall(path=unzip_to_dir_path)
            to_unzip.close()

    print('Successfully Unzip files to {}'.format(unzip_to_dir_path))


def extract_news_info_from_json(news_json, filed=None):
    """
    extract basic news data from any piece of news data
    :param news_json: dict, one piece of news data
    :param filed: str or list, default None to extract all the fileds.
                  The filed to be extracted.it could be any of ['newsId','newsTitle','newsTs','newsUrl','newsSource','newsSummary']
    :return: dict
    """
    info_data = news_json['newsInfo']

    if isinstance(filed, str):
        filed = [filed]

    if not filed:
        ret = info_data

    else:
        ret = {k: v for k, v in info_data.items() if k in filed}

    return ret


def extract_tag_info_from_json(news_json, tag_type=None, filed=None, df=False):
    """
    extract tag data from any piece of news data
    :param news_json:
    :param tag_type:
    :param filed:
    :param df:
    :return:
    """

    if isinstance(tag_type, str):
        tag_type = [tag_type]

    tag_data = news_json['newsTags']

    ret = []

    if tag_data:

        if not tag_type:
            ret = tag_data

        else:
            ret = [tag for tag in tag_data if tag['itemType'] in tag_type]

        if filed:
            ret = [{k: v for k, v in d.items() if k in filed} for d in ret]

        if df:
            ret = pd.DataFrame(ret)

    return ret


def extract_senti_info_from_json(news_json, filed=None, senti_type=None, df=False):
    """

    :param news_json:
    :param filed:
    :param senti_type:
    :param df:
    :return:
    """

    if isinstance(senti_type, str):
        senti_type = [senti_type]

    senti_data = news_json['emotionInfos']

    ret = []

    if senti_data:

        if not senti_type:
            ret = senti_data

        else:
            ret = [senti for senti in senti_data if senti['emotionEntity'] in senti_type]

        if filed:
            ret = [{k: v for k, v in d.items() if k in filed} for d in ret]

        if df:
            ret = pd.DataFrame(ret)

    return ret


def extract_senti_info_from_file(file_path, news_filed=None, senti_filed=None, senti_type='Company', df=False):
    """

    :param file_path:
    :param news_filed: ['newsId','newsTitle','newsTs','newsUrl','newsSource','newsSummary']
    :param senti_filed: ['emotionEntity','entityRefId','emotionIndicator','emotionWeight','emotionDetail','emotionAlgoVersion']
    :param senti_type: ['Company','News']
    :return: pd.DataFrame
    """

    with open(file_path, 'r') as news_f:
        file_lines = news_f.readlines()
        ret = []
        for file_line in file_lines:
            news_json = json.loads(file_line)
            news_info = extract_news_info_from_json(news_json, filed=news_filed)
            senti_info = extract_senti_info_from_json(news_json, filed=senti_filed, senti_type=senti_type, df=False)
            if senti_info:
                [i.update(news_info) for i in senti_info]
                ret.extend(senti_info)
    if df:
        ret = pd.DataFrame(ret)

    return ret


def extract_tag_info_from_file(file_path, news_filed=None, tag_filed=None, tag_type='Company', df=False):
    """

    :param file_path:
    :param news_filed: ['newsId','newsTitle','newsTs','newsUrl','newsSource','newsSummary']
    :param tag_filed: ['itemType','itemName_cn','itemName','itemId','itemAlgoVersion','ItemExtId','ItemRelevance']
    :param tag_type: ['Company',''Product','Concept','Event','Industry']
    :return: pd.DataFrame
    """
    with open(file_path, 'r') as news_f:
        file_lines = news_f.readlines()
        ret = []
        for file_line in file_lines:
            news_json = json.loads(file_line)
            news_info = extract_news_info_from_json(news_json, filed=news_filed)
            tag_info = extract_tag_info_from_json(news_json, filed=tag_filed, tag_type=tag_type, df=False)
            if tag_info:
                [i.update(news_info) for i in tag_info]
                ret.extend(tag_info)

    if df:
        ret = pd.DataFrame(ret)

    return ret


def extract_data_from_files(folder_path, extract_func, **kwargs):
    """
    extract data by extrac_func from multiple files
    :param folder_path: str. the folder which used to save news files
    :param extract_func: function. the extract function used to extract data
    :return: pd.DataFrame
    """

    df_lst = []

    for f in os.listdir(folder_path):
        if f.split('.')[-1] == 'txt':
            f_path = os.path.join(folder_path, f)
            temp_df = extract_func(f_path, **kwargs)
            df_lst.append(temp_df)

    ret = pd.concat(df_lst)
    sort_by = kwargs.get('sort_by')

    if sort_by:
        ret = ret.sort_values(by=sort_by, ascending=True)

    ret = ret.reset_index(drop=True)
    return ret


def align_trade_date(df_raw, date_col, cut_hour=15, cut_minute=0, trade_calendar=None):
    """
    align calendar date to trade date. As default, the news after 15:00 will align to the next nearest trading date
    :param df_raw: pd.DataFrame. raw data with datetime column 'date_col'
    :param date_col: string. the column name of datetime column
    :param cut_hour: int, default 15. the news released after this time is aligned to the next nearest trading date
    :param cut_minute: int, default 0. same as above
    :param trade_calendar: list, default None for China A-Share Market trade calendar. The trade_calendar used to align
                           the data.

    :return: df_raw with one more column 'trade_date'

    """

    start_date = df_raw[date_col].min()
    start_date = start_date.strftime("%Y-%m-%d")

    end_date = df_raw[date_col].max()
    end_date = end_date.strftime("%Y-%m-%d")

    if not trade_calendar:
        data_path = os.path.join(ROOT_PATH, "data/trade_calendar_zh.csv")
        dts = pd.read_csv(data_path, index_col=0)
        dts_arr = dts['date'].values

    else:
        dts_arr = np.array(trade_calendar)

    st_idx = np.searchsorted(dts_arr, start_date)
    et_idx = np.searchsorted(dts_arr, end_date)

    trade_dts = [parse(dt).date() for dt in dts_arr[st_idx - 1:et_idx + 2]]
    ti = datetime(2019, 1, 1, hour=cut_hour, minute=cut_minute).time()
    trade_dts = [datetime.combine(dt, ti) for dt in trade_dts]
    ts_trade_dts = pd.Series(trade_dts)
    trade_date = pd.cut(df_raw[date_col].astype(np.int64) // 10 ** 9,
                        bins=ts_trade_dts.astype(np.int64) // 10 ** 9)
    trade_date = pd.to_datetime([it.right for it in trade_date], unit='s')
    df_raw['trade_date'] = pd.to_datetime(pd.DatetimeIndex(trade_date).date)

    return df_raw


def filter_by_listed_days(fac_df, days=20):
    """
    filter the stock which listed less than #days from the factor data.
    :param fac_df: multi-index pd.DataFrame. The level0 index is date and level1 index is sec_code
    :param days: int, defalut 20.
    :return: pd.DataFrame
    """

    def _combine_list_days(df):
        def _cal_days(code):
            dates = list_dts_dct.get(code)
            if not dates:
                return -1
            elif dates[0] > dt or dates[1] < dt:
                return -1
            else:
                days = (dt - dates[0]).days
                return days

        dt = df.index.get_level_values(level=0).unique()[0]
        if isinstance(dt, str):
            dt = parse(dt).date()
        df = df.reset_index(level=0, drop=True)
        df['list_days'] = [_cal_days(code) for code in df.index]

        return df
    if isinstance(fac_df, pd.Series):
        fac_df = fac_df.to_frame()
        fac_df.columns = ['factor']
    data_path = os.path.join(ROOT_PATH, "data/stock_list_dates.csv")
    list_dts = pd.read_csv(data_path, index_col=0,
                           parse_dates=['list_date', 'dlist_date'])
    list_dts_dct = {k[1]['sec_code']: (k[1]['list_date'], k[1]['dlist_date']) for k in list_dts.iterrows()}
    fac_df = fac_df.groupby(level=0).apply(_combine_list_days)
    fac_df = fac_df.query("list_days > @days")

    if isinstance(fac_df, pd.Series):
        fac_df = fac_df['factor']

    return fac_df


def prepare_data_for_alphalens(fac_data,
                               groupby=None,
                               binning_by_group=False,
                               quantiles=None,
                               bins=10,
                               periods=(1, 5, 10),
                               filter_zscore=None,
                               groupby_labels=None,
                               max_loss=3,
                               zero_aware=False,
                               cumulative_returns=True
                               ):
    fac_data.index = fac_data.index.set_levels(
        fac_data.index.levels[0].tz_localize(None),
        level=0)
    data_path = os.path.join(ROOT_PATH, "data/stock_price_data.csv")
    price_data = pd.read_csv(data_path, index_col=0)
    price_data.index = pd.DatetimeIndex(price_data.index, tz=None)
    price_data.index = pd.DatetimeIndex(price_data.index)
    fac_data = al.utils.get_clean_factor_and_forward_returns(fac_data,
                                                             price_data,
                                                             groupby,
                                                             binning_by_group,
                                                             quantiles,
                                                             bins,
                                                             periods,
                                                             filter_zscore,
                                                             groupby_labels,
                                                             max_loss,
                                                             zero_aware,
                                                             cumulative_returns)

    return fac_data


