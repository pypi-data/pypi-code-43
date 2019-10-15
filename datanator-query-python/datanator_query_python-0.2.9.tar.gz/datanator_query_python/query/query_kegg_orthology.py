from datanator_query_python.util import mongo_util


class QueryKO:

    def __init__(self, username=None, password=None, server=None, authSource='admin',
                 database='datanator', max_entries=float('inf'), verbose=True,
                 readPreference='primary'):

        mongo_manager = mongo_util.MongoUtil(MongoDB=server, username=username,
                                             password=password, authSource=authSource, db=database,
                                             readPreference=readPreference)
        self.max_entries = max_entries
        self.verbose = verbose
        self.client, self.db, self.collection = mongo_manager.con_db(
            'kegg_orthology_new')

    def get_ko_by_name(self, name):
        '''Get a gene's ko number by its gene name

        Args:
            name: (:obj:`str`): gene name
                
        Returns:
            result: (:obj:`str`): ko number of the gene
        '''
        query = {'gene_name': name}
        projection = {'gene_name': 1, 'kegg_orthology_id': 1}
        collation = {'locale': 'en', 'strength': 2}
        docs = self.collection.find_one(
            filter=query, projection=projection, collation=collation)
        if docs != None:
        	return docs['kegg_orthology_id']
        else:
        	return None

    def get_def_by_kegg_id(self, kegg_id):
        """Get kegg definition by kegg id
        
        Args:
            kegg_id (:obj:`str`): kegg orthology

        Returns:
            (:obj:`list` of :obj:`str`): list of kegg orthology definitions
        """
        query = {'kegg_orthology_id': kegg_id}
        projection = {'definition.name': 1, '_id': 0}
        doc = self.collection.find_one(filter=query, projection=projection)
        if doc is None:
            return [None]
        definitions = doc['definition']['name']
        return definitions