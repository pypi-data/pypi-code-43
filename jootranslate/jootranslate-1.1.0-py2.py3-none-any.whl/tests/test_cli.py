import os
import sys

import argparse as argparse

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TEST_ROOT, '..'))
from jootranslate.cli import JooTranslate


class Args(argparse.ArgumentParser):
    path = os.path.join(TEST_ROOT, 'files')
    com = 'com_test'
    lang = 'en-GB'
    trans = False
    log = True


class TestCli(object):
    com_lang = None
    admin_lang = None
    com_ini = None

    @classmethod
    def setup_class(cls):
        args = Args()
        cls.jt = JooTranslate(args=args)
        cls.admin_lang = os.path.join(
            cls.jt.paths['admin'], 'language', args.lang, cls.jt.get_filename())
        cls.com_lang = os.path.join(
            cls.jt.paths['component'], 'language', args.lang, cls.jt.get_filename())
        cls.com_ini = os.path.join(
            cls.jt.paths['admin'], 'language', args.lang, cls.jt.get_filename(sys=True))

    @classmethod
    def teardown_class(cls):
        rf = open(cls.admin_lang, 'r')
        lines = rf.readlines()
        rf.close()
        wf = open(cls.admin_lang, 'w')
        wf.writelines(lines[:1])
        wf.close()

        os.remove(cls.com_lang)
        os.remove(cls.com_ini)
        os.remove(JooTranslate.get_logfile())
        os.rmdir(os.path.dirname(cls.com_lang))

    def test_files_exist(self):
        assert os.path.isfile(self.admin_lang)
        assert os.path.isfile(self.com_lang)
        assert os.path.isfile(self.com_ini)
        assert os.path.isfile(JooTranslate.get_logfile())

    def test_file_content(self):
        af = open(self.admin_lang, 'r')
        assert af.read() == \
               "COM_TEST_KEEPME = 'translated'\nCOM_TEST_NAME = ''\nCOM_TEST_NAME_DESC = ''\nCOM_TEST_TEST_STRING = ''\n"
        af.close()
        cf = open(self.com_lang, 'r')
        assert cf.read() == "COM_TEST_TEST_STRING = ''\nCOM_TEST_JS_STRING = ''\nCOM_TEST_FORM = ''\n"
        cf.close()

    def test_logfile(self):
        lf = open(JooTranslate.get_logfile(), 'r')
        assert 'this is wrong' in lf.read()
        lf.close()