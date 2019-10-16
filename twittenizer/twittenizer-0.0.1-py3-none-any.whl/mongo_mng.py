from pymongo import MongoClient
from typing import List

CONFIG = {
    "_id": "foo",
    "members": [
        {"_id": 0, "host": "localhost:27017"},
        {"_id": 1, "host": "localhost:27018"},
        {"_id": 2, "host": "localhost:27019"},
    ],
}


class MongoMng(object):
    def __init__(self, parameter_list):
        self.connection = None

    @classmethod
    def config_replica(cls, config=CONFIG, host="localhost", port=27017) -> None:
        client = MongoClient(host, port)
        response = client.admin.command("replSetInitiate", config)
        print(response)

    @classmethod
    def connect_db(
        cls,
        host="localhost",
        port=27017,
        replicaset="foo",
        name="twitter",
        collection="tweet",
    ) -> None:
        client = MongoClient(host, port)
        db = client[name]
        connect = db[collection]
        return connect

    @classmethod
    def insert(
        cls, tweet_id_str: str, tweet_date: str, tokens: List[str], tags: List[str]
    ):
        # TODO: Check if the database is available and in replica mode

        # TODO: Insert data in JSON format
        # post = {
        #     "created_at":
        # }
        pass


"""
# Get a MongoClient object
connectionObject = MongoClient("mongodb://localhost:27017/")

# Access the database using object.attribute notation
databaseObject = connectionObject.sample

# Access the mongodb collection using object.attribute notation
collectionObject = databaseObject.test

# insert a simple json document into the test collection
collectionObject.insert({"red": 123, "green": 223, "blue": 23})
collectionObject.insert({"red": 146, "green": 46, "blue": 246})

# Using find() query all the documents from the collection
for document in collectionObject.find():
    # print each document
    print(document)
"""
