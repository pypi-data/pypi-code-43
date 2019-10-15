from datanator_query_python.util import mongo_util
from pymongo.collation import Collation, CollationStrength


class QueryCorum:

    def __init__(self, username=None, password=None, server=None, authSource='admin',
                 database='datanator', max_entries=float('inf'), verbose=True, collection_str='corum',
                 readPreference='primary'):
        self.mongo_manager = mongo_util.MongoUtil(MongoDB=server, username=username,
                                             password=password, authSource=authSource, db=database,
                                             readPreference=readPreference)
        self.collation = Collation(locale='en', strength=CollationStrength.SECONDARY)
        self.max_entries = max_entries
        self.verbose = verbose
        self.client, self.db, self.collection = self.mongo_manager.con_db(collection_str)

    def get_complexes_with_uniprot(self, uniprot_id, ncbi_id=9606):
        """Find complexes in species that have protein with uniprot_id
        
        Args:
            uniprot_id (str): uniprot id of protein
            ncbi_id (int, optional): ncbi taxonomy id of species. Defaults to 9606.

        Returns:
            (:obj:`list` of :obj:`dict`): list of complexes that meet the requirement
        """
        result = []
        query = {'$and': [{'SWISSPROT_organism_NCBI_ID': ncbi_id},
                          {'subunits_uniprot_id': uniprot_id}]}
        projection = {'_id': 0}
        docs = self.collection.find(filter=query, projection=projection, collation=self.collation)
        for doc in docs:
            result.append(doc)
        return result

    def get_complexes_with_ncbi(self, ncbi_id, projection = {'_id': 0}):
        """Find all complexes in species with ncbi taxonomy id
        
        Args:
            ncbi (int): ncbi taxonomy id

        Returns:
            (list): list of all objects that meet the constraint
        """
        result = []
        query = {'SWISSPROT_organism_NCBI_ID': ncbi_id}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result