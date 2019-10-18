#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AIPipeline.
# @File         : lgb_api
# @Time         : 2019-10-12 15:58
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os
import joblib

get_module_path = lambda path, file=__file__: \
    os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(file), path))

clf = joblib.load(get_module_path("../checkpoints/lgb_test.model"))

def api(**args):
    X = args['X']
    return clf.predict(X).tolist()