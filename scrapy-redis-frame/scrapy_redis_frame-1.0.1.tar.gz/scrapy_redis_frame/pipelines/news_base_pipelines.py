from scrapy_redis_frame.common_utils.mongo_util import MongoUtil


class NewsBasePipelines(object):

    def __init__(self, mongo_db_url, mongo_db_name, mongo_collection_name):
        self.mongo_collection_name = mongo_collection_name
        self.mongo_util = MongoUtil(mongo_db_url, mongo_db_name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_db_url=crawler.settings.get('MONGO_DB_URL'),
            mongo_db_name=crawler.settings.get('MONGO_DB_NAME'),
            mongo_collection_name=crawler.settings.get('MONGO_COLLECTION_NAME')
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.mongo_util.insertRecord(self.mongo_collection_name, dict(item))
