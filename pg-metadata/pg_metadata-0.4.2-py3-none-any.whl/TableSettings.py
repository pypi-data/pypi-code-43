#!/usr/bin/python
# -*- coding: utf-8 -*-

QUERY_TABLE_SETTINGS = """
    select
        trim(lower(n.nspname)) as schema,
        trim(lower(c.relname)) as table,
        trim(lower(unnest(c.reloptions))) as setting
    from pg_class c
    join pg_namespace n on
        n.oid = c.relnamespace AND
        n.nspname != ALL(%s)
    where c.reloptions is not null
    order by 1,2,3
"""

class TableSettings():
    def __init__(self, row = {}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip().lower()
        assert len(self.Schema) > 0

        self.Table = row.get('table') or ''
        self.Table = self.Table.strip().lower()
        assert len(self.Table) > 0

        self.FullTable = '%s.%s' % (self.Schema, self.Table)

        self.Setting = row.get('setting') or ''
        self.Setting = self.Setting.strip().lower()
        assert len(self.Setting) > 0
        assert self.Setting.find('=') >= 0

        self.FieldName = self.Setting.split('=')[0].strip()
        self.FieldValue = self.Setting.split('=')[1].strip()

        self.FullName = '%s.%s.%s' % (self.Schema, self.Table, self.FieldName)

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        return """ALTER TABLE %s.%s SET (%s = %s);""" % (self.Schema, self.Table, self.FieldName, self.FieldValue)

    def QueryRemove(self):
        return """ALTER TABLE %s.%s RESET (%s);""" % (self.Schema, self.Table, self.FieldName)
