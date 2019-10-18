from .model import Model

class OneTimePassword(Model):

    def _accepted_params(self):
        return [
            'transactionId',
            'merchantId',
            'recipient',
            'sender',
            'recurring',
            'message',
            'timeToLive',
            'created',
            'delivered',
        ]
