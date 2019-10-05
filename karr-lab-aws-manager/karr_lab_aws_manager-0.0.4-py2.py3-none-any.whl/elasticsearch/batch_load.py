from datanator_query_python.query import query_protein
from datanator_query_python.config import config as config_mongo
from karr_lab_aws_manager.elasticsearch import util


class MongoToES(util.EsUtil):

    def __init__(self, profile_name=None, credential_path=None,
                config_path=None, elastic_path=None,
                cache_dir=None, service_name='es', index=None, max_entries=float('inf'), verbose=False):
        ''' 
            Args:
                profile_name (:obj: `str`): AWS profile to use for authentication
                credential_path (:obj: `str`): directory for aws credentials file
                config_path (:obj: `str`): directory for aws config file
                elastic_path (:obj: `str`): directory for file containing aws elasticsearch service variables
                cache_dir (:obj: `str`): temp directory to store json for bulk upload
                service_name (:obj: `str`): aws service to be used
        '''
        super().__init__(profile_name=profile_name, credential_path=credential_path,
                config_path=config_path, elastic_path=elastic_path,
                cache_dir=cache_dir, service_name=service_name, max_entries=max_entries, verbose=verbose)
        self.index = index


    def data_from_mongo_protein(self, server, db, username, password, verbose=False,
                                readPreference='nearest', authSource='admin', projection={'_id': 0},
                                query={}):
        ''' Acquire documents from protein collection in datanator
            Args:
                server (:obj: `str`): mongodb ip address
                db (:obj: `str`): database name
                username (:obj: `str`): username for mongodb login
                password (:obj: `str`): password for mongodb login
                verbose (:obj: `bool`): display verbose messages
                readPreference (:obj: `str`): mongodb readpreference
                authSource (:obj: `str`): database login info is authenticating against
                projection (:obj: `str`): mongodb query projection
                query (:obj: `str`): mongodb query filter
            Return:
                docs (:obj: `pymongo.Cursor`): pymongo cursor object that points to all documents in protein collection
                count (:obj: `int`): number of documents returned
        '''
        protein_manager = query_protein.QueryProtein(server=server, database=db,
                 verbose=verbose, username=username, authSource=authSource,
                 password=password, readPreference=readPreference)
        docs = protein_manager.collection.find(filter=query, projection=projection)
        count = protein_manager.collection.count_documents(query)
        return (count, docs)


def main():
    conf = config_mongo.Config()
    username = conf.USERNAME
    password = conf.PASSWORD
    server = conf.SERVER
    authDB = conf.AUTHDB
    db = 'datanator'
    manager = MongoToES(verbose=True)
    
    # data from "protein" collection
    count, docs = manager.data_from_mongo_protein(server, db, username, password, authSource=authDB)
    status_code = manager.data_to_es_bulk(count, docs) 
    
    print(status_code)   

if __name__ == "__main__":
    main()