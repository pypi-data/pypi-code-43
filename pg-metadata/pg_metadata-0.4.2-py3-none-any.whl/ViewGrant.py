#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

QUERY_VIEW_GRANT = """
    SELECT *
    FROM (
        SELECT
            c.oid,
            trim(lower(n.nspname)) AS schema,
            trim(lower(c.relname)) AS view,
            regexp_split_to_table(regexp_replace(trim(c.relacl::varchar), '[\{\}]', '', 'igm'),',','im') AS relacl
        FROM pg_class c
        JOIN pg_namespace n ON
            n.oid = c.relnamespace AND
            n.nspname != ALL(%s)
        WHERE c.relkind = 'v'
        ORDER BY 2,3
    ) q
    WHERE COALESCE(TRIM(q.relacl), '') != ''
"""


class ViewGrant():

    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        data = re.split('[\=\/]', row.get('relacl'))

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip().lower()
        assert len(self.Schema) > 0

        self.View = row.get('view') or ''
        self.View = self.View.strip().lower()
        assert len(self.View) > 0

        self.FullView = '%s.%s' % (self.Schema, self.View)

        self.Grantee = data[0].strip()
        self.ActionsFirst = data[1].strip()
        self.Grantor = data[2].strip()

        if self.Grantee == '':
            self.Grantee = 'public'

        self.FullName = '%s.%s.%s' % (self.Schema, self.View, self.Grantee)

        self.Actions = []

        if self.ActionsFirst == 'arwdDxt':
            self.Actions = ['ALL']
        elif self.ActionsFirst == 'arwd':
            self.Actions = ['ALL']
        elif self.ActionsFirst == 'U':
            self.Actions = ['USAGE']
        else:
            if self.ActionsFirst.find('r') >= 0:
                self.Actions.append('SELECT')
            if self.ActionsFirst.find('a') >= 0:
                self.Actions.append('INSERT')
            if self.ActionsFirst.find('w') >= 0:
                self.Actions.append('UPDATE')
            if self.ActionsFirst.find('d') >= 0:
                self.Actions.append('DELETE')
            if self.ActionsFirst.find('D') >= 0:
                self.Actions.append('TRUNCATE')
            if self.ActionsFirst.find('x') >= 0:
                self.Actions.append('REFERENCES')
            if self.ActionsFirst.find('t') >= 0:
                self.Actions.append('TRIGGER')

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        return 'GRANT %s ON TABLE %s.%s TO %s;' % (', '.join(self.Actions), self.Schema, self.View, self.Grantee)

    def QueryRemove(self):
        return 'REVOKE ALL ON TABLE %s.%s FROM %s;' % (self.Schema, self.View, self.Grantee)
