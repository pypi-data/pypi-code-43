#!/usr/bin/python
#
# Print details of all known Protection Groups (DVOLs).
#
from dgpy.cms_client             import CmsClient
from dgpy.aggregates.dvol        import dvol_pb2, dvol_enums_pb2
from dgpy.aggregates.dvol.pg     import pg_enums_pb2
from dgpy.safehaven.api.types    import types_enums_pb2
from dgpy.aggregates.dvol.target import target_enums_pb2

dvols = CmsClient().dvol_list()
if dvols:
    cols = ("Name", "Master", "Remote", "Status", "Type", "OS", "Sbd Type", "Disk Type", "Guest")
    print "| {0:<20} | {1:^15} | {2:^15} | {3:^20} | {4:^8} | {5:^8} | {6:^10} | {7:^30} | {8:^9} |".format(*cols)
    print "| {0:<20} | {1:^15} | {2:^15} | {3:^20} | {4:^8} | {5:^8} | {6:^10} | {7:^30} | {8:^9} |".format(*('-' * len(c) for c in cols))

    for pg in sorted(dvols, key=lambda pg: pg.name):
        statusString = dvol_enums_pb2.DvolStatus.Name(pg.status)
        if pg.has_image and pg.status not in (dvol_enums_pb2.TEST_FAILOVER, dvol_enums_pb2.TEST_FAILOVER_FAILED):
            statusString += " (TFO)"

        print "| {0:<20} | {1:>15} | {2:>15} | {3:^20} | {4:^8} | {5:^8} | {6:^10} | {7:^30} | {8:^9} |".format(pg.name,
                pg.ms_ip,
                pg.rs_ip,
                statusString,
                pg_enums_pb2.ProtectionType.Name(pg.protection_type),
                target_enums_pb2.OsCategory.Name(pg.os_category),
                "/".join((types_enums_pb2.SbdType.Name(pg.primary_sbd_type),
                          types_enums_pb2.SbdType.Name(pg.secondary_sbd_type))),
                "/".join((dvol_enums_pb2.DvolLegDiskType.Name(pg.primary_disk_type),
                          dvol_enums_pb2.DvolLegDiskType.Name(pg.secondary_disk_type))),
                dvol_enums_pb2.GuestType.Name(pg.guest_type),
        )
else:
    print "dvol-list: empty result"
