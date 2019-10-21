#
# Copyright (c) 2006-2019 Balabit
# All Rights Reserved.
#
import re


def plugin_sdk_installed(pip_requirements):
    pattern = r'^oneidentity[_-]safeguard[_-]sessions[_-]plugin[_-]sdk'
    return re.search(pattern, pip_requirements, re.MULTILINE) is not None
