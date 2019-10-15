#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata._System import SEP, ParseACL

class Function():
    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Oid = row.get('oid')
        assert self.Oid is not None and self.Oid > 0

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip()
        assert len(self.Schema) > 0

        self.Name = row.get('proc') or ''
        self.Name = self.Name.strip()
        assert len(self.Name) > 0

        self.ArgsInTypes = row.get('args_in_types') or ''
        self.ArgsInTypes = self.ArgsInTypes.strip()

        # self.FullName = "%s.%s(%s)" % (self.Schema, self.Name, self.ArgsInTypes)
        self.FullName = "%s.%s" % (self.Schema, self.Name)

        self.ArgsIn = row.get('args_in') or ''
        self.ArgsIn = self.ArgsIn.strip()

        self.ArgsOut = row.get('args_out') or ''
        self.ArgsOut = self.ArgsOut.strip()

        self.Cost = row.get('cost') or 0
        self.Cost = self.Cost

        self.Rows = row.get('rows') or 0
        self.Rows = self.Rows

        self.Owner = row.get('owner') or ''
        self.Owner = self.Owner.strip()
        assert len(self.Owner) > 0

        self.Language = row.get('lang') or ''
        self.Language = self.Language.strip()
        assert len(self.Language) > 0

        self.Comment = row.get('comment') or ''
        self.Comment = self.Comment.strip()

        self.Volatility = row.get('volatility') or ''
        self.Volatility = self.Volatility.strip()
        assert len(self.Volatility) > 0

        self.HasDuplicate = row.get('has_duplicate') or False
        self.IsTrigger = row.get('is_trigger') or False
        self.IsRecord = row.get('is_record') or False

        self.Code = row.get('code') or ''
        self.Code = self.Code.strip()
        assert len(self.Code) > 0

        self.Folder = 'triggers' if self.IsTrigger else 'functions'

        self.Grants = ParseACL(row.get("proacl"), self.Owner)

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        result = ''
        result += 'CREATE OR REPLACE FUNCTION %s.%s' % (self.Schema, self.Name)
        result += self.QueryArgsIn()
        result += 'RETURNS %s AS' % (self.QueryArgsOut())
        result += SEP
        result += '$BODY$'
        result += SEP
        result += self.Code
        result += SEP
        result += '$BODY$'
        result += SEP
        result += '  LANGUAGE %s %s' % (self.Language, self.Volatility)

        if self.Cost > 0:
            result += SEP
            result += '  COST %s' % (int(self.Cost))

        if self.Rows > 0:
            result += SEP
            result += '  ROWS %s' % (int(self.Rows))

        result += ';'

        return result

    def QueryRemove(self):
        return 'DROP FUNCTION %s(%s);' % (self.FullName, self.ArgsInTypes)

    def QueryArgsIn(self):
        if len(self.ArgsIn or '') == 0:
            return "()" + SEP
        else:
            r = ""
            r += "("
            r += SEP
            r += "    %s" % (self.ArgsIn.replace(',', ',%s   ' % (SEP)))
            r += SEP
            r += ")"
            r += SEP
            return r

    def QueryArgsOut(self):
        if self.IsRecord:
            return self.ArgsOut.replace(',', ',\n   ').replace('TABLE(', 'TABLE(\n    ').replace(')', '\n)')
        else:
            return self.ArgsOut

    def QueryComment(self):
        return "COMMENT ON FUNCTION %s(%s) IS '%s';" % (self.FullName, self.ArgsInTypes, self.Comment)

    def QueryOwner(self):
        return "ALTER FUNCTION %s(%s) OWNER TO %s;" % (self.FullName, self.ArgsInTypes, self.Owner)

    def QueryGrants(self):
        r = []

        for role_name, gr in self.Grants.items():
            types = ", ".join(gr.get("types"))

            if gr.get("is_grant"):
                r.append("GRANT %s ON FUNCTION %s(%s) TO %s;" % (types, self.FullName, self.ArgsInTypes, role_name))
            else:
                r.append("REVOKE %s ON FUNCTION %s(%s) FROM %s;" % (types, self.FullName, self.ArgsInTypes, role_name))

        return SEP.join(sorted(r))

    def QueryDDL(self):
        result = ''
        result += "-- Function: %s(%s)" % (self.FullName, self.ArgsInTypes)
        result += SEP
        result += SEP
        result += "-- %s" % (self.QueryRemove())
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
        return result.strip() + SEP

QUERY_FUNCTION = """
    select
        p.oid,
        trim(lower(n.nspname)) as schema,
        trim(lower(p.proname)) as proc,
        oidvectortypes(proargtypes) as args_in_types,
        pg_get_function_arguments(p.oid) as args_in,
        pg_get_function_result(p.oid) as args_out,
        coalesce(p.procost, 0) as cost,
        coalesce(p.prorows, 0) as rows,
        trim(lower(o.rolname)) as owner,
        trim(lower(l.lanname)) as lang,
        obj_description(p.oid) as comment,
        case
            when p.provolatile = 'i' then 'IMMUTABLE'
            when p.provolatile = 's' then 'STABLE'
            when p.provolatile = 'v' then 'VOLATILE'
        end || case
            when p.proisstrict then ' STRICT'
            else ''
        end || case
            when not p.prosecdef then ''
            else ' SECURITY DEFINER'
        end as volatility,
        count(*) over (partition by n.oid, p.oid) > 1 as has_duplicate,
        coalesce(trim(lower(t.typname)), '') = 'trigger' as is_trigger,
        coalesce(trim(lower(t.typname)), '') = 'record' as is_record,
        replace(p.prosrc, E'\r', '') as code,
        p.proacl::varchar[] as proacl
    from pg_proc p
    join pg_namespace n on
        n.oid = p.pronamespace and
        n.nspname != ALL(%s)
    join pg_language l on
        l.oid = p.prolang and
        l.lanname in ('sql','plpgsql','plpythonu','plpython3u','plproxy')
    join pg_roles o on
        o.oid = p.proowner
    join pg_type t on
        t.oid = p.prorettype
    order by 1
"""
