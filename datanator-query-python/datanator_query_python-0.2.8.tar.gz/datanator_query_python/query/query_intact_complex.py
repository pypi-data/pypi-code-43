from datanator_query_python.util import mongo_util
from pymongo.collation import Collation, CollationStrength


class QueryIntactComplex:

    def __init__(self, username=None, password=None, server=None, authSource='admin',
                 database='datanator', max_entries=float('inf'), verbose=True, collection_str='intact_complex',
                 readPreference='primary'):
        self.mongo_manager = mongo_util.MongoUtil(MongoDB=server, username=username,
                                             password=password, authSource=authSource, db=database,
                                             readPreference=readPreference)
        self.collation = Collation(locale='en', strength=CollationStrength.SECONDARY)
        self.max_entries = max_entries
        self.verbose = verbose
        self.client, self.db, self.collection = self.mongo_manager.con_db(collection_str)

    def get_complex_with_ncbi(self, ncbi):
        """Get complexes that are in species with ncbi id
        
        Args:
            ncbi (int): ncbi taxonomy id of species

        Returns:
            (:obj:`list` of :obj:`dict`): list of complexes
        """
        result = []
        query = {'ncbi_id': ncbi}
        projection = {'_id': 0}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result