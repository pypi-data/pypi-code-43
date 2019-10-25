import unittest
import warnings
import logging

class TestWarnings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global enable_deprecation_warnings, enable_warnings_to_log

        from pyats.log.warnings import (enable_deprecation_warnings,
                                      enable_warnings_to_log)

        # backup warnings.filters
        cls.filters_bkup = warnings.filters.copy()

        # backup printer
        cls.showwarning = warnings.showwarning

    def setUp(self):
        # get rid of the filter that prints all warnings
        for i, item in enumerate(warnings.filters):
            if item == ('default', None, Warning, None, 0):
                break
        else:
            return

        warnings.filters.pop(i)

    def tearDown(self):
        warnings.filters = self.filters_bkup
        warnings.showwarning = self.showwarning

    def test_enable_deprecation_warnings(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.warn("deprecated", DeprecationWarning)
            
            self.assertEqual(len(w), 0)
        
        enable_deprecation_warnings(module='.*')

        with warnings.catch_warnings(record=True) as w:
            warnings.warn("deprecated", DeprecationWarning)
            
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn( "deprecated", str(w[-1].message))

    def test_duplicates(self):
        filters = warnings.filters.copy()
        enable_deprecation_warnings(module='.*')

        self.assertEqual(len(filters)+1, len(warnings.filters))

        enable_deprecation_warnings(module='.*')
        enable_deprecation_warnings(module='.*')

        self.assertEqual(len(filters)+1, len(warnings.filters))
        self.assertEqual(filters, warnings.filters[1:])

    def test_enable_warnings_to_log(self):
        enable_warnings_to_log()
        with self.assertLogs('warnings', logging.WARNING):
            warnings.warn("Boom")
