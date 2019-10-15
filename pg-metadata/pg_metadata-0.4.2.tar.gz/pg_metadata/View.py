#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata._System import SEP, ParseACL

QUERY_VIEW = """
    SELECT
        c.oid,
        trim(lower(n.nspname)) AS schema,
        trim(lower(c.relname)) AS name,
        trim(lower(r.rolname)) AS owner,
        trim(coalesce(obj_description(c.oid), '')) AS comment,
        pg_get_viewdef(c.oid, true) as definition,
        c.relacl::varchar[],
        c.relkind = 'm' as is_materialized
    FROM pg_class c
    JOIN pg_namespace n ON
        n.oid = c.relnamespace AND
        n.nspname != ALL(%s)
    JOIN pg_roles r ON
        r.oid = c.relowner
    WHERE c.relkind in ('v','m')
    ORDER BY 2,3
"""

class View():
    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Oid = row.get('oid')
        assert self.Oid is not None and self.Oid > 0

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip()
        assert len(self.Schema) > 0

        self.Name = row.get('name') or ''
        self.Name = self.Name.strip()
        assert len(self.Name) > 0

        self.FullName = "%s.%s" % (self.Schema, self.Name)

        self.Owner = row.get('owner') or ''
        self.Owner = self.Owner.strip()
        assert len(self.Owner) > 0

        self.Comment = row.get('comment') or ''
        self.Comment = self.Comment.strip()

        self.Definition = row.get('definition') or ''
        self.Definition = self.Definition.strip()
        assert len(self.Definition) > 0

        self.IsMaterialized = row.get("is_materialized")

        self.Folder = "view"

        self.Grants = ParseACL(row.get("relacl"), self.Owner)

        self.Indexes     = []

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        r = ""

        if self.IsMaterialized:
            r += "CREATE MATERIALIZED VIEW %s AS" % (self.FullName)
        else:
            r += "CREATE OR REPLACE VIEW %s AS" % (self.FullName)
        r += SEP
        r += self.Definition

        return r

    def QueryRemove(self):
        if self.IsMaterialized:
            return 'DROP MATRIALIZED VIEW IF EXISTS %s.%s;' % (self.Schema, self.Name)
        else:
            return 'DROP VIEW IF EXISTS %s.%s;' % (self.Schema, self.Name)

    def QueryComment(self):
        if self.IsMaterialized:
            return "COMMENT ON MATERIALIZED VIEW %s IS '%s';" % (self.FullName, self.Comment)
        else:
            return "COMMENT ON VIEW %s IS '%s';" % (self.FullName, self.Comment)

    def QueryOwner(self):
        return 'ALTER TABLE %s OWNER TO %s;' % (self.FullName, self.Owner)

    def QueryGrants(self):
        r = []

        for role_name, gr in self.Grants.items():
            types = ", ".join(gr.get("types"))
            if gr.get("is_grant"):
                r.append("GRANT %s ON TABLE %s TO %s;" % (types, self.FullName, role_name))
            else:
                r.append("REVOKE %s ON TABLE %s FROM %s;" % (types, self.FullName, role_name))

        return SEP.join(sorted(r))

    def QueryDDL(self):
        result = ''
        result += self.QueryRemove()
        result += SEP
        result += SEP
        result += self.QueryAdd()
        result += SEP
        result += SEP
        result += self.QueryOwner()
        result += SEP
        result += self.QueryGrants()
        result += SEP
        result += SEP
        result += self.QueryComment()
        result += SEP
        result += SEP
        for ind in self.Indexes:
            result += ind.QueryAdd()
            result += SEP
            result += SEP
        return result.strip() + SEP
