from datanator_query_python.util import chem_util, file_util
from . import query_nosql
from pymongo.collation import Collation, CollationStrength


class QueryPax(query_nosql.DataQuery):
    '''Queries specific to pax collection
    '''

    def __init__(self, cache_dirname=None, MongoDB=None, replicaSet=None, db='datanator',
                 collection_str='pax', verbose=False, max_entries=float('inf'), username=None,
                 password=None, authSource='admin', readPreference='primary'):
        """Instantiating query_pax
        
        Args:
            cache_dirname (str, optional): temparory cache director. Defaults to None.
            MongoDB (str, optional): mongodb server address. Defaults to None.
            replicaSet (str, optional): name of mongodb replicaset. Defaults to None.
            db (str, optional): name of database in which pax collection resides. Defaults to 'datanator'.
            collection_str (str, optional): name of collection. Defaults to 'pax'.
            verbose (bool, optional): display verbose messages. Defaults to False.
            max_entries (float, optional): max number of operations, mainly used for tests. Defaults to float('inf').
            username (str, optional): db authentication username. Defaults to None.
            password (str, optional): db authentication password. Defaults to None.
            authSource (str, optional): authentication database. Defaults to 'admin'.
            readPreference (str, optional): mongodb readpreference. Defaults to 'primary'.
        """
        super(query_nosql.DataQuery, self).__init__(cache_dirname=cache_dirname, MongoDB=MongoDB,
                                                    replicaSet=replicaSet, db=db,
                                                    verbose=verbose, max_entries=max_entries, username=username,
                                                    password=password, authSource=authSource, readPreference=readPreference)
        self.collation = Collation(locale='en',
                                   strength=CollationStrength.SECONDARY)
        self.chem_manager = chem_util.ChemUtil()
        self.file_manager = file_util.FileUtil()
        self.max_entries = max_entries
        self.verbose = verbose
        self.client, self.db_obj, self.collection = self.con_db(collection_str)

    def get_all_species(self):
        '''
            Get a list of all species in pax collection

            Returns:
                results (:obj:`list` of :obj:`str`): list of specie names
                                            with no duplicates
        '''
        results = []
        query = {}
        projection = {'species_name': 1}
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            results.append(doc['species_name'])
        return list(set(results))

    def get_abundance_from_uniprot(self, uniprot_id):
        '''
            Get all abundance data for uniprot_id

            Args:
                uniprot_id (:obj:`str`): protein uniprot_id.

            Returns:
                result (:obj:`list` of :obj:`dict`): result containing
                [{'ncbi_taxonomy_id': , 'species_name': , 'ordered_locus_name': },
                {'organ': , 'abundance'}, {'organ': , 'abundance'}].
        '''
        query = {'observation.protein_id.uniprot_id': uniprot_id}
        projection = {'ncbi_id': 1, 'species_name': 1,
                      'observation.$': 1, 'organ': 1}
        collation = Collation(locale='en', strength=CollationStrength.SECONDARY)
        docs = self.collection.find(filter=query, projection=projection, collation=collation)
        count = self.collection.count_documents(query)
        try:
            result = [{'ncbi_taxonomy_id': docs[0]['ncbi_id'],
            'species_name': docs[0]['species_name']}]
        except IndexError:
            return []
        for i, doc in enumerate(docs):
            if i > self.max_entries:
                break
            if self.verbose and i % 50 == 0:
                print('Processing pax document {} out of {}'.format(i, count))
            organ = doc['organ']
            abundance = doc['observation'][0]['abundance']
            ordered_locus_name = doc['observation'][0]['string_id']
            result[0]['ordered_locus_name'] = ordered_locus_name
            dic = {'organ': organ,
            'abundance': abundance}
            result.append(dic)
        return result

    def get_file_by_name(self, file_name: list, projection={'_id': 0}, collation=None) -> list:
        """Given file name, get the information attached to the file.   
        
        Args:
            file_name (:obj:`list`): list of file names, e.g. ['9606/9606-iPS_(DF19.11)_iTRAQ-114_Phanstiel_2011_gene.txt']
        
        Returns:
            :obj:`list`: files that meet the requirement
        """
        result = []
        if collation is None:
            collation = self.collation
        query = {'file_name': {'$in': file_name}}
        projection = projection
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result

    def get_file_by_ncbi_id(self, taxon: list, projection={'_id': 0}, collation=None) -> list:    
        """Given the list of taxon ncbi ID, get all the files associated to the taxon.   
        
        Args:
            taxon (:obj:`list`): list of taxon ncbi ID
        
        Returns:
            :obj:`list`: files that meet the requirement 
        """
        result = []
        if collation is None:
            collation = self.collation
        query = {'ncbi_id': {'$in': taxon}}
        projection = projection
        docs = self.collection.find(filter=query, projection=projection)
        for doc in docs:
            result.append(doc)
        return result

    def get_file_by_quality(self, organ, score=4.0, coverage=20, ncbi_id=None,
                            projection={'_id': 0, 'weight': 0}):
        """Get 'organ's' paxdb file by quality of data
        
        Args:
            organ (:obj:`str`): organ type in paxdb, e.g. WHOLE_ORGANISM, CELL_LINE, etc
            score (:obj:`float`, optional): paxdb data quality score. Defaults to 4.0.
            coverage (:obj:`int`, optional): paxdb data coverage. Defaults to 20.
            ncbi_id (:obj:`int`, optional): ncbi taxonomy id of organism. Defaults to None.
            projection (:obj:`dict`, optional): mongodb query projection. Defaults to {'_id': 0, 'weight': 0}

        Returns:
            (:obj:`tuple`): tuple containing:
                docs (:obj:`Interator`): mongodb docs interator;
                count (:obj:`int`): total number of documents that meet the query conditions.
        """
        constraint_0 = {'organ': organ}
        constraint_1 = {'score': {'$gte': score}}
        constraint_2 = {'coverage': {'$gte': coverage}}
        if ncbi_id is not None:
            constraint_3 = {'ncbi_id': ncbi_id}
        else:
            constraint_3 = {'ncbi_id': {'$exists': True}}
        query = {'$and': [constraint_0, constraint_1, constraint_2, constraint_3]}
        docs = self.collection.find(filter=query, projection=projection)
        count = self.collection.count_documents(query)
        return docs, count

    def get_file_by_publication(self, publication, projection={'_id': 0}):
        """Get documents by publication
        
        Args:
            publication (:obj:`str`): URL of publication
            projection (:obj:`dict`, optional): mongodb query projection. Defaults to {'_id': 0}.

        Returns:
            (:obj:`tuple`): tuple containing:
                docs (:obj:`Interator`): mongodb docs interator;
                count (:obj:`int`): total number of documents that meet the query conditions.
        """
        query = {'publication': publication}
        docs = self.collection.find(filter=query, projection=projection)
        count = self.collection.count_documents(query)
        return docs, count

    def get_file_by_organ(self, organ, projection={'_id': 0}):
        """Get documents by organ
        
        Args:
            organ (:obj:`str`): organ type in paxdb
            projection (dict, optional): mongodb query projection. Defaults to {'_id': 0}.

        Returns:
            (:obj:`tuple`): tuple containing:
                docs (:obj:`Interator`): mongodb docs interator;
                count (:obj:`int`): total number of documents that meet the query conditions.
        """
        query = {'organ': organ}
        docs = self.collection.find(filter=query, projection=projection)
        count = self.collection.count_documents(query)
        return docs, count