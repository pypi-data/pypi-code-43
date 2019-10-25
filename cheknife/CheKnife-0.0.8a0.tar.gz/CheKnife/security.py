# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import stat
import six
import warnings
from builtins import input
from configparser import ConfigParser, NoOptionError, NoSectionError
import binascii
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from io import open
from CheKnife.paths import mktree
from CheKnife.errors import ImproperlyConfigured
import CheKnife
from CheKnife.text import py3_unicode, hidden_prompt, prompt


DEFAULT_CRYPTO_KEY_FILE = os.path.expanduser('~/.private/django_secure.key')
DEFAULT_DATABASES_CONF = os.path.expanduser('~/.private/django_databases.cnf')
DEFAULT_HIDDEN_SETTINGS = os.path.expanduser('~/.private/django_secure_hidden_settings.cnf')
OTHER_PASSWORD_FIELDS = []


class Cipher(object):
    """ Base class to implement ciphers """
    def __init__(self, crypto_key=None):
        self.crypto_key = crypto_key
        self.check_crypto_key()

    def check_crypto_key(self):
        if self.crypto_key is None:
            self.crypto_key = self.gen_key()

    def encrypt(self, plain_text):
        raise NotImplementedError('Must be defined at subclass')

    def decrypt(self, ciphered_text):
        raise NotImplementedError('Must be defined at subclass')

    def gen_key(self, *args, **kwargs):
        raise NotImplementedError('Must be defined at subclass setting self.crypto_key value')


class AESCipher(Cipher):
    block_size = 32
    aes_mode = AES.MODE_ECB
    pad_char = '%'

    def __init__(self, *args):
        super(AESCipher, self).__init__(*args)
        self.unhexlified_crypto_key = self.unhexlify_crypto_key()

    @property
    def cipher(self):
        return AES.new(self.unhexlified_crypto_key, self.aes_mode)

    def encrypt(self, plain_text):
        padded = pad(CheKnife.text.to_bytes(plain_text), self.block_size)
        b = CheKnife.text.to_bytes(padded)
        encoded = self.cipher.encrypt(b)
        hexlified = binascii.hexlify(encoded)
        return hexlified

    def decrypt(self, ciphered_text):
        ciphered_text = binascii.unhexlify(ciphered_text)
        message = self.cipher.decrypt(ciphered_text)
        try:
            message = unpad(message, self.block_size)
        except IndexError:
            pass

        return CheKnife.text.unicode_cast(message)

    def unhexlify_crypto_key(self):
        try:
            return binascii.unhexlify(self.crypto_key)
        except TypeError:
            warnings.warn('Crypto Key could not be unhexlified')
            return None

    def gen_key(self, *args, **kwargs):
        key = os.urandom(self.block_size)
        return binascii.hexlify(key)


class CryptoKeyFileManager(object):

    CipherClass = AESCipher

    def __init__(self, crypto_key_path):
        self.path = crypto_key_path
        try:
            self.key = self.read_key_file()
        except IOError:
            self.key = self.create_key_file()
        if self.key is None:
            self.key = self.create_key_file()

        self.cipher = self.CipherClass(self.key)
        self.unhexlify_key = binascii.unhexlify(self.key)

    def read_key_file(self):
        with open(self.path, "rb") as crypto_key_file:
            return crypto_key_file.read().strip().decode('unicode_escape')

    def create_key_file(self):
        mktree(os.path.dirname(self.path))
        os.chmod(os.path.dirname(self.path), stat.S_IRWXU)
        return self.write_key_file(self.CipherClass().crypto_key)

    def write_key_file(self, crypto_key):
        with open(self.path, 'wb') as key_file:
            if six.PY3:
                key_file.write(crypto_key)
            else:
                key_file.write(crypto_key.decode('utf-8'))
            os.chmod(self.path, stat.S_IRUSR + stat.S_IWRITE)
        return crypto_key

    def __str__(self):
        return self.key


