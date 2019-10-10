# Copyright (C) 2015-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import unittest
from unittest.mock import patch

from swh.loader.tar import build


class TestBuildUtils(unittest.TestCase):
    @patch('swh.loader.tar.build._time_from_last_modified')
    def test_compute_revision(self, mock_time_from_last_modified):
        mock_time_from_last_modified.return_value = 'some-other-time'

        # when
        actual_revision = build.compute_revision('/some/path', 'last-modified')

        expected_revision = {
            'date': {
                'timestamp': 'some-other-time',
                'offset': build.UTC_OFFSET,
            },
            'committer_date': {
                'timestamp': 'some-other-time',
                'offset': build.UTC_OFFSET,
            },
            'author': build.SWH_PERSON,
            'committer': build.SWH_PERSON,
            'type': build.REVISION_TYPE,
            'message': build.REVISION_MESSAGE,
            'synthetic': True,
        }

        # then
        self.assertEqual(actual_revision, expected_revision)

        mock_time_from_last_modified.assert_called_once_with(
            'last-modified')

    def test_time_from_last_modified_with_float(self):
        actual_time = build._time_from_last_modified(
            '2015-10-20T13:38:06.830834+00:00')

        self.assertEqual(actual_time, {
            'seconds': 1445348286,
            'microseconds': 830834
        })

    def test_time_from_last_modified_with_int(self):
        actual_time = build._time_from_last_modified(
            '2015-10-20T13:38:06+00:00')

        self.assertEqual(actual_time, {
            'seconds': 1445348286,
            'microseconds': 0
        })
