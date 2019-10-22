from datanator_query_python.util import mongo_util, chem_util, file_util
from . import query_nosql
import json

class QuerySabioOld(query_nosql.DataQuery):
    '''Queries specific to sabio_rk collection
    '''

    def __init__(self, cache_dirname=None, MongoDB=None, replicaSet=None, db='datanator',
                 collection_str='sabio_rk_old', verbose=False, max_entries=float('inf'), username=None,
                 password=None, authSource='admin'):
        self.max_entries = max_entries
        super(query_nosql.DataQuery, self).__init__(cache_dirname=cache_dirname, MongoDB=MongoDB,
                                        replicaSet=replicaSet, db=db,
                                        verbose=verbose, max_entries=max_entries, username=username,
                                        password=password, authSource=authSource)
        self.chem_manager = chem_util.ChemUtil()
        self.file_manager = file_util.FileUtil()
        self.client, self.db_obj, self.collection = self.con_db(collection_str)

    def get_kinlaw_by_environment(self, taxon=None, taxon_wildtype=None, ph_range=None, temp_range=None,
                          name_space=None, observed_type=None, projection={'_id': 0}):
        """get kinlaw info based on experimental conditions
        
        Args:
            taxon (:obj:`list`, optional): list of ncbi taxon id
            taxon_wildtype (:obj:`list` of :obj:`bool`, optional): True indicates wildtype and False indicates mutant
            ph_range (:obj:`list`, optional): range of pH
            temp_range (:obj:`list`, optional): range of temperature
            name_space (:obj:`dict`, optional): cross_reference key/value pair, i.e. {'ec-code': '3.4.21.62'}
            observed_type (:obj:`list`, optional): possible values for parameters.observed_type
            projection (:obj:`dict`, optional): mongodb query result projection

        Returns:
            (:obj:`tuple`) consisting of 
            docs (:obj:`list` of :obj:`dict`): list of docs;
            count (:obj:`int`): number of documents found 
        """
        all_constraints = []
        taxon_wildtype = [int(x) for x in taxon_wildtype]
        if taxon:
            all_constraints.append({'taxon_id': {'$in': taxon}})
        if taxon_wildtype:
            all_constraints.append({'taxon_wildtype': {'$in': taxon_wildtype}})
        if ph_range:
            all_constraints.append({'ph': {'$gte': ph_range[0], '$lte': ph_range[1]}})
        if temp_range:
            all_constraints.append({'temperature': {'$gte': temp_range[0], '$lte': temp_range[1]}})
        if name_space:
            key = list(name_space.keys())[0]
            val = list(name_space.values())[0]
            all_constraints.append({"resource": {'$elemMatch': {'namespace': key, 'id': val}}})
        if observed_type:
            all_constraints.append({'parameter': {'$elemMatch': {'sbo_type': {'$in': observed_type}}}})

        query = {'$and': all_constraints}
        docs = self.collection.find(filter=query, projection=projection)
        count = self.collection.count_documents(query)
        return docs, count

    def get_reaction_doc(self, kinlaw_id, projection={'_id': 0}):
        '''Find a document on reaction with the kinlaw_id
        Args:
            kinlaw_id (:obj:`list` of :obj:`int`) list of kinlaw_id to search for
            projection (:obj:`dict`): mongodb query result projection

        Returns:
            (:obj:`tuple`) consisting of 
            docs (:obj:`list` of :obj:`dict`): list of docs;
            count (:obj:`int`): number of documents found
        '''
        query = {'kinlaw_id': {'$in': kinlaw_id}}
        docs = self.collection.find(filter=query, projection=projection)
        count = self.collection.count_documents(query)
        return docs, count

    def get_kinlawid_by_rxn(self, substrates, products):
        ''' Find the kinlaw_id defined in sabio_rk using 
            rxn participants' inchi string

            Args:
                substrates: list of substrates' inchi
                products: list of products' inchi

            Return:
                rxns: list of kinlaw_ids that satisfy the condition
                [id0, id1, id2,...,  ]
        '''
        result = []
        substrate = 'reaction_participant.substrate.substrate_structure.InChI_Key'
        product = 'reaction_participant.product.product_structure.InChI_Key'
        projection = {'kinlaw_id': 1, '_id': 0}
        constraint_0 = {substrate: {'$in': substrates}}
        constraint_1 = {product: {'$in': products}}
        query = {'$and': [constraint_0, constraint_1]}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc['kinlaw_id'])
        return result