import argparse
from contextlib import redirect_stderr
import datetime
import io
import json
import os
import shlex
from unittest.mock import call, Mock, patch
import zipfile

import pytest
import requests

from flywheel_cli.commands import sync
from flywheel_cli.sync import fw_src
from flywheel_cli.sync import os_dst
from flywheel_cli.sync import s3_dst


def test_add_command():
    subparsers = Mock(**{'add_parser.return_value': argparse.ArgumentParser()})
    parser = sync.add_command(subparsers, None)

    def assert_parsed_params(command, **kwargs):
        args = vars(parser.parse_args(shlex.split(command)))
        mock = create_args(return_dict=True, **kwargs)
        for key, value in mock.items():
            assert key in args, f'Expected {key} in args ({sorted(args)})'
            assert args[key] == value, f'Expected {key}={value} (got {args[key]})'

    with pytest.raises(SystemExit), redirect_stderr(io.StringIO()):
        parser.parse_args([])

    assert_parsed_params('src', src='src')

    assert_parsed_params('src dst', src='src', dst='dst')

    assert_parsed_params('src -i t1 --include t2', src='src', include=['t1', 't2'])

    assert_parsed_params('src -e t1 --exclude t2', src='src', exclude=['t1', 't2'])

    assert_parsed_params('src -a', src='src', analyses=True)
    assert_parsed_params('src --analyses', src='src', analyses=True)

    assert_parsed_params('src -m', src='src', metadata=True)
    assert_parsed_params('src --metadata', src='src', metadata=True)

    assert_parsed_params('src -x', src='src', full_project=True)
    assert_parsed_params('src --full-project', src='src', full_project=True)

    assert_parsed_params('src -z', src='src', unpack=False)
    assert_parsed_params('src --no-unpack', src='src', unpack=False)

    assert_parsed_params('src -l', src='src', list_only=True)
    assert_parsed_params('src --list-only', src='src', list_only=True)

    assert_parsed_params('src -v', src='src', verbose=True)
    assert_parsed_params('src --verbose', src='src', verbose=True)

    assert_parsed_params('src -n', src='src', dry_run=True)
    assert_parsed_params('src --dry-run', src='src', dry_run=True)

    assert_parsed_params('src -j 2', src='src', jobs=2)
    assert_parsed_params('src --jobs 2', src='src', jobs=2)

    assert_parsed_params('src --delete', src='src', delete=True)


def test_get_download_ticket():
    fw_invalid_project = Mock(**{'lookup.return_value': Mock(container_type='group', id='id')})
    args_invalid_project = create_args(src='fw://group')
    sync.get_download_ticket(fw_invalid_project, args_invalid_project)
    fw_invalid_project.lookup.assert_called_once_with(['group'])
    args_invalid_project.parser.error.assert_called_once_with('fw://group is not a project')

    fw = Mock(**{'lookup.return_value': Mock(container_type='project', id='project_id')})
    sync.get_download_ticket(fw, create_args(src='fw://group/project'))
    fw.lookup.assert_called_once_with(['group', 'project'])
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}]},
        type='full', prefix='')

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(include='type'))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}],
         'filters': [{'types': {'+': 'type'}}]},
        type='full', prefix='')

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(exclude='type'))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}],
         'filters': [{'types': {'-': 'type'}}]},
        type='full', prefix='')

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(exclude='type'))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}],
         'filters': [{'types': {'-': 'type'}}]},
        type='full', prefix='')

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(include=['i1', 'i2'], exclude=['e1', 'e2']))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}],
         'filters': [{'types': {'+': ['i1', 'i2']}},
                     {'types': {'-': ['e1', 'e2']}}]},
        type='full', prefix='')

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(analyses=True))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}]},
        type='full', prefix='', analyses=True)

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(metadata=True))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}]},
        type='full', prefix='', metadata=True)

    fw.reset_mock()
    sync.get_download_ticket(fw, create_args(full_project=True))
    fw.create_download_ticket.assert_called_once_with(
        {'nodes': [{'level': 'project', '_id': 'project_id'}]},
        type='full', prefix='', analyses=True, metadata=True)


def test_get_filedict():
    class TestFile:
        def __init__(self, num):
            self.name = str(num)
            self.size = num

    files = [TestFile(i) for i in range(15)]
    progress = io.StringIO()
    filedict = sync.get_filedict('fs_url', files, report_batch=10, fh=progress)
    assert filedict == {file.name: file for file in files}
    assert progress.getvalue() == (
        'fs_url (45 bytes / 10 files)                                            \r'
        'fs_url (105 bytes / 15 files)                                           \n'
    )


