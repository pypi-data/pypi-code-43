from unittest import TestCase
import futsu.aws.s3 as fstorage
import futsu.fs as ffs
import tempfile
import os
#from google.cloud import storage as gcstorage
import time

class TestStorage(TestCase):

    def test_is_bucket_path(self):
        self.assertTrue(fstorage.is_bucket_path('s3://bucket'))
        self.assertTrue(fstorage.is_bucket_path('s3://bucket/'))

        self.assertFalse(fstorage.is_bucket_path('s3://bucket//'))
        self.assertFalse(fstorage.is_bucket_path('s3://bucket/asdf'))
        self.assertFalse(fstorage.is_bucket_path('s3://bucket/asdf/'))
        self.assertFalse(fstorage.is_bucket_path('s3://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_bucket_path('s://bucket'))
        self.assertFalse(fstorage.is_bucket_path('3://bucket'))
        self.assertFalse(fstorage.is_bucket_path('s3//bucket'))
        self.assertFalse(fstorage.is_bucket_path('s3:/bucket'))
        self.assertFalse(fstorage.is_bucket_path('s3://'))
        self.assertFalse(fstorage.is_bucket_path('s3:///'))
        self.assertFalse(fstorage.is_bucket_path('s3:///asdf'))

    def test_is_blob_path(self):
        self.assertFalse(fstorage.is_blob_path('s3://bucket'))
        self.assertFalse(fstorage.is_blob_path('s3://bucket/'))

        self.assertTrue(fstorage.is_blob_path('s3://bucket//'))
        self.assertTrue(fstorage.is_blob_path('s3://bucket/asdf'))
        self.assertTrue(fstorage.is_blob_path('s3://bucket/asdf/'))
        self.assertTrue(fstorage.is_blob_path('s3://bucket/asdf/asdf'))

        self.assertFalse(fstorage.is_blob_path('s://bucket'))
        self.assertFalse(fstorage.is_blob_path('3://bucket'))
        self.assertFalse(fstorage.is_blob_path('s3//bucket'))
        self.assertFalse(fstorage.is_blob_path('s3:/bucket'))
        self.assertFalse(fstorage.is_blob_path('s3://'))
        self.assertFalse(fstorage.is_blob_path('s3:///'))
        self.assertFalse(fstorage.is_blob_path('s3:///asdf'))

    def test_parse_bucket_path(self):
        self.assertEqual(fstorage.prase_bucket_path('s3://asdf'),'asdf')
        self.assertRaises(ValueError,fstorage.prase_bucket_path,'asdf')

    def test_prase_blob_path(self):
        self.assertEqual(fstorage.prase_blob_path('s3://asdf/qwer'),('asdf','qwer'))
        self.assertEqual(fstorage.prase_blob_path('s3://asdf/qwer/'),('asdf','qwer/'))
        self.assertRaises(ValueError,fstorage.prase_blob_path,'asdf')

    def test_gcp_string(self):
        timestamp = int(time.time())
        tmp_gs_path  = 's3://futsu-test/test-PPCFADJEPR-{0}'.format(timestamp)

        client = fstorage.create_client()
        fstorage.string_to_blob(tmp_gs_path,'NSODRIGNUR',client)
        s = fstorage.blob_to_string(tmp_gs_path,client)
        self.assertEqual(s,'NSODRIGNUR')

    def test_gcp_file(self):
        client = fstorage.create_client()
        with tempfile.TemporaryDirectory() as tempdir:
            timestamp = int(time.time())
            src_fn = os.path.join('futsu','gcp','test','test_storage.txt')
            tmp_gs_path  = 's3://futsu-test/test-TOPTSPZHLZ-{0}'.format(timestamp)
            tmp_filename = os.path.join(tempdir,'QDVBADVVVW')
            
            fstorage.file_to_blob(tmp_gs_path,src_fn,client)
            fstorage.blob_to_file(tmp_filename,tmp_gs_path,client)
            
            self.assertFalse(ffs.diff(src_fn,tmp_filename))

    def test_exist(self):
        timestamp = int(time.time())
        tmp_gs_path  = 's3://futsu-test/test-YYAZXVHGVW-{0}'.format(timestamp)

        client = fstorage.create_client()
        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path,client))
        fstorage.string_to_blob(tmp_gs_path,'EYKVKUAUNU',client)
        self.assertTrue(fstorage.is_blob_exist(tmp_gs_path,client))

    def test_delete(self):
        timestamp = int(time.time())
        tmp_gs_path  = 's3://futsu-test/test-WABWGQVWRP-{0}'.format(timestamp)

        client = fstorage.create_client()

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path,client))

        fstorage.blob_rm(tmp_gs_path,client)

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path,client))

        fstorage.string_to_blob(tmp_gs_path,'RPUBYBJZSN',client)
        self.assertTrue(fstorage.is_blob_exist(tmp_gs_path,client))

        fstorage.blob_rm(tmp_gs_path,client)

        self.assertFalse(fstorage.is_blob_exist(tmp_gs_path,client))
