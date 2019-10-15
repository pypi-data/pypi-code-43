#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata._System import SEP, ParseACL

QUERY_FOREIGN_SERVER = """
    select
        s.oid,
        s.srvname as server_name,
        w.fdwname as fdw_name,
        o.rolname as owner_name,
        s.srvoptions as options,
        s.srvacl::varchar[],
        obj_description(s.oid) AS comment
    from pg_foreign_server s
    join pg_roles o on
        o.oid = s.srvowner
    join pg_foreign_data_wrapper w on
        w.oid = s.srvfdw
"""

class ForeignServer():
    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Schema = "_foreign"
        self.Folder = "server"

        self.Name = row.get('server_name')
        assert self.Name is not None
        self.Name = self.Name.strip().lower()
        assert len(self.Name) > 0

        self.FDW = row.get('fdw_name')
        assert self.FDW is not None
        self.FDW = self.FDW.strip().lower()
        assert len(self.FDW) > 0

        self.Owner = row.get('owner_name')
        assert self.Owner is not None
        self.Owner = self.Owner.strip()
        assert len(self.Owner) > 0

        self.Comment = row.get("comment")

        self.Options = row.get("options")

        self.Grants = ParseACL(row.get("srvacl"), self.Owner)

    def __str__(self):
        return self.Name

    def QueryRemove(self):
        return 'DROP SERVER IF EXISTS %s;' % (self.Name)

    def QueryDDL(self):
        r = ""
        r += "-- Server: %s" % (self.Name)
        r += SEP
        r += SEP
        r += "-- %s" % (self.QueryRemove())
        r += SEP
        r += SEP
        r += "CREATE SERVER %s" % (self.Name)
        r += SEP
        r += "FOREIGN DATA WRAPPER %s" % (self.FDW)
        r += SEP
        r += "OPTIONS("
        r += SEP
        r += self.QueryOptions()
        r += SEP
        r += ");"
        r += SEP
        r += SEP

        if self.Owner is not None:
            r += self.QueryOwner()
            r += SEP

        if len(self.Grants.keys()) > 0:
            r += self.QueryGrants()
            r += SEP

        if self.Comment is not None:
            r += SEP
            r += self.QueryComment()
            r += SEP

        return r.strip() + SEP

    def QueryComment(self):
        return "COMMENT ON SERVER %s IS '%s';" % (self.Name, self.Comment)

    def QueryOwner(self):
        return "ALTER SERVER %s OWNER TO %s;" % (self.Name, self.Owner)

    def QueryOptions(self):
        result = []

        for o in sorted(self.Options):
            o = o.split("=")
            if len(o) != 2:
                continue
            result.append("    %s = '%s'" % (o[0], o[1]))

        separator = ",%s" % (SEP)
        return separator.join(result)

    def QueryGrants(self):
        r = []

        for role_name, gr in self.Grants.items():
            types = ", ".join(gr.get("types"))

            if gr.get("is_grant"):
                r.append("GRANT %s ON FOREIGN SERVER %s TO %s;" % (types, self.Name, role_name))
            else:
                r.append("REVOKE %s ON FOREIGN SERVER %s FROM %s;" % (types, self.Name, role_name))

        return SEP.join(sorted(r))
