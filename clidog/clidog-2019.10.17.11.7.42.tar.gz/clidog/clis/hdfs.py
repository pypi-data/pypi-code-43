#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : hdfs
# @Time         : 2019-08-27 14:12
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os


class hdfs(object):
    """
    hdfspath=hdfs://zjyprc-analysis/user/sql_prc/warehouse/kudu_demo.db/h_fenqun_3844_20190827
    hdfs --cluster zjyprc-hadoop dfs -getmerge $hdfspath ./data
    hdfs --cluster zjyprc-hadoop dfs -put ./data  /user/h_browser/algo/yuanjie/UserGroups/军事
    """

    def __init__(self):
        pass

    def get(self):
        pass

    def getmerge(self):
        pass
