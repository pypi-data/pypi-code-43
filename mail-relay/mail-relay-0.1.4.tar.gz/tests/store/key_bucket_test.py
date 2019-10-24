import random

from mail_relay.config import Config, CSConfig, IMAPConfig, SMTPConfig
from mail_relay.store.handlers import (read_config, read_key, read_keys,
                                       read_users, update_config, write_key,
                                       write_user)
from pvHelpers.crypto import PVKeyFactory
from pvHelpers.utils import randUnicode

from ..utils import rand_user_id, test_local_user, users_equal


def key_bucket_test(store):
    for _ in xrange(random.randint(0, 10)):
        test_user = rand_user_id()
        account_version = random.randint(0, 1000)
        key_version_count = random.randint(0, 40)
        for i in xrange(key_version_count):
            k = PVKeyFactory.newUserKey(i)
            write_key(test_user, account_version, k, store)
            k2 = read_key(test_user, account_version, i, store)
            assert k2 == k

        keys = read_keys(test_user, account_version, store)
        assert len(keys) == key_version_count


def user_bucket_test(store):
    test_users = []
    for _ in xrange(random.randint(0, 10)):
        test_users.append(test_local_user())
        write_user(test_users[-1], store)

    users = read_users(store)
    for tu in test_users:
        assert users_equal(tu, users[(tu.account_version, tu.user_id)])


def config_bucket_test(store):
    config = read_config(store)
    assert config is None

    test_config = Config(
        SMTPConfig(randUnicode(10), random.randint(0, 55555), randUnicode(10), randUnicode(10), rand_user_id(), False),
        IMAPConfig(randUnicode(10), random.randint(0, 55555), randUnicode(10), randUnicode(10), False),
        CSConfig(randUnicode(10), random.randint(0, 55555), False)
    )
    update_config(test_config, store)
    config = read_config(store)
    assert config.smtp.password == test_config.smtp.password

    test_config.smtp.password = randUnicode(10)
    update_config(test_config, store)
    config2 = read_config(store)
    assert config2.smtp.password == test_config.smtp.password
