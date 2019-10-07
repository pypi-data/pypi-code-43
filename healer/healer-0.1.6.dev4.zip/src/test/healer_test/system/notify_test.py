"""
"""

import time

from healer.system.notify import *


def test_notify_message():
    print()

    notify = NotifyUnit("bada-boom", "hello-kitty")

    notify.open()
    notify.open()
    notify.open()

    print(f"notify={notify}")

    for index in range(3):
        print(f"index={index}")
        notify.message = f"index={index}"
        time.sleep(0.2)

    notify.close()
    notify.close()
    notify.close()


def test_user_list():
    print()
    user_list = NotifySupport.runtime_user_list()
    print(f"user_list: {user_list}")
