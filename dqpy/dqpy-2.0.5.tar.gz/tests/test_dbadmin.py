import subprocess
import unittest

from sqlalchemy_utils import database_exists


class TestDatabase(unittest.TestCase):

    def test_create_drop(self):
        db = 'mysql+pymysql://root@127.0.0.1:3306/dqpy_dbadmin?charset=utf8mb4'
        subprocess.Popen(
            'dbadmin create dbadmin_sql.url',
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        assert database_exists(db)

        subprocess.Popen(
            'dbadmin drop dbadmin_sql.url',
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.read()
        assert not database_exists(db)

    def test_create_error(self):
        error = subprocess.Popen(
            'dbadmin create wrong', shell=True, stdout=subprocess.PIPE,
        ).stdout.read()
        assert 'Unable to create database' in str(error)

    def test_drop_error(self):
        error = subprocess.Popen(
            'dbadmin drop wrong', shell=True, stdout=subprocess.PIPE,
        ).stdout.read()
        assert 'Unable to drop database' in str(error)
