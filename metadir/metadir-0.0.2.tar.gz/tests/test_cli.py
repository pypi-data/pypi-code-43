"""Tests for our main metadir module."""


from subprocess import PIPE, Popen as popen
from unittest import TestCase

from metadir import __version__ as VERSION


class TestHelp(TestCase):
    def test_returns_usage_information(self):
        output = popen(['metadir', '-h'], stdout=PIPE).communicate()[0]
        self.assertTrue(bytes('Usage:', 'utf-8') in output)

        output = popen(['metadir', '--help'], stdout=PIPE).communicate()[0]
        self.assertTrue(bytes('Usage:', 'utf-8') in output)


class TestVersion(TestCase):
    def test_returns_version_information(self):
        output = popen(['metadir', '--version'], stdout=PIPE).communicate()[0]
        self.assertEqual(output.strip(), bytes(VERSION, 'utf-8'))
