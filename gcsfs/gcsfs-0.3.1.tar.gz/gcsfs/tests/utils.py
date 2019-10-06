from contextlib import contextmanager
import gzip
import json
import os
import shutil
import re
import pytest
import pickle
import sys
import tempfile
import vcr

from gcsfs.core import GCSFileSystem
from gcsfs.tests.settings import (TEST_BUCKET, TEST_PROJECT, RECORD_MODE,
                                  GOOGLE_TOKEN, FAKE_GOOGLE_TOKEN, DEBUG)

import vcr
import requests
import logging

if DEBUG:
    logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from vcrpy
    vcr_log = logging.getLogger("vcr")
    vcr_log.setLevel(logging.DEBUG)


def before_record_response(response):
    r = pickle.loads(pickle.dumps(response))
    for field in ['Alt-Svc', 'Date', 'Expires', 'X-GUploader-UploadID']:
        r['headers'].pop(field, None)
    if 'Location' in r['headers']:
        r['headers']['Location'] = [r['headers']['Location'][0].replace(
            TEST_BUCKET, 'gcsfs-testing')]
    try:
        try:
            data = json.loads(gzip.decompress(r['body']['string']).decode())
            if 'access_token' in data:
                data['access_token'] = 'xxx'
            if 'id_token' in data:
                data['id_token'] = 'xxx'
            if 'refresh_token' in data:
                data['refresh_token'] = 'xxx'
            r['body']['string'] = gzip.compress(
                    json.dumps(data).replace(
                            TEST_PROJECT, 'test_project').replace(
                        TEST_BUCKET, 'gcsfs-testing').encode())
        except (OSError, TypeError, ValueError):
            r['body']['string'] = r['body']['string'].replace(
                    TEST_PROJECT.encode(), b'test_project').replace(
                        TEST_BUCKET.encode(), b'gcsfs-testing')
    except Exception:
        pass
    return r


def before_record(request):
    r = pickle.loads(pickle.dumps(request))
    for field in ['User-Agent']:
        r.headers.pop(field, None)
    r.uri = request.uri.replace(TEST_PROJECT, 'test_project').replace(
        TEST_BUCKET, 'gcsfs-testing')
    if r.body:
        for field in FAKE_GOOGLE_TOKEN:
            r.body = r.body.replace(FAKE_GOOGLE_TOKEN[field].encode(), b'xxx')
        r.body = r.body.replace(TEST_PROJECT.encode(), b'test_project').replace(
                        TEST_BUCKET.encode(), b'gcsfs-testing')
        r.body = re.sub(b'refresh_token=[^&]+', b'refresh_token=xxx', r.body)
    return r


def matcher(r1, r2):
    if r2.uri.replace(TEST_PROJECT, 'test_project').replace(
            TEST_BUCKET, 'gcsfs-testing') != r1.uri:
        return False
    if r1.method != r2.method:
        return False
    if r1.method != 'POST' and r1.body != r2.body:
        return False
    if r1.method == 'POST':
        try:
            return json.loads(r2.body.decode()) == json.loads(r1.body.decode())
        except:
            pass
        r1q = (r1.body or b'').split(b'&')
        r2q = (r2.body or b'').split(b'&')
        for q in r1q:
            if b'secret' in q or b'token' in q:
                continue
            if q not in r2q:
                return False
    else:
        for key in ['Content-Length', 'Content-Type', 'Range']:
            if key in r1.headers and key in r2.headers:
                if r1.headers.get(key, '') != r2.headers.get(key, ''):
                    return False
    return True

recording_path = os.path.join(os.path.dirname(__file__), 'recordings')

my_vcr = vcr.VCR(
    cassette_library_dir=recording_path,
    record_mode=RECORD_MODE,
    path_transformer=vcr.VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
    filter_query_parameters=['refresh_token', 'client_id',
                             'client_secret'],
    before_record_response=before_record_response,
    before_record=before_record
    )
my_vcr.register_matcher('all', matcher)
my_vcr.match_on = ['all']
files = {'test/accounts.1.json':  (b'{"amount": 100, "name": "Alice"}\n'
                                   b'{"amount": 200, "name": "Bob"}\n'
                                   b'{"amount": 300, "name": "Charlie"}\n'
                                   b'{"amount": 400, "name": "Dennis"}\n'),
         'test/accounts.2.json':  (b'{"amount": 500, "name": "Alice"}\n'
                                   b'{"amount": 600, "name": "Bob"}\n'
                                   b'{"amount": 700, "name": "Charlie"}\n'
                                   b'{"amount": 800, "name": "Dennis"}\n')}

csv_files = {'2014-01-01.csv': (b'name,amount,id\n'
                                b'Alice,100,1\n'
                                b'Bob,200,2\n'
                                b'Charlie,300,3\n'),
             '2014-01-02.csv': (b'name,amount,id\n'),
             '2014-01-03.csv': (b'name,amount,id\n'
                                b'Dennis,400,4\n'
                                b'Edith,500,5\n'
                                b'Frank,600,6\n')}
text_files = {'nested/file1': b'hello\n',
              'nested/file2': b'world',
              'nested/nested2/file1': b'hello\n',
              'nested/nested2/file2': b'world'}
a = TEST_BUCKET+'/tmp/test/a'
b = TEST_BUCKET+'/tmp/test/b'
c = TEST_BUCKET+'/tmp/test/c'
d = TEST_BUCKET+'/tmp/test/d'


@contextmanager
def ignoring(*exceptions):
    try:
        yield
    except exceptions:
        pass


@contextmanager
def tempdir(dir=None):
    dirname = tempfile.mkdtemp(dir=dir)
    shutil.rmtree(dirname, ignore_errors=True)

    try:
        yield dirname
    finally:
        if os.path.exists(dirname):
            shutil.rmtree(dirname, ignore_errors=True)


@contextmanager
def tmpfile(extension='', dir=None):
    extension = '.' + extension.lstrip('.')
    handle, filename = tempfile.mkstemp(extension, dir=dir)
    os.close(handle)
    os.remove(filename)

    try:
        yield filename
    finally:
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                with ignoring(OSError):
                    os.remove(filename)


@pytest.yield_fixture
def token_restore():
    cache = GCSFileSystem.tokens
    try:
        GCSFileSystem.tokens = {}
        yield
    finally:
        GCSFileSystem.tokens = cache
        GCSFileSystem._save_tokens()


@contextmanager
def gcs_maker(populate=False):
    gcs = GCSFileSystem(TEST_PROJECT, token=GOOGLE_TOKEN)
    gcs.invalidate_cache()
    try:
        try:
            gcs.mkdir(TEST_BUCKET, default_acl="authenticatedread",
                      acl="publicReadWrite")
        except:
            pass
        for k in [a, b, c, d]:
            try:
                gcs.rm(k)
            except:
                pass
        if populate:
            for flist in [files, csv_files, text_files]:
                for fname, data in flist.items():
                    with gcs.open(TEST_BUCKET+'/'+fname, 'wb') as f:
                        f.write(data)
        yield gcs
    finally:
        for f in gcs.find(TEST_BUCKET):
            try:
                gcs.rm(f)
            except:
                pass
