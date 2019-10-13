from __future__ import absolute_import
import requests
import logging


from soofa.transaction import Transaction

__all__ = ["Soofa"]

logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)

class Soofa(object):
    TRANSACTION_DOES_NOT_EXIST = 404
    PERMISSION_DENIED = 403
    SUCCESSFUL = 200

    def __init__(self, till_no, client_secret):
        self.till_no = str(int(till_no))
        self.client_secret = client_secret
        self.transaction = None
        self.status = None

    def find(self, tid):
        url = 'https://api.soofapay.com/v1/transactions/%s/' % tid
        r = requests.get(
            url, headers={
                "Authorization": "Token %s" % self.client_secret,
                "X-TILL": self.till_no
        })
        self.status = r.status_code
        if self.status == self.SUCCESSFUL:
            data = r.json()
            self.transaction = Transaction(**data)
            return True
        self.__raise403(self.status)
        if self.status == self.TRANSACTION_DOES_NOT_EXIST:
            logging.warning("The transaction %s does not exist" % tid)
        return False

    def __raise403(self, status_code):
        if status_code==403:
            raise PermissionError("Your are not allowed to perform this action. Please ensure you use your "
                              "correct till number and client_secret")

    def get_transaction(self):
        if self.transaction is None:
            raise UserWarning("A transaction is not available yet. Please ensure you call find method and verify "
                            "that one exists before proceeding")
        return self.transaction

    def get_balance(self):
        url = "https://api.soofapay.com/v1/balance/"
        r = requests.get(
            url, headers={
                "Authorization": "Token %s" % self.client_secret,
                "X-TILL": self.till_no
        })
        self.__raise403(r.status_code)
        return r.json()


if __name__ == '__main__':
    soofa = Soofa("5005", '1zjmqsomeaxx8j8nqrn3t9oc1ee4ig')
    print(soofa.get_balance())
    exists = soofa.find("QTMB6")
    if exists:
        transaction = soofa.get_transaction()
        print(transaction.json())
