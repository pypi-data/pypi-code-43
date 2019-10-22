import pymongo

class QueryBasicUsers:
    '''Queries specific to registered_users database
    '''

    def __init__(self, MongoDB=None, db='registered_users', collection_str='basic_accounts', verbose=False, 
                 max_entries=float('inf'), username=None,
                 password=None, authSource='registered_users', readPreference='primary'):
        self.client = pymongo.MongoClient(
            MongoDB, username=username, password=password,
            authSource=authSource, authMechanism='SCRAM-SHA-256',
            tz_aware=True, readPreference=readPreference) 
        self.db = self.client[db]
        self.collection = self.db[collection_str]
        
    def get_username_from_id(self, _id):
        ''' 
            Given a list of user ids, find corresponding usernames
            Args: 
                id (:obj:`list` of :obj:`ObjectId`): list of user ids
            Returns:
                results (:obj:`list` of :obj:`str`): list of usernames
        '''
        results = []
        query = {'_id': {'$in': _id}}
        projection = {'username': 1}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            results.append(doc['username'])
            
        return results

    def get_userid_from_username(self, username):
        ''' 
            Given a list of user usernames, find corresponding ids
            Args: 
                id (:obj:`list` of :obj:`str`): list of usernames
            Returns:
                results (:obj:`list` of :obj:`int`): list of user_ids
        '''
        results = []
        query = {'username': {'$in': username }}
        projection = {'_id': 1}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            results.append(doc['_id'])
            
        return results