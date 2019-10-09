import binascii
import os
import re
from .git import get_repo_dir, show_file, list_tree
from .errors import ManagedException
from .postgrator import list_postgrator_records

RECORD_FILENAME_REGEX = re.compile('^[0-9a-f]{40}$')

def generate_record_id():
    return binascii.b2a_hex(os.urandom(20)).decode('utf8')

# Returns a list of record IDs
def list_records(conf, treeish):
    record_dir = conf['record_dir']
    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    native_records = [
        x
        for x in list_tree(treeish, record_dir + '/')
        if RECORD_FILENAME_REGEX.match(x) is not None
    ]
    postgrator_records = list_postgrator_records(conf, treeish)
    return native_records + postgrator_records

# Content may be None, then nothing will be written
def write_record(record_dir_path, record_id, content):
    filename = record_id
    file_path = os.path.join(record_dir_path, filename)
    with open(file_path, 'w') as f:
        if content:
            f.write(content)
            os.fsync(f)
    return file_path

# record_fields is dict or None
def create_record(conf, record_fields):
    repo_dir = get_repo_dir()
    if repo_dir is None:
        raise ManagedException("No git repo found")

    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    record_dir_path = os.path.join(repo_dir, conf['record_dir'])

    record_id = generate_record_id()
    if record_fields is not None:
        record_buffer = record_fields.get('type', 'type') + ': ' + record_fields.get('description', '')
    else:
        record_buffer = None
    record_path = write_record(record_dir_path, record_id, record_buffer)
    return record_id, record_path

def read_branch_record(conf, treeish, record_id):
    if record_id.startswith('pg/'):
        filename = record_id[3:]
        if conf['postgrator_dir'] is None:
            raise ManagedException("Must specify postgres_dir in conf")
        git_path = os.path.join(conf['postgrator_dir'], filename)
        return 'migration: ' + git_path
    else:
        filename = record_id
        if conf['record_dir'] is None:
            raise ManagedException("Must specify record_dir in conf")
        git_path = os.path.join(conf['record_dir'], filename)
        return show_file(treeish, git_path)
