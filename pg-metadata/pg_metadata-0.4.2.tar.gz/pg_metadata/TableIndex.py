#!/usr/bin/python
# -*- coding: utf-8 -*-

QUERY_TABLE_INDEX = """
    select
        ic.oid,
        trim(lower(n.nspname)) as schema,
        trim(lower(c.relname)) as table,
        trim(lower(ic.relname)) as name,
        pg_get_indexdef(i.indexrelid, 0, true) as definition
    from pg_index i
    join pg_class c on
        c.oid = i.indrelid
    join pg_namespace n on
        n.oid = c.relnamespace and
        n.nspname != ALL(%s)
    join pg_class ic on
        ic.oid = i.indexrelid
    where
        not i.indisprimary and
        not exists(
            select 1
            from pg_constraint co
            where co.conindid = ic.oid
        )
    order by 1,2,3
"""

class TableIndex():
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

        self.Definition = row.get('definition') or ''
        assert len(self.Definition) > 0

        self.Definition = self.Definition.replace(' ON ', '\n  ON ')
        self.Definition = self.Definition.replace(' USING ', '\n  USING ')
        self.Definition = self.Definition.replace(' (', '\n  (')
        self.Definition = self.Definition + ';'

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        return self.Definition

    def QueryRemove(self):
        return 'DROP INDEX IF EXISTS %s.%s;' % (self.Schema, self.Name)
