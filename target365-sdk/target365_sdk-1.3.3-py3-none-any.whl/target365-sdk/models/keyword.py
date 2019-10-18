class Keyword:

    def fromDict(self, dictionaryItem):
        self.keywordId = dictionaryItem["keywordId"]
        self.shortNumberId = dictionaryItem["shortNumberId"]
        self.keywordText = dictionaryItem["keywordText"]
        self.mode = dictionaryItem["mode"]
        self.forwardUrl = dictionaryItem["forwardUrl"]
        self.enabled = dictionaryItem["enabled"]
        self.created = dictionaryItem["created"]
        self.lastModified = dictionaryItem["lastModified"]
        self.tags = dictionaryItem["tags"]
        self.customProperties = dictionaryItem.get("customProperties", None)

    def fromResponseList(self, listOfKeywords):
        items = []
        for item in listOfKeywords:
            keyword = Keyword()
            keyword.fromDict(item)
            items.append(keyword)

        return items
