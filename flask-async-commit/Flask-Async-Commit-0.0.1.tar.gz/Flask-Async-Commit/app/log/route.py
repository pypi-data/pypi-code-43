# ! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    A brief description goes here.

    :copyright: (c) Jimmy@2018年03月16日.
"""

from flask import Blueprint, g, request
from app.log.models import Device
from random import randint


log = Blueprint('log', __name__)


@log.route('/')
def test():
    a = randint(0, 100)
    d = Device(id=a, date_time=a, customer_mac=a, rssi=a)
    d.cache_save()
    # d.quick_save()
    return 'hello'

