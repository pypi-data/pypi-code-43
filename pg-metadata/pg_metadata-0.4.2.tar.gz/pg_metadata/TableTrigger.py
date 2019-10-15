#!/usr/bin/python
# -*- coding: utf-8 -*-

QUERY_TABLE_TRIGGER = """
    select
        tr.oid,
        trim(lower(n.nspname)) as schema,
        trim(lower(t.relname)) as table,
        trim(lower(tr.tgname)) as name,
        tr.tgenabled = 'D' as is_disabled,
        pg_get_triggerdef(tr.oid) as definition
    FROM pg_trigger tr
    join pg_class t on
        t.oid = tr.tgrelid
    join pg_namespace n on
        n.oid = t.relnamespace AND
        n.nspname != ALL(%s)
    where not tr.tgisinternal
    order by 2,3
"""

class TableTrigger():
    def __init__(self, row={}):
        assert row is not None
        assert isinstance(row, dict)
        assert len(row.keys()) > 0

        self.Oid = row.get('oid')
        assert self.Oid is not None and self.Oid > 0

        self.Schema = row.get('schema') or ''
        self.Schema = self.Schema.strip().lower()
        assert len(self.Schema) > 0

        self.Table = row.get('table') or ''
        self.Table = self.Table.strip().lower()
        assert len(self.Table) > 0

        self.FullTable = '%s.%s' % (self.Schema, self.Table)

        self.Name = row.get('name') or ''
        self.Name = self.Name.strip().lower()
        assert len(self.Name) > 0

        self.FullName = '%s.%s' % (self.Schema, self.Name)

        self.IsDisabled = row.get('is_disabled') or False

        self.Definition = row.get('definition') or ''
        assert len(self.Definition) > 0

        self.Definition = self.Definition.replace(' BEFORE', '\n  BEFORE')
        self.Definition = self.Definition.replace(' AFTER', '\n  AFTER')
        self.Definition = self.Definition.replace(' ON', '\n  ON')
        self.Definition = self.Definition.replace(' FOR', '\n  FOR')
        self.Definition = self.Definition.replace(' EXECUTE', '\n  EXECUTE')

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        result = self.Definition + ';'
        if self.IsDisabled:
            result = result + '\nALTER TABLE %s.%s DISABLE TRIGGER %s;' % (self.Schema, self.Table, self.Name)
        return result

    def QueryRemove(self):
        return 'DROP TRIGGER %s on %s.%s;' % (self.Name, self.Schema, self.Table)