def test_print_tree():
    class TestFile:
        def __init__(self, name):
            self.name = name
            self.size = len(self.name)

    files = [TestFile(name) for name in (
        'a/b/c',
        'a/b/d',
        'a/e',
        'f',
    )]

    tree_1 = io.StringIO()
    sync.print_tree(files, fh=tree_1)
    assert tree_1.getvalue() == (
        '`- a (3 bytes / 1 file)\n'
        '   `- b (10 bytes / 2 files)\n'
    )

    tree_2 = io.StringIO()
    sync.print_tree(files, verbose=True, fh=tree_2)
    assert tree_2.getvalue() == (
        '`- f (1 byte)\n'
        '`- a\n'
        '   |- e (3 bytes)\n'
        '   `- b\n'
        '      |- c (5 bytes)\n'
        '      `- d (5 bytes)\n'
    )

    tree_3 = Mock(wraps=io.StringIO(), encoding='UTF-8')
    sync.print_tree(files, verbose=True, fh=tree_3)
    assert tree_3.getvalue() == (
        '└─ f (1 byte)\n'
        '└─ a\n'
        '   ├─ e (3 bytes)\n'
        '   └─ b\n'
        '      ├─ c (5 bytes)\n'
        '      └─ d (5 bytes)\n'
    )


def test_fw_src(tmpdir):
    path = str(tmpdir.join('acq.dicom.zip'))
    member_1 = b'first'
    member_2 = b'second'
    with zipfile.ZipFile(path, 'w') as zf:
        zf.writestr('member/path/1.dcm', member_1)
        zf.writestr('member/path/2.dcm', member_2)
    zip_size = os.path.getsize(path)
    zip_mod = float(int(os.path.getmtime(path)))  # truncate before isoformat does...
    zip_mod_iso = datetime.datetime.fromtimestamp(zip_mod).isoformat()
    zip_content = open(path, 'rb').read()

    meta = {'info': {'DicomTag': 'Value'}}
    meta_content = json.dumps(meta).encode('utf8')
    meta_size = len(meta_content)
    meta_mod = zip_mod

    targets = [{
        'container_id': 'acq_id',
        'filename': 'acq.dicom.zip',
        'filetype': 'dicom',
        'download_type': 'file',
        'dst_path': '/proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip',
        'size': zip_size,
        'modified': zip_mod_iso,
    }, {
        'container_id': 'acq_id',
        'filename': 'acq.dicom.zip',
        'filetype': None,
        'download_type': 'metadata_sidecar',
        'dst_path': '/proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip.flywheel.json',
        'metadata': meta,
        'size': 0,  # set dynamically in FWFile.__init__ based on json.dumps(metadata)
        'modified': zip_mod_iso,
    }]

    def call_api(url, method, **kwargs):
        url = url.format_map(kwargs.get('path_params'))
        if (method, url) == ('GET', '/download/ticket/targets'):
            content = ''.join(f'--boundary\r\n\r\n{json.dumps(t)}\r\n' for t in targets)
            content = (content + '--boundary--\r\n').encode('utf8')
            return Mock(**{
                'status_code': 200,
                'raise_for_status.side_effect': None,
                'headers': {'content-type': 'multipart/form-data; boundary=boundary'},
                'content': content,
            })
        if (method, url) == ('GET', '/containers/acq_id/files/acq.dicom.zip'):
            return Mock(status_code=200, raw=open(path, 'rb'))
        assert False, f'Unexpected request {method} {url}'

    def zip_info(container_id, filename):
        assert (container_id, filename) == ('acq_id', 'acq.dicom.zip')
        return Mock(members=[
            {'path': member.filename, 'size': member.file_size}
            for member in zipfile.ZipFile(path).infolist()
        ])

    fw = Mock(**{
        'api_client.call_api': call_api,
        'get_container_file_zip_info': zip_info,
    })

    def file_to_dict(file):
        return {'size': file.size, 'modified': file.modified, 'content': file.read()}

    src = fw_src.FWSource(fw, 'ticket')
    files = {file.name: file_to_dict(file) for file in src}
    assert files == {
        'proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip': {
            'size': zip_size, 'modified': zip_mod, 'content': zip_content
        },
        'proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip.flywheel.json': {
            'size': meta_size, 'modified': zip_mod, 'content': meta_content
        },
    }

    src = fw_src.FWSource(fw, 'ticket', strip_project=True)
    files = {file.name: file_to_dict(file) for file in src}
    assert files == {
        'SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip': {
            'size': zip_size, 'modified': zip_mod, 'content': zip_content
        },
        'SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip.flywheel.json': {
            'size': meta_size, 'modified': zip_mod, 'content': meta_content
        },
    }

    src = fw_src.FWSource(fw, 'ticket', unpack=True)
    files = {file.name: file_to_dict(file) for file in src}
    assert files == {
        'proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq/1.dcm': {
            'size': len(member_1), 'modified': zip_mod, 'content': member_1
        },
        'proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq/2.dcm': {
            'size': len(member_2), 'modified': zip_mod, 'content': member_2
        },
        'proj/SUBJECTS/subj/SESSIONS/sess/ACQUISITIONS/acq/FILES/acq.dicom.zip.flywheel.json': {
            'size': meta_size, 'modified': zip_mod, 'content': meta_content
        },
    }

    member = list(fw_src.FWSource(fw, 'ticket', unpack=True))[0]
    assert isinstance(member, fw_src.FWMember)

    data = chunk = member.read(1)
    assert chunk
    assert len(chunk) == 1
    while chunk:
        chunk = member.read()
        data += chunk
    assert data == member_1

    temp_path = f'{member.packfile.tempdir}/{member.path}'
    assert os.path.exists(temp_path)
    member.cleanup()
    assert not os.path.exists(temp_path)


