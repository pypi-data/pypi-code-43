from quantx_sdk.portfolio import Portfolio
import pandas as pd
from quantx_sdk.util import Util
import datetime
import simplejson as json


class Algorithm:
    """
    アルゴリズム情報を管理します。
    """
    def __init__(self, qx, name, origin, owner, live_hash):
        self.qx = qx
        self.name = name
        self.origin = origin
        self.owner = owner
        self.live_hash = live_hash
        self._data = None

    def _get(self):
        if not self._data:
            path = "/live/{}".format(self.live_hash)
            result = self.qx.api(path, {"fetch": "full"})
            self._data = result["result"]
        return self._data

    def signals(self, from_date=None, to_date=None):
        """シグナル情報を取得します。

        取得期間を指定しない場合、最新のシグナルが最大1000件返ります。
        一度に取得できる件数の上限は1000件です。
        期間を指定していても、1000件を超える場合、1000件のみが返ります。

        Parameters
        ----------
        from_date : str
            取得開始日。 YYYY-MM-DD フォーマットで指定。
        to_date: str
            取得終了日。 YYYY-MM-DD フォーマットで指定。

        Returns
        -------
        pandas.DataFrame
            シグナル一覧
        """

        param = {"hashes": [self.live_hash]}
        if from_date is not None:
            param["from"] = from_date
        else:
            td = datetime.timedelta(days=7)
            param["from"] = (datetime.date.today() - td).strftime("%Y-%m-%d")

        if to_date is not None:
            param["to"] = to_date
        else:
            param["to"] = datetime.date.today().strftime("%Y-%m-%d")

        result = self.qx.api_fullpath(
            "https://api.quantx.io/public/api/v2/signal/list", param)

        data = []
        if self.live_hash in result["result"]:
            data = result["result"][self.live_hash]

        columns = [
            "target_date", "symbol", "market_sig", "pos", "neg", "order_type",
            "order_num", "order_comment", "order_params"
        ]
        rows = [[d[c] for c in columns] for d in data]
        df = pd.DataFrame(rows, columns=columns)
        df = Util.convert_df(df,
                             date_columns=["target_date"],
                             number_columns=["pos", "neg", "order_num"])
        return df

    def info(self):
        """アルゴリズム情報を取得します。

        Returns
        -------
        dict
            アルゴリズム情報
        """
        data = self._get()
        info = data["algorithm_info"]
        for k, v in data["bt"].items():
            info[k] = v
        return info

    def summary(self):
        """サマリーを取得します。

        アルゴリズムのMaxDrawdown,Volatility,SharpeRatio等を取得します。

        Returns
        -------
        dict
            アルゴリズム情報
        """
        data = self._get()
        indicators = data["indicator"]
        indicators["TradingDays"] = data["trading_days"]
        indicators["TradedCount"] = data["traded_count"]
        return indicators

    def symbols(self):
        """銘柄一覧を取得します。

        Returns
        -------
        pandas.DataFrame
            銘柄コードがindexのDataFrame。
        """
        data = self._get()
        columns = ["symbol", "name", "sector"]
        rows = []

        for k in sorted(data["master"].keys()):
            d = data["master"][k]
            rows.append([d[c] for c in columns])
        df = pd.DataFrame(rows, columns=columns)
        df = df.set_index("symbol")
        return df

    def orders(self):
        """取引履歴を取得します。

        Returns
        -------
        pandas.DataFrame
            取引履歴
            [ "symbol", "order_type", "ordered_at", "completed_at", "completed_price", "amount", "comission", "comment", "order_params" ]

        """
        data = self._get()

        algoVersion = data["algorithm_info"]["engine_version"]
        if algoVersion == "maron-0.0.1b":
            columns = [
                "symbol", "ordered_at", "completed_at", "completed_price",
                "amount", "comission", "comment", "order_params"
            ]
            rows = [o for o in reversed(data["open_orders"])]
            for orders in reversed(data["complete_orders"]):
                rows.extend([o for o in reversed(orders)])
            for r in rows:
                r.append({})
            df = pd.DataFrame(rows, columns=columns)
            df = Util.convert_df(
                df,
                date_columns=["ordered_at", "completed_at"],
                number_columns=["completed_price", "amount", "comission"])
            df["status"] = "close"
            df["order_type"] = "market_close"
            df.loc[df["completed_price"].isnull(), "status"] = "open"

            return df

        else:
            # maron-0.0.5 or later
            columns = [
                "symbol",
                "order_type",
                "ordered_at",  # "signal_date",
                "completed_at",  # "trade_date",
                "completed_price",
                "amount",
                "comission",
                "comment",
                "order_params"
            ]

            rows = [o for o in reversed(data["open_orders"])]
            for orders in reversed(data["complete_orders"]):
                rows.extend([o for o in reversed(orders)])
            df = pd.DataFrame(rows, columns=columns)
            df = Util.convert_df(
                df,
                date_columns=["ordered_at", "completed_at"],
                number_columns=["completed_price", "amount", "comission"],
            )
            df["status"] = "close"
            df.loc[df["completed_price"].isnull(), "status"] = "open"
            df.loc[df["order_type"] == 1, "order_type"] = "market_close"
            df.loc[df["order_type"] == 2, "order_type"] = "market_open"
            df.loc[df["order_type"] == 3, "order_type"] = "limit"
            return df

    def product(self):
        """商品情報を取得します。

        Returns
        -------
        dict
            商品情報
        """
        return self._get().get("product", {})

    def seller(self):
        """販売者を取得します。

        Returns
        -------
        dict
            販売者情報
        """
        return self._get().get("seller", {})

    def portfolio(self, type=None):
        """ポートフォリオを取得します。

        Returns
        -------
        quantx_sdk.Portfolio
            ポートフォリオオブジェクト
        """
        key = "portfolio"
        if type:
            key += "_" + type
        return Portfolio(self._get()[key])

    def to_dict(self):
        """アルゴリズム情報をdictに変換します。

        Returns
        -------
        dict
        """
        return {
            "name": self.name,
            "origin": self.origin,
            "owner": self.owner,
            "hash": self.live_hash,
        }
