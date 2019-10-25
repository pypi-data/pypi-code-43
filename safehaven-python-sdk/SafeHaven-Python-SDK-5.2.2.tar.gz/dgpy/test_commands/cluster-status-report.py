#!/usr/bin/python
#
# Request a (DVOL) cluster status report from the CMS and print it in JSON format.
#
from google.protobuf import json_format
from dgpy.cms_client import CmsClient
from dgpy.errors     import GrpcError

try:
    print json_format.MessageToJson(CmsClient().cluster_status_report())
except GrpcError as e:
    print "Failed to obtain a DVOL cluster status report: {0}".format(e)
