#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata._System import SEP, ParseACL

QUERY_FOREIGN_TABLE = """
    select
        c.oid,
        n.nspname as schema_name,
        c.relname as table_name,
        o.rolname as owner_name,
        s.srvname as server_name,
        t.ftoptions as options,
        obj_description(c.oid) AS comment,
        c.relacl::varchar[],
        (
            select array_agg(concat_ws(' ',
                a.attname,
                trim(lower(format_type(a.atttypid, a.atttypmod))),
                case when a.attnotnull then 'NOT NULL' end
            ))
            from pg_attribute a
            where
                a.attrelid = c.oid and
                a.attnum > 0
        ) as columns_list
    from pg_foreign_table t
    join pg_foreign_server s on
        s.oid = t.ftserver
    join pg_class c on
        c.oid = t.ftrelid
    join pg_roles o on
        o.oid = c.relowner
    join pg_namespace n on
        n.oid = c.relnamespace AND
        n.nspname != ALL(%s)
"""

class ForeignTable():
    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Folder = "foreign_table"

        self.Schema = row.get("schema_name")
        assert self.Schema is not None
        self.Schema = self.Schema.strip().lower()
        assert len(self.Schema) > 0

        self.Name = row.get('table_name')
        assert self.Name is not None
        self.Name = self.Name.strip().lower()
        assert len(self.Name) > 0

        self.FullName = "%s.%s" % (self.Schema, self.Name)

        self.Owner = row.get('owner_name')
        assert self.Owner is not None
        self.Owner = self.Owner.strip()
        assert len(self.Owner) > 0

        self.Server = row.get('server_name')
        assert self.Server is not None
        self.Server = self.Server.strip()
        assert len(self.Server) > 0

        self.Comment = row.get("comment")

        self.Options = row.get("options")

        self.Grants = ParseACL(row.get("relacl"), self.Owner)

        self.Columns = row.get("columns_list")

    def __str__(self):
        return self.Name

    def QueryRemove(self):
        return 'DROP FOREIGN TABLE IF EXISTS %s;' % (self.FullName)

    def QueryDDL(self):
        r = ""
        r += "-- Foreign Table: %s" % (self.FullName)
        r += SEP
        r += SEP
        r += "-- %s" % (self.QueryRemove())
        r += SEP
        r += SEP
        r += "CREATE FOREIGN TABLE %s(" % (self.FullName)
        r += SEP
        r += self.QueryColumns()
        r += SEP
        r += ")"
        r += SEP
        r += "SERVER %s" % (self.Server)
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
        return "COMMENT ON FOREIGN TABLE %s IS '%s';" % (self.FullName, self.Comment)

    def QueryOwner(self):
        return "ALTER FOREIGN TABLE %s OWNER TO %s;" % (self.FullName, self.Owner)

    def QueryOptions(self):
        result = []

        for o in sorted(self.Options):
            o = o.split("=")
            if len(o) != 2:
                continue
            result.append("    %s '%s'" % (o[0], o[1]))

        separator = ",%s" % (SEP)
        return separator.join(result)

    def QueryGrants(self):
        r = []

        for role_name, gr in self.Grants.items():
            types = ", ".join(gr.get("types"))

            if gr.get("is_grant"):
                r.append("GRANT %s ON TABLE %s TO %s;" % (types, self.FullName, role_name))
            else:
                r.append("REVOKE %s ON TABLE %s FROM %s;" % (types, self.FullName, role_name))

        return SEP.join(sorted(r))

    def QueryColumns(self):
        result = []
        for col in self.Columns:
            result.append("    %s" % (col))
        separator = ",%s" % (SEP)
        return separator.join(result)
