import os
import random
import time
import uuid

import loremipsum
from mail_relay.secure_channel.websocket_wrapper import (WSError, WSNoData,
                                                         WSWebSocketWrapper)
from pvHelpers.crypto import PVKeyFactory
from pvHelpers.mail.email import EmailHelpers
from pvHelpers.user import LocalDevice, LocalUser, OrganizationInfo
from pvHelpers.utils import jdumps, NOT_ASSIGNED, randUnicode
import requests


def rand_user_id():
    return u'{}{}@preveil.test'.format(randUnicode(), os.getpid())


def test_local_device():
    return LocalDevice(
        unicode(uuid.uuid4()),
        randUnicode(10),
        PVKeyFactory.newUserKey(0),
        {},
        u'active')


def test_local_user():
    return LocalUser(
        rand_user_id(),
        random.randint(0, 1000),
        randUnicode(10),
        unicode(uuid.uuid4()),
        OrganizationInfo(
            unicode(uuid.uuid4()), randUnicode(10), randUnicode(10), random.choice([u'standard', u'admin'])),
        NOT_ASSIGNED(),
        randUnicode(10),
        [PVKeyFactory.newUserKey(i-1) for i in xrange(random.randint(1, 10))],
        test_local_device())


def create_test_mime(sender_id=None, recipient_ids=None):
    recipient_ids = recipient_ids or [rand_user_id() for _ in xrange(random.randint(1, 5))]
    sender_id = sender_id or rand_user_id()
    return '''
        X-PreVeil-Msg
        Message-ID: <{}>
        From: {} <{}>
        To: {}

        {}
        '''.format(
            EmailHelpers.newMessageId(),
            sender_id, sender_id,
            ', '.join(map(lambda i: '{} <{}>'.format(i, i), recipient_ids)),
            loremipsum.generate_paragraph()[2])


def devices_equal(d1, d2):
    return all([
        d1.id.lower() == d2.id.lower(),
        d1.name.lower() == d2.name.lower(),
        d1.status == d2.status,
        d1.metadata == d2.metadata,
        d1.key == d2.key
    ])


def org_infos_equal(o1, o2):
    return all([
        o1.org_id.lower() == o2.org_id.lower(),
        o1.role.lower() == o2.role.lower(),
        o1.dept_name.lower() == o2.dept_name.lower(),
        o1.org_name.lower() == o2.org_name.lower()
    ])


def users_equal(u1, u2):
    return all([
        u1.user_id.lower() == u2.user_id.lower(),
        u1.mail_cid.lower() == u2.mail_cid.lower(),
        u1.display_name.lower() == u2.display_name.lower(),
        org_infos_equal(u1.org_info, u2.org_info),
        all([k1 == k2 for k1 in u1.user_keys for k2 in u2.user_keys if k1.key_version == k2.key_version]),
        devices_equal(u1.device, u2.device)
    ])


def wait_for_data(socket_wrapper, timeout=2):
    current_time = time.time()
    while (time.time() - current_time) < timeout:
        data = socket_wrapper.receive()
        assert not isinstance(data, WSError)
        if isinstance(data, WSNoData):
            time.sleep(0.1)
            continue
        # data is of type WSData
        return data.message

    assert False


def crypto_create_account(crypto_host, crypto_port, user_id):
    resp = requests.put(
        u'http://{}:{}/put/test/account/{}'.format(crypto_host, crypto_port, user_id),
        headers={'Content-Type': 'application/json', 'HOST': '127.0.0.1:2002'},
        data=jdumps({'name': randUnicode(5)})
    )
    resp.raise_for_status()
    return resp.json()


def crypto_send_user_key(crypto_host, crypto_port, for_user):
    conn = WSWebSocketWrapper('ws://{}:{}/get/account/{}/key/send'.format(crypto_host, crypto_port, for_user), 4, 0.1)

    conn.send(jdumps({'user_id': for_user, 'action': 'init'}))
    result = wait_for_data(conn)
    assert result['status'] == 'ok'

    def verify_pin(pin):
        conn.send(jdumps({'user_id': for_user, 'action': 'verify', 'pin': pin}))
        conn.close()

    return verify_pin
