import lazy_import
fgcpstorage = lazy_import.lazy_module('futsu.gcp.storage')
gcstorage = lazy_import.lazy_module('google.cloud.storage')
fs3 = lazy_import.lazy_module('futsu.aws.s3')
ffs = lazy_import.lazy_module('futsu.fs')

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
    ffs.cp(dst,src)
