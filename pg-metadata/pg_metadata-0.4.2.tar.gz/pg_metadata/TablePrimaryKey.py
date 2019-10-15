#!/usr/bin/python
# -*- coding: utf-8 -*-

QUERY_TABLE_PRIMARY_KEY = """
    select
        c.oid as oid,
        trim(lower(n.nspname)) as schema,
        trim(lower(t.relname)) as table,
        trim(lower(c.conname)) as name,
        trim(lower(c.contype)) as type,
        pg_get_constraintdef(c.oid) as definition,
        trim(lower(c.confupdtype)) as update_type,
        trim(lower(c.confdeltype)) as delete_type,
        trim(lower(c.confmatchtype)) as match_type,
        c.condeferrable as is_deferrable,
        c.condeferred as is_deferred
    from pg_constraint c
    join pg_namespace n on
        n.oid = c.connamespace AND
        n.nspname != ALL(%s)
    join pg_class t on
        t.oid = c.conrelid
    where
        trim(lower(c.contype)) = 'p' and
        c.conislocal
    order by 1,2,3
"""

class TablePrimaryKey():
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

        self.FullName = '%s.%s.%s' % (self.Schema, self.Table, self.Name)

        self.Type = row.get('type') or ''
        self.Type = self.Type.strip().lower()
        assert len(self.Type) > 0

        if self.Type == 'p':
            self.OrderNum = 1
        elif self.Type == 'u':
            self.OrderNum = 2
        elif self.Type == 'c':
            self.OrderNum = 3
        elif self.Type == 'f':
            self.OrderNum = 4
        else:
            self.OrderNum = 5

        self.Definition = row.get('definition') or ''
        assert len(self.Definition) > 0

        self.UpdateType = row.get('update_type') or ''
        self.UpdateType = self.UpdateType.strip().lower()
        # assert len(self.UpdateType) > 0

        if self.UpdateType == 'a':
            self.UpdateAction = 'ON UPDATE NO ACTION'
        elif self.UpdateType == 'r':
            self.UpdateAction = 'ON UPDATE RESTRICT'
        elif self.UpdateType == 'c':
            self.UpdateAction = 'ON UPDATE CASCADE'
        elif self.UpdateType == 'n':
            self.UpdateAction = 'ON UPDATE SET NULL'
        elif self.UpdateType == 'd':
            self.UpdateAction = 'ON UPDATE SET DEFAULT'
        else:
            self.UpdateAction = ''

        self.DeleteType = row.get('delete_type') or ''
        self.DeleteType = self.DeleteType.strip().lower()
        # assert len(self.DeleteType) > 0

        if self.DeleteType == 'a':
            self.DeleteAction = 'ON DELETE NO ACTION'
        elif self.DeleteType == 'r':
            self.DeleteAction = 'ON DELETE RESTRICT'
        elif self.DeleteType == 'c':
            self.DeleteAction = 'ON DELETE CASCADE'
        elif self.DeleteType == 'n':
            self.DeleteAction = 'ON DELETE SET NULL'
        elif self.DeleteType == 'd':
            self.DeleteAction = 'ON DELETE SET DEFAULT'
        else:
            self.DeleteAction = ''

        self.MatchType = row.get('match_type') or ''
        self.MatchType = self.MatchType.strip().lower()
        # assert len(self.MatchType) > 0

        if self.MatchType == 'f':
            self.MatchAction = 'MATCH FULL'
        elif self.MatchType == 'p':
            self.MatchAction = 'MATCH PARTIAL'
        elif self.MatchType == 'u':
            self.MatchAction = 'MATCH SIMPLE'
        elif self.MatchType == 's':
            self.MatchAction = 'MATCH SIMPLE'
        else:
            self.MatchAction = ''

        self.IsDeferrable = row.get('is_deferrable') or False
        self.IsDeferred = row.get('is_deferred') or False

        if self.IsDeferrable:
            if self.IsDeferred:
                self.DeferrableType = 'DEFERRABLE INITIALLY DEFERRED'
            else:
                self.DeferrableType = 'DEFERRABLE INITIALLY IMMEDIATE'
        else:
            self.DeferrableType = 'NOT DEFERRABLE'

        self.IsForeignKey = self.Definition.find('FOREIGN KEY') > -1

    def __str__(self):
        return self.FullName

    def QueryRaw(self):
        return "CONSTRAINT %s %s" % (self.Name, self.Definition)

    def QueryAdd(self):
        return "ALTER TABLE %s.%s ADD %s;" % (self.Schema, self.Table, self.QueryRaw())

    def QueryRemove(self):
        return 'ALTER TABLE %s.%s DROP CONSTRAINT %s;' % (self.Schema, self.Table, self.Name)
