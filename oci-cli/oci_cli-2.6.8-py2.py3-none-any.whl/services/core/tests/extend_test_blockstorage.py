# coding: utf-8
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.

import unittest
from tests import util


class TestBlockStorage(unittest.TestCase):
    def setUp(self):
        pass

    def test_copy_volume_backup(self):
        result = util.invoke_command(['bv', 'backup'])
        assert 'copy' in result.output
        result = util.invoke_command(['bv', 'backup', 'copy'])
        assert 'Error: Missing option(s) --volume-backup-id, --destination-region' in result.output
