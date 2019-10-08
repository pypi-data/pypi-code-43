from datanator_query_python.util import mongo_util, chem_util, file_util
from . import query_nosql
import json

class QuerySabio(query_nosql.DataQuery):
    '''Queries specific to sabio_rk collection
    '''

    def __init__(self, cache_dirname=None, MongoDB=None, replicaSet=None, db='datanator',
                 collection_str='sabio_rk_new', verbose=False, max_entries=float('inf'), username=None,
                 password=None, authSource='admin'):
        self.max_entries = max_entries
        super(query_nosql.DataQuery, self).__init__(cache_dirname=cache_dirname, MongoDB=MongoDB,
                                        replicaSet=replicaSet, db=db,
                                        verbose=verbose, max_entries=max_entries, username=username,
                                        password=password, authSource=authSource)
        self.chem_manager = chem_util.ChemUtil()
        self.file_manager = file_util.FileUtil()
        self.client, self.db_obj, self.collection = self.con_db(collection_str)

    def get_reaction_doc(self, kinlaw_id):
        '''
            Find a document on reaction with the kinlaw_id
            Args:
                kinlaw_id (:obj:`list` of :obj:`int`) list of kinlaw_id to search for
            Returns:
                result (:obj:`list` of :obj:`dict`): list of docs
        '''
        projection = {'_id': 0}
        query = {'kinlaw_id': {'$in': kinlaw_id}}
        result = []
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            to_append = json.dumps(doc, indent=4, sort_keys=True, default=str)
            result.append(json.loads(to_append))
        return result

    def find_reaction_participants(self, kinlaw_id):
        ''' Find the reaction participants defined in sabio_rk using kinetic law id
            Args:
                kinlaw_id (:obj:`list` of :obj:`int`) list of kinlaw_id to search for
            Return:
                rxns (:obj:`list` of :obj:`dict`) list of dictionaries containing names of reaction participants
                [{'substrates': [], 'products': [] }, ... {} ]
        '''
        projection = {'products': 1, 'reactants': 1, '_id': 0, 'kinlaw_id':1}
        if isinstance(kinlaw_id, list):
            query = {'kinlaw_id': {'$in': kinlaw_id}}
        else:
            query = {'kinlaw_id': kinlaw_id}
        docs = self.collection.find(filter=query, projection=projection)
        rxns = []
        i = 0
        for doc in docs:
            if i == self.max_entries:
                break
            if i % 10 == 0:
                print('Finding reaction participants for kinlaw_id {} ...'.format(
                    doc['kinlaw_id']))

            substrates = self.file_manager.get_val_from_dict_list(doc.get('reactants',), 'name')
            products = self.file_manager.get_val_from_dict_list(doc.get('products',), 'name')

            rxn = {'substrates': substrates, 'products': products}

            rxns.append(rxn)
            i += 1

        return rxns

    def get_kinlawid_by_inchi(self, hashed_inchi):
        ''' Find the kinlaw_id defined in sabio_rk using 
            rxn participants' inchi string
            Args:
                inchi (:obj:`list` of :obj:`str`): list of inchi, all in one rxn
            Return:
                rxns (:obj:`list` of :obj:`int`): list of kinlaw_ids that satisfy the condition
                [id0, id1, id2,...,  ]
        '''
        # hashed_inchi = [self.chem_manager.inchi_to_inchikey(s)
        #                 for s in inchi]
        substrate = 'reactants.structures.InChI_Key'
        product = 'products.structures.InChI_Key'
        projection = {'kinlaw_id': 1}

        id_tally = []
        for inchi in hashed_inchi:
            ids = []
            query = {'$or': [{substrate: inchi}, {product: inchi}]}
            cursor = self.collection.find(filter=query, projection=projection)
            for doc in cursor:
                ids.append(doc['kinlaw_id'])
            id_tally.append(ids)

        return list(set(id_tally[0]).intersection(*id_tally))

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

        def get_kinlawid(hashed_inchi, side='substrate'):
            ''' Find the kinlaw_id defined in sabio_rk using 
                rxn participants' inchi string
                Args:
                    inchi: list of inchi, all in one rxn, on one side
                Return:
                    rxns: list of kinlaw_ids that satisfy the condition
                    [id0, id1, id2,...,  ]
            '''

            substrate = 'reactants.structures.InChI_Key'
            product = 'products.structures.InChI_Key'
            projection = {'kinlaw_id': 1, '_id': 0}

            id_tally = []
            if side == 'substrate':
                for inchi in hashed_inchi:
                    ids = []
                    query = {substrate: inchi}
                    cursor = self.collection.find(
                        filter=query, projection=projection)
                    for doc in cursor:
                        ids.append(doc['kinlaw_id'])
                    id_tally.append(ids)

                return list(set(id_tally[0]).intersection(*id_tally))
            else:

                for inchi in hashed_inchi:
                    ids = []
                    query = {product: inchi}
                    cursor = self.collection.find(
                        filter=query, projection=projection)
                    for doc in cursor:
                        ids.append(doc['kinlaw_id'])
                    id_tally.append(ids)

                return list(set(id_tally[0]).intersection(*id_tally))

        sub_id = get_kinlawid(substrates, side='substrate')
        pro_id = get_kinlawid(products, side='product')
        result = list(set(sub_id) & set(pro_id))

        return result

    def get_kinlawid_by_name(self, substrates, products):
        '''
            Get kinlaw_id from substrates and products, all in one reaction
            Args:
                substrates: (:obj:`list` of :obj:`str`): list of substrate names
                products: (:obj:`list` of :obj:`str`): list of product names
            Returns:
                result: (:obj:`list` of :obj:`str`): list of compound names
        '''
        collation = {'locale': 'en', 'strength': 2}
        projection = {'_id': 0, 'products': 1, 'reactants': 1, 'kinlaw_id': 1}

        def get_kinlawid(compounds, side='substrate'):
            ''' Find the kinlaw_id defined in sabio_rk using 
                rxn participants' name
                Args:
                    compounds (:obj:`list` of :obj:`str`): compound names all in one rxn, on one side
                    side (:obj:`str`): left side or right side of the rxn
                Return:
                    rxns: list of kinlaw_ids that satisfy the condition
                    [id0, id1, id2,...,  ]
            '''
            substrates = 'reactants.name'
            products = 'products.name'
            projection = {'kinlaw_id': 1, '_id': 0}

            id_tally = []
            if side == 'substrate':
                for name in compounds:
                    ids = []
                    query = {substrates: name}
                    cursor = self.collection.find(
                        filter=query, projection=projection, collation=collation)
                    for doc in cursor:
                        ids.append(doc['kinlaw_id'])
                    id_tally.append(ids)

                return list(set(id_tally[0]).intersection(*id_tally))
            else:

                for name in compounds:
                    ids = []
                    query = {products: name}
                    cursor = self.collection.find(
                        filter=query, projection=projection, collation=collation)
                    for doc in cursor:
                        ids.append(doc['kinlaw_id'])
                    id_tally.append(ids)

                return list(set(id_tally[0]).intersection(*id_tally))

        if substrates == None:
            sub_id = self.collection.distinct('kinlaw_id')
        else:
            sub_id = get_kinlawid(substrates, side='substrate')

        if products == None:
            pro_id = self.collection.distinct('kinlaw_id')
        else:
            pro_id = get_kinlawid(products, side='product')
            
        result = list(set(sub_id) & set(pro_id))

        return result

    def get_h1_hesc_kinlaw(self, ph_range: list, temp_range: list,
                          name_space: dict, observed_type: list, projection={'_id': 0}):
        """get kinlaw info for h1_hesc
        
        Args:
            ph_range (list): range of pH
            temp_range (list): range of temperature
            name_space (dict): cross_reference key/value pair, i.e. {'ec-code': '3.4.21.62'}
            observed_type (list): possible values for parameters.observed_type
            projection (dict): mongodb query result projection

        Returns:
            (list): list of kinetic laws that meet the constraints 
        """
        result = []
        constraint_0 = {'temperature': {'$gte': temp_range[0], '$lte': temp_range[1]} }
        constraint_1 = {'ph': {'$gte': ph_range[0], '$lte': ph_range[1]} }
        key = list(name_space.keys())[0]
        val = list(name_space.values())[0]
        field = 'cross_references' + '.' + key
        constraint_2 = {field: val}
        constraint_3 = {'parameters.observed_type': {'$in': observed_type} }
        query = {'$and': [constraint_0, constraint_1, constraint_2, constraint_3]}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result