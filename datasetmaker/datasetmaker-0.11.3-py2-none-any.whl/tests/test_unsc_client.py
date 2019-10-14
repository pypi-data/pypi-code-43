# mypy: allow-untyped-defs

import unittest
from unittest.mock import patch
import datasetmaker as dam
import pandas as pd

@unittest.skip('Skipped because empty test')
class TestUNSCClient(unittest.TestCase):
    def setUp(self):
        pass
