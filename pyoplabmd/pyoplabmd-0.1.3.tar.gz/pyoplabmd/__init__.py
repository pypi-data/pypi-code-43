#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Oplab Finance market data downloader
# https://github.com/marcellopaz
#
# Copyright 2019 Marcello Paz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from collections import namedtuple as _namedtuple
import requests as _requests
import pandas as _pd
import datetime as _datetime
import json

class Config:

    def __init__(self):
        with open('token.json') as json_file:
            data = json.load(json_file)
        self.Token = data["token"]

    def getToken(self):
        return self.Token




class Tickers:
    def __repr__(self):
        return 'pyoplabmd.Tickers object <%s>' % ",".join(self.symbols)

    def __init__(self, tickers):
        tickers = tickers if isinstance(
            tickers, list) else tickers.replace(',', ' ').split()
        self.symbols = [ticker.upper() for ticker in tickers]
        ticker_objects = {}

        for ticker in self.symbols:
            ticker_objects[ticker] = Ticker(ticker)

        self.tickers = _namedtuple(
            "Tickers", ticker_objects.keys(), rename=True
        )(*ticker_objects.values())


class Ticker:

    def __repr__(self):
        return 'pyoplabmd.Ticker object <%s>' % self.ticker

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self._history = None
        self._base_url = 'https://api.oplab.com.br/v2'
        self._scrape_url = 'https://api.oplab.com.br/v2/charts/data'
        config = Config()
        self.__TOKEN = config.getToken()

    def set_token(self, token):
        self.__TOKEN = token

    @property
    def info(self):
        """ retreive metadata and currenct price data """
        "sample: https://api.oplab.com.br/v2/stocks/PETR4"
        headers = {
            "Access-Token": self.__TOKEN,
            "Content-Type": "application/json"}
        url = "{}/stocks/{}".format(
            self._base_url, self.ticker)
        r = _requests.get(url=url, headers=headers)
        rj = {}
        if r.status_code == 200:
            rj = r.json()

        if rj:
            return rj
        return {}

    @staticmethod
    def _parse_quotes(data):
        opens = []
        closes = []
        lows = []
        highs = []
        volumes= []
        dates = []
        for tick in data["data"]:
            str_data = str(tick["time"])[0:10]
            dt_object = _datetime.datetime.fromtimestamp(int(str_data)).strftime("%Y%m%d")
            dates.append(dt_object)
            opens.append(tick["open"])
            closes.append(tick["close"])
            lows.append(tick["low"])
            highs.append(tick["high"])
            volumes.append(tick["volume"])

        quotes = _pd.DataFrame({"Date": dates,
                                "Open": opens,
                                "High": highs,
                                "Low": lows,
                                "Close": closes,
                                "Volume": volumes})

        quotes.sort_index(inplace=True)
        return quotes

    def history(self, interval="1d",
                start=None, end=None):
        """
        :Parameters:
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        """

        if start is None:
            start = "195001010500"
        else:
            start = start + "0500"

        if end is None:
            end = _datetime.date.today().strftime("%Y%m%d")+"2200"
        else:
            end = end + "2200"

        params = {"from": start, "to": end}
        params["interval"] = interval.lower()

        headers = {
            "Access-Token": self.__TOKEN,
            "Content-Type": "application/json"}

        url = "{}/charts/data/{}/{}?from={}&to={}".format(self._base_url, self.ticker, params["interval"],
                                                          params["from"], params["to"])
        r = _requests.get(url=url, headers=headers)
        if r.status_code != 200:
            raise ValueError(self.ticker, r)
            return
        data = r.json()

        # parse quotes
        try:
            quotes = self._parse_quotes(data)
        except Exception:
            raise ValueError(self.ticker, "")

        quotes.dropna(inplace=True)
        self._history = quotes.copy()

        return quotes

