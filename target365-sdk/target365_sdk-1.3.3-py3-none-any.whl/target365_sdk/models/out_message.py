from .model import Model
from .out_message_strex import OutMessageStrex

class OutMessage(Model):

    def _init_preprocess(self, args):

        # NOTE args.strex could already be a model (passed in by programmer to construsctor)
        # or it could be a dict (passed during JSON deserialization process also via constructor)
        # In this case we will convert it to a model

        if 'strex' in args:
            if type(args['strex']) != OutMessageStrex:
                strex = OutMessageStrex(**args['strex'])
                setattr(self, 'strex', strex)
                del args['strex']

        return args


    def _accepted_params(self):
        return [
            'transactionId',
            'correlationId',
            'keywordId',
            'sender',
            'recipient',
            'content',
            'strex', # OutMessageStrex class
            'allowUnicode', # TRUE to allow unicode SMS, FALSE to fail if content is unicode, NULL to replace unicode chars to '?'
            'sendTime',
            'timeToLive',
            'priority',
            'deliveryMode',
            'deliveryReportUrl',
            'statusCode',
            'smscTransactionId',
            'detailedStatusCode',
            'delivered',
            'smscMessageParts',
            'tags',
            'properties',
            'lastModified',
            'created',
        ]
