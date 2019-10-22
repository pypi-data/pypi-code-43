from datanator_query_python.util import mongo_util
from pymongo.collation import Collation, CollationStrength


class QueryEcmdb:

    def __init__(self, username=None, password=None, server=None, authSource='admin',
                 database='datanator', max_entries=float('inf'), verbose=True, collection_str='ecmdb',
                 readPreference='primary'):
        self.mongo_manager = mongo_util.MongoUtil(MongoDB=server, username=username,
                                             password=password, authSource=authSource, db=database,
                                             readPreference=readPreference)
        self.collation = Collation(locale='en', strength=CollationStrength.SECONDARY)
        self.max_entries = max_entries
        self.verbose = verbose
        self.client, self.db, self.collection = self.mongo_manager.con_db(collection_str)

    def get_all_concentrations(self, projection={'_id': 0, 'inchi': 1,
                              'inchikey': 1, 'smiles': 1, 'name': 1}):
        """Get all entries that have concentration values
        
        Args:
            projection (dict, optional): mongodb query projection. Defaults to {'_id': 0, 'inchi': 1,'inchikey': 1, 'smiles': 1, 'name': 1}.

        Returns:
            (list): all results that meet the constraint.
        """
        result = []
        query = {'concentrations': {'$exists': True} }
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result
