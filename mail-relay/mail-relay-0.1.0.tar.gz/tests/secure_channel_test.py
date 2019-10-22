import os
import time

from mail_relay.secure_channel import GetMessageManager, TransferTypes
from pvHelpers.crypto import PVKeyFactory
from pvHelpers.cs_client import BACKEND_CLIENT
from pvHelpers.request import DeviceRequest
from pvHelpers.user import LocalDevice, LocalUser
from pvHelpers.utils import NOT_ASSIGNED
import pytest

from .utils import crypto_create_account, crypto_send_user_key, rand_user_id


@pytest.mark.integration
def transfer_user_account_test(test_config):
    user_id = rand_user_id()

    # create account in crypto
    crypto_create_account(os.environ['CRYPTO_HOST'], os.environ['CRYPTO_PORT'], user_id)
    send_pin_handle = crypto_send_user_key(os.environ['CRYPTO_HOST'], os.environ['CRYPTO_PORT'], user_id)

    def verifier(pin):
        # sleep needed for sockets read/write timing sequence
        time.sleep(0.1)
        send_pin_handle(pin)
        return True

    def callback(transferred_user_key, device_req_signature):
        user_key = PVKeyFactory.deserializeUserKey(transferred_user_key, is_protobuf=False)
        user = LocalUser(
            user_id, -153, user_id, u'', None, NOT_ASSIGNED(), u'', [user_key], device_req.device)

        # check user is authorized
        BACKEND_CLIENT.init(test_config.cs.http)
        BACKEND_CLIENT.getUserDevices(user)
        return True

    device_req = DeviceRequest.newForTransfer(user_id, LocalDevice.newDevice())
    manager = GetMessageManager(
        test_config.cs.ws, user_id, user_id, TransferTypes.TRANSFER, verifier, callback)

    # test blocks here till `callback` function returns
    manager.get_secure_channel(new_device_req=device_req)
