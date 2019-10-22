import lazy_import
import re
boto3 = lazy_import.lazy_module('boto3')
import futsu.aws as faws
io = lazy_import.lazy_module('io')
botocore_exceptions = lazy_import.lazy_module('botocore.exceptions')

BUCKET_PATH_FORMAT = 's3://([^/]+)/?'
BUCKET_PATH_FORMAT_RE = None
def init_BUCKET_PATH_FORMAT_RE():
    global BUCKET_PATH_FORMAT_RE
    if BUCKET_PATH_FORMAT_RE is None:
        BUCKET_PATH_FORMAT_RE = re.compile(BUCKET_PATH_FORMAT)

BLOB_PATH_FORMAT = 's3://([^/]+)/(.+)'
BLOB_PATH_FORMAT_RE = None
def init_BLOB_PATH_FORMAT_RE():
    global BLOB_PATH_FORMAT_RE
    if BLOB_PATH_FORMAT_RE is None:
        BLOB_PATH_FORMAT_RE = re.compile(BLOB_PATH_FORMAT)

def is_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    return BUCKET_PATH_FORMAT_RE.fullmatch(path) is not None

def is_blob_path(path):
    init_BLOB_PATH_FORMAT_RE()
    return BLOB_PATH_FORMAT_RE.fullmatch(path) is not None

def prase_bucket_path(path):
    init_BUCKET_PATH_FORMAT_RE()
    m = BUCKET_PATH_FORMAT_RE.fullmatch(path)
    if not m: raise ValueError()
    return m.group(1)

def prase_blob_path(path):
    init_BLOB_PATH_FORMAT_RE()
    m = BLOB_PATH_FORMAT_RE.fullmatch(path)
    if not m: raise ValueError()
    return m.group(1), m.group(2)

def create_client(region_name=None):
    if region_name == None:
        if faws.default_region_name != None:
            region_name = faws.default_region_name
    return boto3.client('s3')

#def bucket(gs_path, client):
#    bucket_name = prase_bucket_path(gs_path)
#    return client.bucket(bucket_name)

#def blob(gs_path, client):
#    bucket_name, blob_name = prase_blob_path(gs_path)
#    return client.bucket(bucket_name).blob(blob_name)

def file_to_blob(dst,src,client):
    dst_bucket_name, dst_object_key = prase_blob_path(dst)
    client.upload_file(
        Filename = src,
        Bucket = dst_bucket_name,
        Key = dst_object_key,
    )

def blob_to_file(dst,src,client):
    src_bucket_name, src_object_key = prase_blob_path(src)
    client.download_file(
        Filename = dst,
        Bucket = src_bucket_name,
        Key = src_object_key,
    )

def bytes_to_blob(dst,bytes,client):
    dst_bucket_name, dst_object_key = prase_blob_path(dst)
    with io.BytesIO(bytes) as bout:
        client.upload_fileobj(
            Fileobj = bout,
            Bucket = dst_bucket_name,
            Key = dst_object_key,
        )

def blob_to_bytes(src,client):
    src_bucket_name, src_object_key = prase_blob_path(src)
    with io.BytesIO() as bin:
        client.download_fileobj(
            Fileobj = bin,
            Bucket = src_bucket_name,
            Key = src_object_key,
        )
        bytes = bin.getvalue()
    return bytes

def string_to_blob(dst,s,client):
    bytes_to_blob(dst,s.encode('utf8'),client)

def blob_to_string(src,client):
    return blob_to_bytes(src,client).decode('utf8')

def is_blob_exist(path,client):
    bucket_name, object_key = prase_blob_path(path)
    try:
        client.head_object(
            Bucket=bucket_name,
            Key=object_key,
        )
        return True
    except botocore_exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise e
    assert(False)

def blob_rm(path,client):
    bucket_name, object_key = prase_blob_path(path)
    client.delete_object(
        Bucket = bucket_name,
        Key = object_key,
    )
