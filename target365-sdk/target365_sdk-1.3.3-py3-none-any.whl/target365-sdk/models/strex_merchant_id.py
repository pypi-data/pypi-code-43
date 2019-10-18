class StrexMerchantId:
    def fromDict(self, dict):
        self.merchantId = dict["merchantId"]
        self.shortNumberId = dict["shortNumberId"]
        self.password = dict["password"]
    
    def fromResponseList(self, listOfStrexMerchantIds):
        items = []
        for item in listOfStrexMerchantIds:
            strexMerchantId = StrexMerchantId()
            strexMerchantId.fromDict(item)
            items.append(strexMerchantId)

        return items
