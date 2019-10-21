#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The nsh-item Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
date_sub

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/2/18
"""

import datetime
from dateutil.relativedelta import relativedelta


def date_sub(date, i):
    d = datetime.datetime.strptime(date, '%Y-%m-%d')
    return (d - relativedelta(days=i)).strftime('%Y-%m-%d')
