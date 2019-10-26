import lazy_import
fgcpstorage = lazy_import.lazy_module('futsu.gcp.storage')
gcstorage = lazy_import.lazy_module('google.cloud.storage')
fs3 = lazy_import.lazy_module('futsu.aws.s3')
ffs = lazy_import.lazy_module('futsu.fs')
urllib_request = lazy_import.lazy_module('urllib.request')
shutil = lazy_import.lazy_module('shutil')

def local_to_path(dst, src):
    if fgcpstorage.is_blob_path(dst):
        gcs_client = gcstorage.client.Client()
        fgcpstorage.file_to_blob(dst, src, gcs_client)
        return
    if fs3.is_blob_path(dst):
        client = fs3.create_client()
        fs3.file_to_blob(dst, src, client)
        return
    ffs.cp(dst,src)

def path_to_local(dst, src):
    if fgcpstorage.is_blob_path(src):
        gcs_client = gcstorage.client.Client()
        fgcpstorage.blob_to_file(dst, src, gcs_client)
        return
    if fs3.is_blob_path(src):
        client = fs3.create_client()
        fs3.blob_to_file(dst, src, client)
        return
    if src.startswith('https://') or src.endswith('http://'):
        with urllib_request.urlopen(src) as w_in, open(dst, 'wb') as f_out:
            shutil.copyfileobj(w_in, f_out)
        return
    ffs.cp(dst,src)

def bytes_to_path(dst, bytes):
    if fgcpstorage.is_blob_path(dst):
        gcs_client = gcstorage.client.Client()
        fgcpstorage.bytes_to_blob(dst, bytes, gcs_client)
        return
    if fs3.is_blob_path(dst):
        client = fs3.create_client()
        fs3.bytes_to_blob(dst, bytes, client)
        return
    ffs.bytes_to_file(dst,bytes)

def path_to_bytes(src):
    if fgcpstorage.is_blob_path(src):
        gcs_client = gcstorage.client.Client()
        return fgcpstorage.blob_to_bytes(src, gcs_client)
    if fs3.is_blob_path(src):
        client = fs3.create_client()
        return fs3.blob_to_bytes(src, client)
    if src.startswith('https://') or src.endswith('http://'):
        with urllib_request.urlopen(src) as w_in:
            return w_in.read()
    return ffs.file_to_bytes(src)
