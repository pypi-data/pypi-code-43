#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 12:57:27 2019

@author: patrickmcfarlane

5/18/18 - 8/19/18
5/13/17 - 9/3/17
5/14/16 - 9/18/16
6/5/15 - 9/13/15
5/16/14 - 8/17/14
5/24/13 - 9/15/13
5/18/12 - 9/23/12
6/3/11 - 9/11/11
5/15/10 - 8/22/10
6/6/09 - 9/13/09
5/17/18 - 9/14/08 (14 teams!)

10/16/18 - 4/10/19
10/17/17 - 4/11/18
10/25/16 - 4/12/17
10/27/15 - 4/13/16
10/28/14 - 4/15/15
10/29/13 - 4/16/14
10/30/12 - 4/17/13
12/25/11 - 4/26/12***
10/26/10 - 4/13/11
10/27/09 - 4/14/10

OFF_RATING
DEF_RATING (weighted by lineup usage and availability)
OPP_OFF_RATING (exlcuding games against you)
OPP_DEF_RATING (weighted by lineup usage and availability)
HOME/AWAY
REST
DISTANCE TRAVELED
PREDICTED FOULS (Refs, foul rates, pace)
SCORE HOW (2nd CHANCE, OFF_TOV, PAINT, FB)
OPP SCORE HOW
"""

from vegas import Vegas
from datetime import datetime, timedelta
import pandas as pd
import time

HEADERS = {'Connection': 'close',
           'Host': 'sportsdatabase.com',
           'Origin': 'http://sportsdatabase.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'}

start_date = datetime(2019, 5, 24)
days = 65

full_df = pd.DataFrame()
num_games = 0
for day in range(days + 1):
    date = start_date + timedelta(days=day)
    print(date)
    years = str(date.year)
    if date.month <= 9:
        month = '0' + str(date.month)
    else:
        month = str(date.month)
    if date.day <= 9:
        day_str = '0' + str(date.day)
    else:
        day_str = str(date.day)

    t0 = time.time()
    date_str = years + month + day_str
    data = Vegas(HEADERS, date_str, 'wnba')
    if data.data != {}:
        data_df = pd.DataFrame(data.data)
        print(num_games)
        num_games += len(data_df)
        full_df = pd.concat([full_df, data_df], axis=0)
    delay = time.time() - t0
    print('Waiting ' + str(10*delay) + 's')
    time.sleep(10*delay)

full_df.to_csv('wnba_2019.csv', index=False)