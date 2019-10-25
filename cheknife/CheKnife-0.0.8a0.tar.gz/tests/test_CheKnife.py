from __future__ import unicode_literals
from CheKnife import hashing, dynamic_import, paths
from CheKnife.django.choiceutils import ChoiceHelper
import os
from unittest import TestCase
import six
from CheKnife.security import (
    CryptoKeyFileManager,
    Vault,
    DjangoDatabaseSettings,
    DjangoSecretKey,
)
from CheKnife.paths import mktree
from io import open
from .aux_data import AUX_DATA_PATH


# nosetests --with-coverage --cover-inclusive --cover-package=CheKnife --cover-html


class SecurityTestCase(TestCase):
    to_remove = []
    output_dir = None
    files = None

    @classmethod
    def setUpClass(cls):
        if six.PY3:
            cls.output_dir = 'tests/python3/'
        else:
            cls.output_dir = 'tests/python2/'
        cls.files = {
            'cryptokeyfile': os.path.join(cls.output_dir, 'criptokey.key'),
            'new_cryptokey': os.path.join(cls.output_dir, 'new_criptokey.key'),
            'secret_key': os.path.join(cls.output_dir, 'secret_key.secure'),
            'db_path': os.path.join(cls.output_dir, 'databases.cnf'),
            'S3_CFG': os.path.join(cls.output_dir, 'S3.cnf'),
            'hidden_settings': os.path.join(cls.output_dir, 'hidden.cnf'),
        }
        # cls.cryptokey = djangosecure.cryptolib.read_key_file(cls.files['cryptokeyfile'])

    @classmethod
    def tearDownClass(cls):
        for file_dec, path in cls.files.items():
            try:
                os.remove(path)
            except OSError:
                pass
        try:
            os.removedirs(cls.output_dir)
        except OSError:
            pass


class TestCriptolib(SecurityTestCase):

    def setUp(self):
        self.cryptokey = CryptoKeyFileManager(self.files['cryptokeyfile'])
        self.hidden_settings = Vault(self.files['hidden_settings'],
                                     crypto_key_file=self.files['cryptokeyfile'])
        self.database_settings = DjangoDatabaseSettings(self.files['db_path'])

    def test_crypto_key_file_manager(self):
        self.assertEqual(len(self.cryptokey.key), 64)

    def test_read_key_file(self):
        mktree(os.path.dirname(self.files['cryptokeyfile']))
        with open(self.files['cryptokeyfile'], 'w') as key_file:
            key_file.write('c8f12b2936034ee019fa1760dd6a4ce7065ead9b00cd20b48af0e408e89a9a02')
        self.assertEqual(CryptoKeyFileManager(self.files['cryptokeyfile']).key,
                         'c8f12b2936034ee019fa1760dd6a4ce7065ead9b00cd20b48af0e408e89a9a02')

    def test_hidden_settings(self):
        # Set value
        self.assertEqual('test setting value', self.hidden_settings.get('test_section', 'test_option',
                                                                        test_value='test setting value'))
        # Recover value
        self.assertEqual('test setting value', self.hidden_settings.get('test_section', 'test_option'))

    def test_create_key_file(self):
        new_cryptokey = CryptoKeyFileManager(self.files['new_cryptokey'])
        self.assertTrue(os.path.isfile(new_cryptokey.path))

    def test_get_database(self):
        database = self.database_settings.settings('default', test=True)
        self.assertEqual(self.database_settings.config_file_path, self.files['db_path'])
        self.assertDictEqual(database, {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test_db_name',
            'USER': 'test_user',
            'PASSWORD': 'test_password',
            'HOST': 'test_host',
            'PORT': '5432',
        })

    def test_get_secret_key(self):
        secret_key = DjangoSecretKey(self.files['secret_key'])
        self.assertEqual(secret_key.config_file_path, self.files['secret_key'])
        self.assertIsNotNone(secret_key.key)
        self.assertTrue(os.path.isfile(secret_key.config_file_path))


class TestCheknife(TestCase):
    """Tests for `CheKnife` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_hashing_textmd5sum(self):
        self.assertEqual(hashing.textmd5sum('Hola'), 'f688ae26e9cfa3ba6235477831d5122e')
        self.assertEqual(hashing.textmd5sum('Adios'), 'eeb15117bd15cf4c9474acda0b2f6598')

    def test_dynamic_import_get_attribute(self):
        self.assertEqual(dynamic_import.get_attribute('CheKnife.dynamic_import.get_attribute'), dynamic_import.get_attribute)

    def test_filemd5sum(self):
        self.assertEqual(hashing.filemd5sum(os.path.join(AUX_DATA_PATH, 'md5testfile.txt')),
                         'e42b2de78fc6c21912de0cdbb8d9631a')


class TestDjangoChoiceHelper(TestCase):
    def test_choice_helper(self):
        choices = (
            (1, 'First Choice'),
            (2, 'Second Choice'),
        )
        helper = ChoiceHelper(choices)

        self.assertEqual(helper.get_literal(1), 'First Choice')
        self.assertEqual(helper.get_value('First Choice'), 1)
        self.assertEqual(helper.get_value('Second Choice'), 2)
        self.assertEqual(helper.get_literal(2), 'Second Choice')


class TestPaths(TestCase):
    def test_split_path(self):
        self.assertDictEqual(paths.split_path('/some/file/path/filename.ext'),
                             {'path': '/some/file/path', 'filename': 'filename', 'extension': '.ext', 'type': 'ext'})
        self.assertDictEqual(paths.split_path('/some/file/path/'),
                             {'path': '/some/file/path', 'filename': '', 'extension': '', 'type': ''})
        self.assertDictEqual(paths.split_path('/some/file/path'),
                             {'path': '/some/file', 'filename': 'path', 'extension': '', 'type': ''})