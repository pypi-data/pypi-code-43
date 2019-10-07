# -*- coding: utf-8 -*-

import datetime
from lbdrabbit import LbdFuncConfig


def handler(event, context):
    print("now is %s" % datetime.datetime.utcnow())


handler.__lbd_func_config__ = LbdFuncConfig()
handler.__lbd_func_config__.scheduled_job_yes = True
handler.__lbd_func_config__.scheduled_job_expression = "cron(15 10 * * ? *)"
