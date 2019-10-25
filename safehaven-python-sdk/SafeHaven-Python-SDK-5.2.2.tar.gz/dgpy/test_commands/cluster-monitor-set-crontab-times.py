#!/usr/bin/python
#
# Set the crontab(5) settings for the periodic cluster status reports.
#
# Usage: $0 check|email <spec>, with
#         - check|email: whether to configure periodic 'email' or 'check'
#         - @spec: quoted string, one of
#           + "<min> <hour> <day-of-week>", e.g.: "0 12 THU", "30 9 *", "11 11 THU",
#           + expected format: "{0..59} {0..23} {*|SUN|MON|TUE|WED|THU|FRI|SAT}"
#           + "" (empty string) to disable the check or email setting.
#
import sys
from dgpy.cms_client              import CmsClient
from dgpy.safehaven.cron.cron_pb2 import ClusterMonitorSpec
from dgpy.errors                  import GrpcError

if len(sys.argv) != 3 or sys.argv[1] not in ('check', 'email'):
    print >>sys.stderr, 'Usage:   %s check|email <spec>' % sys.argv[0]
    print >>sys.stderr, 'Example: %s check "0 12 THU"' % sys.argv[0]
else:
    try:
        spec = ClusterMonitorSpec()
        if sys.argv[1] == 'check':
            spec.report_check_repeat = sys.argv[2]
            spec.report_email_repeat = "* * *"      # keep
        elif sys.argv[1] == 'email':
            spec.report_check_repeat = "* * *"      # keep
            spec.report_email_repeat = sys.argv[2]
        res = CmsClient().cluster_monitor_set_cron(spec)
    except GrpcError as e:
        print "Failed to configure cluster monitor crontab entries: {0}".format(e)
    else:
        print "Configure cluster crontab entries Job ID: {0}".format(res.job_id)
