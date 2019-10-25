#!/usr/bin/python
#
# Dump the crontab(5) settings for the periodic cluster status reports.
#
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

try:
    res = CmsClient().cluster_monitor_get_cron()
    print "Periodic Health Check: {0}".format(res.report_check_repeat or "disabled")
    print "Periodic Email Report: {0}".format(res.report_email_repeat or "disabled")
except GrpcError as e:
    print "Failed to obtain cluster monitor crontab times: {0}".format(e)
