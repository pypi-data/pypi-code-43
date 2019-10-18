class OutMessage:
    def fromDict(self, dictionaryItem):

        self.transactionId = dictionaryItem["transactionId"]
        # self.correlationId = dictionaryItem["correlationId"]
        # self.keywordId = dictionaryItem["keywordId"]
        self.sender = dictionaryItem["sender"]
        self.recipient = dictionaryItem["recipient"]
        self.content = dictionaryItem["content"]
        self.sendTime = dictionaryItem["sendTime"]
        self.timeToLive = dictionaryItem["timeToLive"]
        self.priority = dictionaryItem["priority"]
        self.deliveryMode = dictionaryItem["deliveryMode"]
        
        # only used for STREX messages
        self.merchantId = dictionaryItem.get("merchantId", None)
        self.serviceCode = dictionaryItem.get("serviceCode", None)
        self.invoiceText = dictionaryItem.get("invoiceText", None)
        self.price = dictionaryItem.get("price", None)
        
        # self.deliveryReportUrl = dictionaryItem["deliveryReportUrl"]
        self.lastModified = dictionaryItem["lastModified"]
        self.created = dictionaryItem["created"]
        self.statusCode = dictionaryItem["statusCode"]
        # self.delivered = dictionaryItem["delivered"]
        # self.billed = dictionaryItem["billed"]
        self.tags = dictionaryItem["tags"]
