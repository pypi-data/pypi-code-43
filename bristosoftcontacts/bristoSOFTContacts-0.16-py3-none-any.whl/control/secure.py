#!/usr/bin/python3
#
#
# Copyright 2016 Kirk A Jackson DBA bristoSOFT all rights reserved.  All methods,
# techniques, algorithms are confidential trade secrets under Ohio and U.S.
# Federal law owned by bristoSOFT.
#
# Kirk A Jackson dba bristoSOFT
# 4100 Executive Park Drive
# Suite 11
# Cincinnati, OH  45241
# Phone (513) 401-9114
# email jacksonkirka@bristosoft.com
#
# The trade name bristoSOFT is a registered trade name with the State of Ohio
# document No. 201607803210.

'''
This secure module provides security for bristoSOFT Contacts v. 0.1.
It uses Python's hashlib, uuid and re modules.  A one way salted
hash is used to encrypt the user password.  The actual password is
not stored in the database.
'''
import hashlib
import uuid
import re

class Security:

    '''
    The Security class provides resources to maintain secure communication
    and authentication in contacts.
    '''
    @staticmethod
    def mincomplex(_pwd):
        r'''
        mincomplex evaluates a plain text password and returns true if the
        password evaluated contains 1) uppercase letter, 2) lowercase letter,
        3) a digit 0 - 9, 4) a special character and 5) is at least 8 characters.

        >>> sec = Security()
        >>> test_digit = sec.mincomplex('Bmw$4839')
        >>> test_digit
        True
        >>> test_digit = sec.mincomplex('Bmw$xkeo')
        >>> test_digit
        False
        >>> test_lower = sec.mincomplex('Bmw$4839')
        >>> test_lower
        True
        >>> test_lower = sec.mincomplex('BMW$4839')
        >>> test_lower
        False
        >>> test_upper = sec.mincomplex('Bmw$4839')
        >>> test_upper
        True
        >>> test_upper = sec.mincomplex('bmw$xkeo')
        >>> test_upper
        False
        >>> test_special = sec.mincomplex('Bmw$4839')
        >>> test_special
        True
        >>> test_special = sec.mincomplex('BmwZ4839')
        >>> test_special
        False
        >>> test_eight = sec.mincomplex('Bmw$4839')
        >>> test_eight
        True
        >>> test_eight = sec.mincomplex('Bmw$483')
        >>> test_eight
        False
        '''
        _digit = re.search('[0-9]', _pwd)
        _lower = re.search('[a-z]', _pwd)
        _upper = re.search('[A-Z]', _pwd)
        _special = re.search('.[!@#$%^&*()_~-]',_pwd)

        if len(_pwd) > 7 and _digit and _lower and _upper and _special:
            return True
        else:
            return False

    @staticmethod
    def hashpwd(_pwd):

        '''
        hashpwd hashes a password by NSA Secure Hash Algorithm 2
        sha256 algorithm and adds a uuid prefix salt.

        >>> sec = Security()
        >>> hashed_password = sec.hashpwd('Bmw$535is')
        >>> _pwd = 'Bmw$535is'
        >>> hashed_password_split, salt_prefix = hashed_password.split(':')
        >>> manual_hash_pwd = hashlib.sha256(salt_prefix.encode() +
        ... _pwd.encode()).hexdigest() + ':' + salt_prefix
        >>> hashed_password == manual_hash_pwd
        True
        >>> _pwd = 'Bmw$435is'
        >>> manual_hash_pwd = hashlib.sha256(salt_prefix.encode() +
        ... _pwd.encode()).hexdigest() + ':' + salt_prefix
        >>> hashed_password == manual_hash_pwd
        False

        '''
        salt = uuid.uuid4().hex
        return hashlib.sha256(salt.encode() +
            _pwd.encode()).hexdigest() + ':' + salt

    @staticmethod
    def authenticatepwd(_dbhashpwd, _usrpwd):

        '''
        authenticatepwd authenticates the password entered by the user by
        comparing the database hash with a hash of the user entered
        password.

        >>> sec = Security()
        >>> salt = uuid.uuid4().hex
        >>> _dbhashpwd = hashlib.sha256(salt.encode() +
        ... 'Guest$123'.encode()).hexdigest() + ':' + salt
        >>> dbpwd, salt = _dbhashpwd.split(':')
        >>> _usrpwd = 'Guest$123'
        >>> usrhashedpwd = hashlib.sha256(salt.encode() +
        ... _usrpwd.encode()).hexdigest()
        >>> dbpwd == usrhashedpwd
        True
        >>> match = sec.authenticatepwd(_dbhashpwd,_usrpwd)
        >>> match
        True
        >>> _dbhashpwd = hashlib.sha256(salt.encode() +
        ... 'Guest$123'.encode()).hexdigest() + ':' + salt
        >>> dbpwd, salt = _dbhashpwd.split(':')
        >>> _usrpwd = 'Guost$124'
        >>> usrhashedpwd = hashlib.sha256(salt.encode() +
        ... _usrpwd.encode()).hexdigest()
        >>> dbpwd == usrhashedpwd
        False
        >>> match = sec.authenticatepwd(_dbhashpwd,_usrpwd)
        >>> match
        False
        '''
        dbpwd, salt = _dbhashpwd.split(':')
        return dbpwd == hashlib.sha256(salt.encode() +\
            _usrpwd.encode()).hexdigest()

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)


