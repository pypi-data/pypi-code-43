#!/usr/bin/python
#
# Resize a non-legacy PG from a .yaml or .json input file.
#
import os
import sys
from dgpy.cms_client      import CmsClient
from dgpy.utils           import die, fatal, load_protobuf
from dgpy.aggregates.dvol import dvol_pb2
from dgpy.errors          import GrpcError

if len(sys.argv) != 2:
    die("Usage: %s <parameter-file.{json|yaml}>" % sys.argv[0])
elif not os.path.exists(sys.argv[1]):
    fatal("No such file %r" % sys.argv[1])
else:
    try:
        req = load_protobuf(sys.argv[1], dvol_pb2.PgResizeRequest())
        res = CmsClient().pg_resize(req)
    except GrpcError as e:
        print "Failed to resize {0.name}: {1}".format(req, e)
    else:
        print "Resize {0.name} Job ID: {1}".format(req, res.job_id)
