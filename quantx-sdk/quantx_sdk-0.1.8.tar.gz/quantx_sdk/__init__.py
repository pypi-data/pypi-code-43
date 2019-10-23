from quantx_sdk.api import API
from quantx_sdk.root import Root
from quantx_sdk.backtest import Backtest


def QX(public_key,
       secret_key,
       api_entry_point="https://api.quantx.io/public/api/v1",
       websocket_entry_point="wss://ws.quantx.io/ws/v1",
       websocket_timeout=30):
    """QuantX SDKの初期化

        SDKを初期化し、Rootオブジェクトを作成します。

        Parameters
        ----------
        public_key : str
            QuantX Factory で発行したPublic Key
        secret_key : str
            QuantX Factory で発行したSecret Key
        api_entry_point: str
            APIのエントリポイントを指定します。
        websocket_entry_point: str
            Websocketのエントリポイントを指定します。
        websocket_timeout: int
            Websocketのタイムアウト値を指定します(default: 30)

        Returns
        -------
        quantx_sdk.Root

        Examples
        --------
        >>> from quantx_sdk import QX
        >>> qx = QX(publicKey, secretKey)

        """

    Backtest.WEBSOCKET_TIMEOUT = websocket_timeout

    api = API(public_key,
              secret_key,
              api_entry_point=api_entry_point,
              websocket_entry_point=websocket_entry_point)
    return Root(api)
