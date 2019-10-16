import botocore, coloredlogs, boto3, json, logging, s3fs, pickle, urllib
import pyarrow.parquet as pq

from foqus.configuration import *
from foqus.database import PostgreSQL

db = PostgreSQL()

if LOCAL is False:

    from azure_storage_logging.handlers import TableStorageHandler

    # configure the handler and add it to the logger
    logger = logging.getLogger(__name__)
    handler = TableStorageHandler(account_name=LOG_AZURE_ACCOUNT_NAME,
                                  account_key=LOG_AZURE_ACCOUNT_KEY,
                                  extra_properties=('%(hostname)s',
                                                    '%(levelname)s'))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
else:

    logger = logging.getLogger(__name__)
    coloredlogs.install()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_PATH + 'trynfit_debug.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s', '%d/%b/%Y %H:%M:%S')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)


def upload_file_into_s3(file, chemin):

    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)
    fichier = file.split('/')[-1]
    file_to_upload = chemin + fichier
    try:
        logger.info('Uploading file into %s' %file_to_upload)
        data = open(file, 'rb')
        s3.Bucket('trynfit-bucket').put_object(Key=file_to_upload, Body=data)
    except Exception as e:
        logger.error('Error in uploading file %s'%e)


def delete_from_s3(file):
    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)
    try:
        s3.Object('trynfit-bucket', file).delete()
        return 0
    except Exception as e:
        logger.error('Error in deleting file %s error is %s' %(file, e))
        return -1


def delete_folder(prefix_to_delete):
    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)
    try:
        objects_to_delete = s3.meta.client.list_objects(Bucket="trynfit-bucket", Prefix=prefix_to_delete)
        delete_keys = {'Objects': []}
        delete_keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects_to_delete.get('Contents', [])]]

        s3.meta.client.delete_objects(Bucket="trynfit-bucket", Delete=delete_keys)
    except Exception as e:
        logger.error("Error deleting directory %s error is %s" % (prefix_to_delete, e))


def list_object_folder(prefix):
    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)
    try:
        objects = s3.meta.client.list_objects(Bucket="trynfit-bucket", Prefix=prefix)

        keys = {'Objects': []}
        keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects.get('Contents', [])]]

        return keys['Objects']
    except Exception as e:
        logger.error("Errorororor %s" % e)


def load_file_from_url(url):
    s3 = s3fs.S3FileSystem(key=AWS_KEY_ID, secret=AWS_SECRET_KEY)
    try:
        vector = pq.ParquetDataset('s3://%s'
                                   % (AWS_STORAGE_BUCKET_NAME + '/' + url),
                                   filesystem=s3).read_pandas().to_pandas()
        return vector
    except Exception as e:
        logger.error('%s file not loaded %s '% (url,e))


def load_file_json_s3(prefix):
    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)
    try:
        content_object = s3.Object('trynfit-bucket', prefix)
        file_content = content_object.get()['Body'].read().decode('utf-8')

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.error("File doen't exist")
        file_content = None
    json_content = json.loads(file_content)
    return json_content


def load_pickle_file(prefix):
    base_url = 'https://s3.eu-central-1.amazonaws.com/trynfit-bucket/'
    file = urllib.request.urlopen(base_url + prefix)
    old_list = pickle.load(file)
    return old_list


def list_subdirectories(prefix):
    import boto3
    s3 = boto3.resource('s3', aws_access_key_id=AWS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_KEY)

    caractere_to_split = prefix.split('/')[-1]
    if caractere_to_split == "":
        caractere_to_split = prefix.split('/')[-2]
    subdirectories=[]
    objects = s3.meta.client.list_objects(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
    keys = {'Objects': []}
    keys['Objects'] = [{'Key': k} for k in [obj['Key'] for obj in objects.get('Contents', [])]]
    for key in keys['Objects']:
        project = key['Key'].split('/')[-2]
        if project not in subdirectories:
            subdirectories.append(project)
    return subdirectories


def load_vectors_from_s3(vectors, users):
    for user in users:
        vector_path = VECTORS_S3 + str(user[8]) + '/' + str(user[1]) + '/'
        try:
            vectors_client = list_object_folder(vector_path)
            for vector in vectors_client:
                vector_name = vector['Key'].split('.parquet')[0].split('/')[-1]
                if vector_name:
                    project_name = vector_name.split('_')[0]
                    if int(db.get_status_project('status_projects', user[1], user[8], 'similars', project_name)[0]) == 2:
                        if vector_name not in vectors.keys():
                            logger.info('Vector to load  =====> %s' % (vector['Key'].split('.parquet')[0] + '.parquet'))
                            vector_data = load_file_from_url(vector['Key'].split('.parquet')[0]+'.parquet')
                            if vector_data is not None:
                                vectors[vector_name] = vector_data
                                logger.info('Vector %s  loaded successfully for client %s '
                                        % (vector_name, str(user[1])))
                            else:
                                logger.info(
                                'Vector %s not loaded for client %s vector is None' % (vector['Key'].split('.parquet')[0].split('/')[-1]
                                                                                  , str(user[1])))
        except Exception as e:
            logger.warning("Can't get the parquet file for client %s with domaine %s error %s" % (str(user[1]), str(user[8]), e))
    logger.info("Vectors keys : %s" % vectors.keys())
    return vectors