class Vault(object):

    def __init__(self, config_file_path, crypto_key_file=DEFAULT_CRYPTO_KEY_FILE,  test_mode=False):
        self.cipher_manager = CryptoKeyFileManager(crypto_key_file)
        self.config_file_path = config_file_path
        self.check_config_file_path_has_been_set()
        mktree(os.path.dirname(self.config_file_path))
        self.test_mode = test_mode
        self.config = ConfigParser()
        self.cipher = self.cipher_manager.cipher
        self.read_encrypted_config()

    def get(self, section, option, test_value=None):
        try:
            setting = self.config.get(section, option)
            setting = self.cipher.decrypt(setting)
        except (NoSectionError, NoOptionError):
            setting = self.prompt(message="[{}] {}".format(section, option), test_value=test_value)
            self.save_encrypted_setting(section, option, setting)
        return setting

    def read_encrypted_config(self):
        return self.config.read(self.config_file_path)

    def write_encrypted_config(self):
        with open(self.config_file_path, 'w') as cnf_file:
            self.config.write(cnf_file)

    def check_or_create_section(self, section):
        if not self.config.has_section(section):
            self.config.add_section(section)

    def save_encrypted_setting(self, section, option, value):
        self.check_or_create_section(section)

        self.config.set(section, py3_unicode(option), py3_unicode(self.cipher.encrypt(value)))
        self.write_encrypted_config()

    def check_config_file_path_has_been_set(self):
        if self.config_file_path is None:
            raise ImproperlyConfigured("{} should define config_file_path attribute, where the encripted settings\n"
                                            "will be stored.".format(self.__class__.__name__))

    @staticmethod
    def prompt(message, test_value=None, hide=False):
        """
        Deal with python2 python3 input differences and don't show what's typed for password like inputs
        """
        if test_value:
            return test_value

        if use_password_prompt(message) or hide:
            return hidden_prompt('%s: ' % message)
        else:
            return input('%s: ' % message)


def use_password_prompt(message):

    has_password = 'password' in message.lower()
    has_secret = 'secret' in message.lower()
    if has_password or has_secret or message in OTHER_PASSWORD_FIELDS:
        return True
    return False


class DictionarySettings(Vault):
    test = None
    config = ConfigParser()
    alias = None
    alias_fixed = None
    public_fields = []
    secret_fields = []
    mapped_fields = []
    mappings = {}

    def __init__(self, config_file_path, crypto_key_file=DEFAULT_CRYPTO_KEY_FILE, test_mode=False,
                 public_fields=None, secret_fields=None, mapped_fields=None, mappings=None):
        super(DictionarySettings, self).__init__(config_file_path, crypto_key_file=crypto_key_file, test_mode=test_mode)
        self._set_fields('public_fields', public_fields)
        self._set_fields('secret_fields', secret_fields)
        self._set_mapped_fields(mapped_fields, mappings)

    def _set_fields(self, attr_name, field_name_list):
        if field_name_list and isinstance(field_name_list, list):
            setattr(self, attr_name, field_name_list)
        elif field_name_list:
            raise ImproperlyConfigured('{} parameter must be a list'.format(attr_name))
        if not getattr(self, attr_name):
            warnings.warn('No public_fields at {}'.format(self.__class__.__name__), RuntimeWarning)

    def _set_mapped_fields(self, mapped_fields, mappings):
        has_fields_but_no_mappings, has_fields_and_mapping, passed_fields = self._mapped_fields_conditions(
            mapped_fields, mappings)

        if has_fields_but_no_mappings:
            raise ImproperlyConfigured('Can not define mapped_fields without defining mappings')

        elif has_fields_and_mapping:
            if passed_fields:
                self._ensure_all_mapped_fields_have_mapping(mapped_fields, mappings)
                self.mapped_fields = mapped_fields
                self.mappings = mappings
            else:
                self._ensure_all_mapped_fields_have_mapping(self.mapped_fields, self.mappings)

    def _mapped_fields_conditions(self, mapped_fields, mappings):
        has_fields_but_no_mappings = (mapped_fields and not mappings) or (self.mapped_fields and not self.mappings)
        has_mapped_fields_and_mapping = (mapped_fields and mappings) or (self.mapped_fields and self.mappings)
        passed_fields = mapped_fields and mappings
        return has_fields_but_no_mappings, has_mapped_fields_and_mapping, passed_fields

    def _ensure_all_mapped_fields_have_mapping(self, mapped_fields, mappings):
        for field_name in mapped_fields:
            if not mappings.get(field_name):
                raise ImproperlyConfigured('You did not define mappings for field {} at {}'.format(
                    field_name, self.__class__.__name__))

    def settings(self, alias, test=None, public_fields=None, secret_fields=None, mapped_fields=None, mappings=None):
        self.alias = alias
        self.alias_fixed = self.alias.replace('default', 'default_db')
        if six.PY2:
            self.alias_fixed = self.alias_fixed.decode('utf-8')

        self.test = test
        return self.get_dict_settings()

    def create_alias(self):
        if self.alias_fixed not in self.config.sections():
            self.config.add_section('{}'.format(self.alias_fixed))

    def get_dict_settings(self):
        self.read_config()
        alias_exists = self.alias_fixed in self.config.sections()
        if alias_exists:
            return self._get_decrypted_config()
        else:
            return self.populate_alias()

    def populate_alias(self):
        self.create_alias()
        self.create_database_config_file()
        return self.get_dict_settings()

    def _get_decrypted_config(self):
        dbconfig = {}
        options = self.config.options(self.alias_fixed)
        for option in options:
            dbconfig[option] = self.cipher.decrypt(self.config.get(self.alias_fixed, option))
        return dbconfig

    def read_config(self):
        cfg_path = self.get_path()
        self.config.read(cfg_path)

    def get_path(self):
        if self.config_file_path is None:
            cfg_path = DEFAULT_DATABASES_CONF
        else:
            cfg_path = self.config_file_path
        return cfg_path

    def create_database_config_file(self):
        if os.path.isfile(self.get_path()):
            self.config.read(self.get_path())
        if self.test is None:
            self.prompt_for_database_settings(self.config)
        else:
            self.set_test(self.config, self.alias)

        with open(self.config_file_path, 'w') as cfgfile:
            self.config.write(cfgfile)

    def prompt_for_database_settings(self, config):
        self.mapped_fields_prompt(config)
        self.public_fields_prompt(config)
        self.secret_fields_prompt(config)

    def mapped_fields_prompt(self, config):
        for field in self.mapped_fields:
            options = ', '.join(self.mappings[field].keys())
            input_value = prompt('{} (options: {})'.format(field, options))
            self.set_value(config, field, self.mappings[field][input_value])

    def set_value(self, config, field, input_value):
        config.set(self.safe_alias, py3_unicode(field),
                   py3_unicode(self.cipher.encrypt(input_value)))

    def public_fields_prompt(self, config):
        for field in self.public_fields:
            input_value = prompt('{}'.format(field))
            self.set_value(config, field, input_value)

    def secret_fields_prompt(self, config):
        for field in self.secret_fields:
            input_value = hidden_prompt('{}'.format(field))
            self.set_value(config, field, input_value)

    @property
    def safe_alias(self):
        return py3_unicode(self.alias.replace('default', 'default_db'))

    def set_test(self, test, alias):
        if isinstance(test, dict):
            self.set_test_from_dict(test, alias)
        else:
            self.set_test_from_dict({
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': u'test_db_name',
                'USER': u'test_user',
                'PASSWORD': u'test_password',
                'HOST': u'test_host',
                'PORT': u'5432',
            }, alias)

    def set_test_from_dict(self, test, database_alias):
        for option, value in test.items():
            self.config.set(database_alias.replace('default', 'default_db'), py3_unicode(option), py3_unicode(self.cipher.encrypt(value)))


