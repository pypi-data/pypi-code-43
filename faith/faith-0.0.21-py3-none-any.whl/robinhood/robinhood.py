from robinhood.lib.account.account import Account


class Robinhood(object):

    def __init__(self) -> None:
        self._account = Account()
