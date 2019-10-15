# -*- coding: utf-8 -*-
"""
Created 2017/09/20
Latest update 2019/08/21

@author: Markus Eisenbach, Ronny Stricker

Description:
Helper functions for downloading datasets from FTP.
"""

from __future__ import print_function
import ftplib
try:
    import cPickle as pkl
except ImportError:
    import pickle as pkl
import hashlib
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # python 2 backport
from .ftp_info import FTP_HOST, ftp_version_prefix, INFO_FILE_TEMPLATE, CHUNK_TEMPLATE, NP_FILE_TEMPLATE,\
    dataset_info, dataset_checksums


def _cond_print(condition, content):
    if condition:
        print(content)


def _calc_md5(filename, debug_outputs=False):
    """Helper function to compute the MD5 checksum
       of the content of a file."""
    try:
        with filename.open('rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            return hashlib.md5(data).hexdigest()
    except IOError:
        _cond_print(debug_outputs, '[ERROR] cannot open file {} for computing md5 checksum'.format(filename))
        raise


def _is_valid(filename, md5_checksum, debug_outputs=False):
    """Helper function to check whether the MD5 checksum
       of the content of a file matches the expected checksum."""
    if filename.exists():
        file_md5 = _calc_md5(filename, debug_outputs)
        if file_md5 == md5_checksum:
            return True
        _cond_print(debug_outputs, '[ERROR] invalid checksum for file {}: {}'.format(filename, file_md5))
    else:
        _cond_print(debug_outputs, '[INFO] file {} does not exist'.format(filename))
    return False


def _read_pkl(file_path):
    with file_path.open('rb') as pkl_file:
        try:
            return pkl.load(pkl_file, encoding='latin1')  # python 3
        except TypeError:
            return pkl.load(pkl_file)  # python 2


def connect_ftp(connection):
    if connection['ftp'] is None:
        connection['ftp'] = ftplib.FTP(FTP_HOST, user=connection['user'], passwd=connection['password'])


def download_file(remote_path,
                  local_path,
                  checksum,
                  connection,
                  debug_outputs):
    if not _is_valid(local_path, checksum, debug_outputs):
        connect_ftp(connection)
        _cond_print(debug_outputs, '[INFO] downloading {}'.format(remote_path))

        for trial in range(3):
            # try to download file
            with local_path.open('wb') as dst_file:
                connection['ftp'].retrbinary('RETR '
                                             + ftp_version_prefix[connection['version']]
                                             + remote_path.as_posix(),
                                             dst_file.write)
            # verify checksum
            if _is_valid(local_path, checksum, debug_outputs):
                return
        raise IOError('[ERROR] Download of file {} failed three times in a row! Giving up.'.format(remote_path))


def _download_images(connection,
                     output_dir,
                     version=1,
                     subsets=None,
                     debug_outputs=False):

    # create database root dir
    ftp_dir = Path('images')
    db_dir = Path(output_dir) / 'v{}'.format(version) / ftp_dir
    db_dir.mkdir(parents=True, exist_ok=True)

    # download images
    images_file = 'images.zip'
    checksum = dataset_checksums[version]['images']['images']

    download_file(ftp_dir / images_file,
                  db_dir / images_file,
                  checksum,
                  connection,
                  debug_outputs)

    for subset in subsets:

        # download numpy file of subset
        np_file = NP_FILE_TEMPLATE.format(subset=subset)
        checksum = dataset_checksums[version]['images'][subset]

        download_file(ftp_dir / np_file,
                      db_dir / np_file,
                      checksum,
                      connection,
                      debug_outputs)


def _download_segmentation(connection,
                           output_dir,
                           version=2,
                           subsets=None,
                           debug_outputs=False):
    # create filelist
    files = ['images']
    if subsets is not None:
        files += subsets

    # create database root dir
    ftp_dir = Path('segmentation')
    db_dir = Path(output_dir) / 'v{}'.format(version) / ftp_dir
    db_dir.mkdir(parents=True, exist_ok=True)

    # download files
    for f in files:
        filename = f+".zip"
        checksum = dataset_checksums[version]['segmentation'][f]

        download_file(ftp_dir / filename,
                      db_dir / filename,
                      checksum,
                      connection,
                      debug_outputs)


def _download_patches(connection,
                      output_dir,
                      version=1,
                      patchsize=64,
                      issue='NORMvsDISTRESS',
                      subsets=None,
                      debug_outputs=False):

    # create database root dir
    ftp_dir = Path('{}_{}'.format(issue, patchsize))
    db_dir = Path(output_dir) / 'v{}'.format(version) / ftp_dir
    db_dir.mkdir(parents=True, exist_ok=True)

    for subset in subsets:
        # create subdir
        db_subdir = db_dir/subset
        ftp_subdir = ftp_dir/subset
        db_subdir.mkdir(exist_ok=True)

        # download subset info file
        sub_info_file = INFO_FILE_TEMPLATE.format(patchsize=str(patchsize),
                                                  issue=issue,
                                                  subset=subset)
        checksum = dataset_checksums[version][patchsize][issue][subset]

        download_file(ftp_subdir/sub_info_file,
                      db_subdir/sub_info_file,
                      checksum,
                      connection,
                      debug_outputs)

        # read subset info
        sub_info = _read_pkl(db_subdir/sub_info_file)

        # check if alternative ftp patch source is required
        if 'patch_issue' in dataset_checksums[version][patchsize][issue]:
            patch_issue = dataset_checksums[version][patchsize][issue]['patch_issue']
            ftp_patch_subdir = Path('{}_{}'.format(patch_issue, patchsize)) / subset
        else:
            patch_issue = issue
            ftp_patch_subdir = ftp_subdir

        # download all subset chunks
        for chunk_id in range(sub_info['n_chunks']):
            # use different issue and subdir for x files if required
            for data, d_issue, d_ftp_dir, checksum in zip(['x', 'y'],
                                                          [patch_issue, issue],
                                                          [ftp_patch_subdir, ftp_subdir],
                                                          sub_info['checksums'][chunk_id]):
                source_file = CHUNK_TEMPLATE.format(patchsize=str(patchsize),
                                                    issue=d_issue,
                                                    subset=subset,
                                                    part_nr=str(chunk_id).zfill(sub_info['chunk_descriptor_digits']),
                                                    data=data)
                target_file = CHUNK_TEMPLATE.format(patchsize=str(patchsize),
                                                    issue=issue,
                                                    subset=subset,
                                                    part_nr=str(chunk_id).zfill(sub_info['chunk_descriptor_digits']),
                                                    data=data)
                download_file(d_ftp_dir/source_file,
                              db_subdir/target_file,
                              checksum,
                              connection,
                              debug_outputs)


def download_dataset(
        login,
        output_dir,
        version=1,
        patchsize=64,
        issue='NORMvsDISTRESS',
        subsets=None,
        debug_outputs=False):

    if version not in dataset_info.keys():
        raise ValueError('Version must be one of {}'.format(dataset_info.keys()))
    if patchsize not in dataset_info[version]['patchsizes']:
        raise ValueError('Patchsize must be one of {}'.format(dataset_info[version]['patchsizes']))
    if issue not in dataset_info[version]['issues']:
        raise ValueError('Issue must be one of {} for selected version'.format(dataset_info[version]['issues']))

    if subsets is None:
        subsets = dataset_info[version]['subsets']

    if not isinstance(subsets, list):
        subsets = [subsets]

    unknown_subsets = [sub for sub in subsets if sub not in dataset_info[version]['subsets']]
    if len(unknown_subsets) > 0:
        raise ValueError('Subsets {} are not supported by the selected version. Supported subsets are: {}'.format(
            unknown_subsets,
            dataset_info[version]['subsets']
        ))

    if isinstance(patchsize, int):
        if dataset_checksums[version][patchsize][issue]['train'] is None:
            raise ValueError('Version, patchsize and subset combination available upon request only! '
                             'Please contact ronny.stricker@tu-ilmenau.de')

    try:
        split = int(login[-1])
    except ValueError:
        raise ValueError('Invalid login! Please provide proper login data.')

    connection = {
        'ftp': None,
        'user': login[:split],
        'password': login[split:-1],
        'version': version
    }

    if patchsize == 'images':
        _download_images(connection,
                         output_dir,
                         version,
                         subsets,
                         debug_outputs)
    elif patchsize == 'segmentation':
        _download_segmentation(connection,
                               output_dir,
                               version,
                               subsets,
                               debug_outputs)
    else:
        _download_patches(connection,
                          output_dir,
                          version,
                          patchsize,
                          issue,
                          subsets,
                          debug_outputs)

    # close ftp connection
    if connection['ftp'] is not None:
        connection['ftp'].quit()
