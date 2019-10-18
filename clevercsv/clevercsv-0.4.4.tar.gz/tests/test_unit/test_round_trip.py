# -*- coding: utf-8 -*-

"""
Unit tests for round trips.

Author: Gertjan van den Burg

"""

import clevercsv
import tempfile
import unittest


class RoundTripTestCase(unittest.TestCase):
    pass
#    def _write_test_vary_doublequote(self, fields, expect, **kwargs):
#        kwargs.update(doublequote=True)
#        self._write_test(fields, expect, **kwargs)
#        kwargs.update(doublequote=False)
#        self._write_test(fields, expect, **kwargs)
#
#    def _write_test(self, fields, expect, **kwargs):
#        with tempfile.TemporaryFile("w+", newline="") as fileobj:
#            writer = clevercsv.writer(fileobj, **kwargs)
#            writer.writerow(fields)
#            fileobj.seek(0)
#            self.assertEqual(
#                fileobj.read(), expect + writer.dialect.lineterminator
#            )
#
#    def test_write_escape_escapechar(self):
#        dialect_qminimal = dict(
#            escapechar="/", quoting=clevercsv.QUOTE_MINIMAL
#        )
#
#        dialect_qnone = dict(escapechar="/", quoting=clevercsv.QUOTE_NONE)
#
#        dialect_qall = dict(escapechar="/", quoting=clevercsv.QUOTE_ALL)
#
#        fields = ["a/", 1]
#        with self.subTest(fields=fields):
#            self._write_test_vary_doublequote(
#                fields, '"a//",1', **dialect_qminimal
#            )
#            self._write_test_vary_doublequote(fields, "a//,1", **dialect_qnone)
#            self._write_test_vary_doublequote(fields, '"a//","1"', 
#                    **dialect_qall)
#
#        fields = ["a/b", 1]
#        with self.subTest(fields=fields):
#            self._write_test_vary_doublequote(
#                fields, '"a//b",1', **dialect_qminimal
#            )
#            self._write_test_vary_doublequote(fields, "a//b,1", 
#                    **dialect_qnone)
#            self._write_test_vary_doublequote(fields, '"a//b","1"', 
#                    **dialect_qall)
#
#        fields = ["/", 2]
#        with self.subTest(fields=fields):
#            self._write_test_vary_doublequote(fields, '"//",2', 
#                    **dialect_qminimal)
#            self._write_test_vary_doublequote(fields, "//,2", **dialect_qnone)
#            self._write_test_vary_doublequote(fields, '"//","2"', 
#                    **dialect_qall)
#
#        fields = ["a", 1, "p/q"]
#        with self.subTest(fields=fields):
#            self._write_test_vary_doublequote(
#                fields, 'a,1,"p//q"', **dialect_qminimal
#            )
#            self._write_test_vary_doublequote(fields, "a,1,p//q", 
#                    **dialect_qnone)
#            self._write_test_vary_doublequote(
#                fields, '"a","1","p//q"', **dialect_qall
#            )