def test_os_dest(tmpdir):
    def create_file(name):
        path = str(tmpdir.join(name))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wt') as file:
            file.write(path)
        stat = os.stat(path)
        return stat.st_size, stat.st_mtime

    empty_dir = str(tmpdir.join('empty/dir'))
    os.makedirs(empty_dir)
    expected_stats = {name: create_file(name) for name in (
        'a/b/c',
        'a/b/d',
        'a/e',
        'f',
    )}

    dst = os_dst.OSDestination(tmpdir)
    stats = {file.name: (file.size, file.modified) for file in dst}
    assert stats == expected_stats

    file = dst.file('new/file')
    assert file.name == 'new/file'
    assert file.filepath == str(tmpdir.join('new/file'))
    assert not os.path.exists(file.filepath)

    file.store(io.BytesIO(b'test'))
    assert os.path.exists(file.filepath)
    assert open(file.filepath).read() == 'test'

    file.delete()
    assert not os.path.exists(file.filepath)

    assert os.path.exists(empty_dir)
    dst.cleanup()
    assert not os.path.exists(empty_dir)


def test_s3_dst():
    boto = Mock(**{
        'client.return_value.get_paginator.return_value.paginate.return_value': [
            {'Contents': [
                {'Key': 'prefix/path/1', 'Size': 1,
                 'LastModified': datetime.datetime.fromtimestamp(1)},
            ]},
            {'Contents': [
                {'Key': 'prefix/path/2', 'Size': 2,
                 'LastModified': datetime.datetime.fromtimestamp(2)},
            ]}
        ]
    })
    patcher = patch('flywheel_cli.sync.s3_dst.boto3', new=boto)
    patcher.start()

    dst = s3_dst.S3Destination('bucket', 'prefix/')
    stats = {file.name: (file.size, file.modified) for file in dst}
    assert stats == {'path/1': (1, 1.0), 'path/2': (2, 2.0)}
    boto.client.assert_has_calls([
        call('s3', config=s3_dst.BOTO_CONFIG),
        call().get_paginator('list_objects'),
        call().get_paginator().paginate(Bucket='bucket', Prefix='prefix/')
    ])

    file = dst.file('path/3')
    assert file.name == 'path/3'
    assert file.key == 'prefix/path/3'

    boto.reset_mock()
    data = io.BytesIO(b'test')
    file.store(data)
    boto.client().upload_fileobj.assert_called_once_with(
        data, 'bucket', 'prefix/path/3', Config=s3_dst.S3_TRANSFER_CONFIG)

    boto.reset_mock()
    file.delete()
    assert dst.delete_keys == ['prefix/path/3']
    assert not boto.client().delete_objects.called

    dst.cleanup()
    assert dst.delete_keys == []
    boto.client().delete_objects.assert_called_once_with(
        Bucket='bucket', Delete={'Objects': [{'Key': 'prefix/path/3'}]})

    boto.reset_mock()
    for i in range(1000):
        file.delete()
    assert dst.delete_keys == []
    boto.client().delete_objects.assert_called_once()

    patcher.stop()


def test_queue():
    # TODO
    pass


def create_args(return_dict=False, **kwargs):
    """Create mocked parsed CLI args"""
    kwargs.setdefault('src', None)
    kwargs.setdefault('dst', None)
    kwargs.setdefault('include', [])
    kwargs.setdefault('exclude', [])
    kwargs.setdefault('analyses', False)
    kwargs.setdefault('metadata', False)
    kwargs.setdefault('full_project', False)
    kwargs.setdefault('unpack', True)
    kwargs.setdefault('list_only', False)
    kwargs.setdefault('verbose', False)
    kwargs.setdefault('dry_run', False)
    kwargs.setdefault('jobs', 4)
    kwargs.setdefault('delete', False)
    if return_dict:
        return kwargs
    return Mock(**kwargs)
