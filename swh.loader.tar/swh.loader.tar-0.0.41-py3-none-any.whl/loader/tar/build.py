# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import copy
import logging
import os

import arrow


logger = logging.getLogger(__name__)


# Static setup
EPOCH = 0
UTC_OFFSET = 0
SWH_PERSON = {
    'name': 'Software Heritage',
    'fullname': 'Software Heritage',
    'email': 'robot@softwareheritage.org'
}
REVISION_MESSAGE = 'swh-loader-tar: synthetic revision message'
REVISION_TYPE = 'tar'


def _time_from_last_modified(last_modified):
    """Compute the modification time from the tarpath.

    Args:
        last_modified (str): Last modification time

    Returns:
        dict representing a timestamp with keys {seconds, microseconds}

    """
    last_modified = arrow.get(last_modified)
    mtime = last_modified.float_timestamp
    normalized_time = list(map(int, str(mtime).split('.')))
    return {
        'seconds': normalized_time[0],
        'microseconds': normalized_time[1]
    }


def compute_revision(tarpath, last_modified):
    """Compute a revision.

    Args:
        tarpath (str): absolute path to the tarball
        last_modified (str): Time of last modification read from the
                             source remote (most probably by the lister)

    Returns:
        Revision as dict:
        - date (dict): the modification timestamp as returned by
                       _time_from_path function
        - committer_date: the modification timestamp as returned by
                       _time_from_path function
        - author: cf. SWH_PERSON
        - committer: cf. SWH_PERSON
        - type: cf. REVISION_TYPE
        - message: cf. REVISION_MESSAGE

    """
    ts = _time_from_last_modified(last_modified)

    return {
        'date': {
            'timestamp': ts,
            'offset': UTC_OFFSET,
        },
        'committer_date': {
            'timestamp': ts,
            'offset': UTC_OFFSET,
        },
        'author': SWH_PERSON,
        'committer': SWH_PERSON,
        'type': REVISION_TYPE,
        'message': REVISION_MESSAGE,
        'synthetic': True,
    }


def set_original_artifact(*, revision, filepath, nature, hashes):
    """Set the original artifact data on the given revision for
        the tarball currently being loaded."""

    revision = copy.deepcopy(revision)
    if 'metadata' not in revision or not revision['metadata']:
        revision['metadata'] = {}
    if 'original_artifact' in revision['metadata']:
        oa = revision['metadata']['original_artifact']
        if oa:
            logger.warning(
                'Revision already contains original_artifact metadata, '
                'replacing: %r',
                oa,
            )

    revision['metadata']['original_artifact'] = [{
        'name': os.path.basename(filepath),
        'archive_type': nature,
        **hashes,
    }]

    return revision