class DjangoDatabaseSettings(DictionarySettings):
    public_fields = ['NAME', 'HOST', 'PORT', 'USER']
    secret_fields = ['PASSWORD']
    mapped_fields = ['ENGINE']
    mappings = {
        'ENGINE': {
            'postgres': 'django.db.backends.postgresql',
            'mysql': 'django.db.backends.mysql',
            'sqlite': 'django.db.backends.sqlite3',
            'oracle': 'django.db.backends.oracle',
        }
    }

    def settings(self, alias, test=None, public_fields=None, secret_fields=None, mapped_fields=None, mappings=None):
        settings = super(DjangoDatabaseSettings, self).settings(
            alias, test=test, public_fields=public_fields, secret_fields=secret_fields, mapped_fields=mapped_fields,
            mappings=mappings
        )
        return {k.upper(): v for k, v in settings.items()}


class SqlAlchemyDatabaseSettings(DictionarySettings):
    # TODO: Test
    public_fields = ['host', 'port', 'username', 'database']
    secret_fields = ['password']
    mapped_fields = ['drivername']
    mappings = {
        'drivername': {
            'postgresql+psycopg2': 'postgresql+psycopg2',
            'postgresql': 'postgresql',
            'sqlite': 'sqlite',
            'sqlite+pysqlite': 'sqlite+pysqlite',
            'mysql': 'mysql',
            'mysql+mysqlconnector': 'mysql+mysqlconnector',
            'mysql+mysqldb': 'mysql+mysqldb',
            'mysql+oursql': 'mysql+oursql',
        }
    }


class DjangoSecretKey(Vault):
    @property
    def key(self):
        try:
            return self.cipher.decrypt(open(self.config_file_path, 'rb').read().strip())
        except IOError:
            return self.create_encripted_config()

    def read_encrypted_config(self):
        pass

    def create_encripted_config(self):
        key = self.generate_random_secret_key()
        with open(self.config_file_path, 'wb') as secret:
            print('create_encrypted_config key=', key, type(key))
            secret.write(self.cipher.encrypt(key))
        return key

    @staticmethod
    def generate_random_secret_key():
        key = ''.join(
            [random.SystemRandom().choice("{}{}{}".format(string.ascii_letters, string.digits, string.punctuation))
             for i in range(50)])
        return key
