import datetime
from pymongo import MongoClient


class NeoIngest(object):

    def __init__(self, hostname, protocol='mongodb+srv', username='switcheo', password='switcheo', port='27017', database='neo'):
        self.mongo_connection_string = protocol + '://' + username + ':' + password + '@' + hostname + ':' + port + '/' + database
        self.mongo_client = MongoClient(self.mongo_connection_string)
        self.mongo_db = self.mongo_client['neo']

    def mongo_upsert_one(self, collection, upsert_dict):
        update_query = {'_id': upsert_dict['_id']}
        if collection == 'blocks':
            update_query = {'_id': upsert_dict['index']}
            upsert_dict['_id'] = upsert_dict['index']
        elif collection == 'transactions':
            update_query = {'_id': upsert_dict['transaction_hash']}
            upsert_dict['_id'] = upsert_dict['transaction_hash']
        update_values = {'$set': upsert_dict}
        self.mongo_db[collection].update_one(filter=update_query,
                                             update=update_values,
                                             upsert=True)

    def mongo_upsert_many(self, collection, upsert_list_dict):
        bulk = self.mongo_db[collection].initialize_unordered_bulk_op()
        count = 0
        batch_size = 500
        for upsert_dict in upsert_list_dict:
            if collection == 'blocks':
                update_query = {'_id': upsert_dict['index']}
                upsert_dict['_id'] = upsert_dict['index']
                upsert_dict['block_date'] = datetime.datetime.utcfromtimestamp(upsert_dict['time']).strftime('%Y-%m-%d')
            elif collection in ['transactions', 'fees', 'freezes']:
                update_query = {'_id': upsert_dict['transaction_hash']}
                upsert_dict['_id'] = upsert_dict['transaction_hash']
            elif '_id' in upsert_dict:
                update_query = {'_id': upsert_dict['_id']}
            bulk.find(update_query).upsert().replace_one(upsert_dict)
            count += 1
            if count % batch_size == 0:
                bulk.execute()
                bulk = self.mongo_db[collection].initialize_unordered_bulk_op()
        if count % batch_size != 0:
            bulk.execute()

    def get_collection_count(self, collection):
        return self.mongo_db[collection].count()

    def get_missing_blocks(self, block_height, block_offset, blocks_ingested, blocks_ingested_list):
        missing_blocks = set()
        block_height_offset = block_height - block_offset
        missing_block_count = block_height_offset - blocks_ingested
        if missing_block_count > 0:
            all_blocks = set(range(block_offset, block_height + 1))
            missing_blocks = all_blocks.difference(blocks_ingested_list)
        return list(missing_blocks)
