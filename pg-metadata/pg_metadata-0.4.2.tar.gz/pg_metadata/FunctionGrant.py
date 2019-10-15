#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

QUERY_FUNCTION_GRANT = """
    SELECT *
    FROM (
        select
            p.oid,
            trim(lower(n.nspname)) as schema,
            trim(lower(p.proname)) as proc,
            regexp_split_to_table(regexp_replace(trim(p.proacl::varchar), '[\{\}]', '', 'igm'),',','im') AS proacl,
            oidvectortypes(p.proargtypes) as args_in_types
        from pg_proc p
        join pg_namespace n on
            n.oid = p.pronamespace and
            n.nspname != all(%s)
        order by 1
    ) q
    WHERE COALESCE(TRIM(q.proacl), '') != ''
"""


class FunctionGrant():

    def __init__(self, row={}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        data = re.split('[\=\/]', row.get('proacl'))

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip().lower()
        assert len(self.Schema) > 0

        self.Function = row.get('proc') or ''
        self.Function = self.Function.strip().lower()
        assert len(self.Function) > 0

        self.ArgsInTypes = row.get('args_in_types') or ''
        self.ArgsInTypes = self.ArgsInTypes.strip()

        # self.FullFunction = "%s.%s(%s)" % (self.Schema, self.Function, self.ArgsInTypes)
        self.FullFunction = "%s.%s" % (self.Schema, self.Function)

        self.Grantee = data[0].strip()
        self.ActionsFirst = data[1].strip()
        self.Grantor = data[2].strip()

        if self.Grantee == '':
            self.Grantee = 'public'

        # self.FullName = '%s.%s(%s).%s' % (self.Schema, self.Function, self.ArgsInTypes, self.Grantee)
        self.FullName = '%s.%s.%s' % (self.Schema, self.Function, self.Grantee)

        self.Actions = []

        if self.ActionsFirst.find('X') >= 0:
            self.Actions.append('EXECUTE')

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        return 'GRANT %s ON FUNCTION %s(%s) TO %s;' % (', '.join(self.Actions), self.FullFunction, self.ArgsInTypes, self.Grantee)

    def QueryRemove(self):
        return 'REVOKE ALL ON FUNCTION %s(%s) FROM %s;' % (self.FullFunction, self.ArgsInTypes, self.Grantee)
