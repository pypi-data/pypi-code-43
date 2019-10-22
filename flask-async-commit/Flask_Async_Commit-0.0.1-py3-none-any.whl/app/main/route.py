# ! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    package.module
    ~~~~~~~~~~~~~~

    A brief description goes here.

    :copyright: (c) Jimmy@2018年03月16日.
"""

from flask import Blueprint, g, request
from app.main.models import *

main = Blueprint('main', __name__)

@main.route('/account/storeList', methods=['GET', 'POST'])
def _store_list():
    pass
