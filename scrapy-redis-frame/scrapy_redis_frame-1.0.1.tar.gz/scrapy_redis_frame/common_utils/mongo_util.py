from pymongo import MongoClient


class MongoUtil(object):

    def __init__(self, mongoUrl, dbName):
        self.client = MongoClient(mongoUrl)
        self.db = self.client[dbName]

    def __del__(self):
        self.client.close()

    def insertRecord(self, collectionName, record):
        self.db[collectionName].insert(record)

    def selectByCondition(self, collectionName, condition):
        return self.db[collectionName].find(condition)

    def updateRecord(self, collectionName, condition, updateData):
        return self.db[collectionName].update(condition, {'$set': updateData})

    def selectByPage(self, collectionName, condition, pageIndex, pageSize):
        return self.db[collectionName].find(condition).skip(pageSize * pageIndex - 1).limit(pageSize)
