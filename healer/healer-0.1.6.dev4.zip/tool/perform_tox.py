#!/usr/bin/env python

"""
PyPi release testing.
"""

from __future__ import annotations

from devrepo import shell

shell(f"tox")

# select_list = " ".join([
#     "src/test/healer_test/device/actor/cms50f_test.py",
#     "src/test/healer_test/device/usb/cms50f_test.py",
# ])

# select_list = " ".join([
#     "src/test/healer_test/system/notify_test.py",
# ])

# shell(f"tox -- {select_list}")
