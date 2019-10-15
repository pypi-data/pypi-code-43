#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from pg_metadata._System import SEP

QUERY_TABLE_COLUMN = """
    select
        trim(lower(n.nspname)) as schema,
        trim(lower(c.relname)) as table,
        trim(lower(a.attname)) as name,
        trim(lower(format_type(a.atttypid, a.atttypmod))) as type,
        a.attnotnull as not_null,
        ad.adsrc as default_value,
        trim(d.description) as comment,
        a.attnum as order_num,
        max(a.attnum) over (partition by a.attrelid) as max_order_num
    from pg_attribute a
    join pg_class c on
        c.oid = a.attrelid and
        c.relkind in ('r','p')
    join pg_namespace n on
        n.oid = c.relnamespace and
        n.nspname != ALL(%s)
    left join pg_attrdef ad on
        a.atthasdef and
        ad.adrelid = a.attrelid and
        ad.adnum = a.attnum
    left join pg_description d on
        d.objoid = a.attrelid and
        d.objsubid = a.attnum
    where
        a.attnum > 0 and
        not a.attisdropped
    order by 1,2,8
"""

class TableColumn():
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

        self.Name = row.get('name') or ''
        self.Name = self.Name.strip().lower()
        assert len(self.Name) > 0

        self.FullName = '%s.%s.%s' % (self.Schema, self.Table, self.Name)

        self.Type = row.get('type') or ''
        assert len(self.Type) > 0

        self.NotNull = row.get('not_null') or False

        self.DefaultValue = row.get('default_value') or ''
        self.DefaultValue = self.DefaultValue.strip()

        self.OrderNum = row.get('order_num')
        assert self.OrderNum is not None and self.OrderNum > 0

        self.OrderNumLast = row.get("max_order_num")
        assert self.OrderNumLast is not None and self.OrderNumLast > 0

        self.Comment = row.get('comment')
        if self.Comment is not None:
            self.Comment = re.sub("[\n\r]{1,}", SEP, self.Comment, re.MULTILINE | re.IGNORECASE)

        self.IsLast = (self.OrderNum == self.OrderNumLast)

    def __str__(self):
        return self.FullName

    def QueryAdd(self):
        result = 'ALTER TABLE %s.%s ADD COLUMN %s %s%s%s;' % (
            self.Schema,
            self.Table,
            self.Name,
            self.Type,
            '' if not self.NotNull else ' NOT NULL',
            '' if len(self.DefaultValue) <= 0 else ' DEFAULT ' + self.DefaultValue
        )

        if self.Comment is not None and self.Comment.strip() != '':
            result = result + "\nCOMMENT ON COLUMN %s.%s.%s IS '%s';" % (
                self.Schema, self.Table, self.Name, self.Comment)

        return result

    def QueryNotNull(self):
        if self.NotNull:
            return 'ALTER TABLE %s.%s ALTER COLUMN %s SET NOT NULL;' % (self.Schema, self.Table, self.Name)
        else:
            return 'ALTER TABLE %s.%s ALTER COLUMN %s DROP NOT NULL;' % (self.Schema, self.Table, self.Name)

    def QueryDefault(self):
        if self.DefaultValue is None or self.DefaultValue.strip() == '':
            return 'ALTER TABLE %s.%s ALTER COLUMN %s DROP DEFAULT;' % (self.Schema, self.Table, self.Name)
        else:
            return 'ALTER TABLE %s.%s ALTER COLUMN %s SET DEFAULT %s;' % (self.Schema, self.Table, self.Name, self.DefaultValue)

    def QueryRemove(self):
        return 'ALTER TABLE %s.%s DROP COLUMN IF EXISTS %s;' % (self.Schema, self.Table, self.Name)

    def QueryComment(self):
        if self.Comment is not None and self.Comment.strip() != '':
            return "COMMENT ON COLUMN %s.%s.%s IS '%s';" % (self.Schema, self.Table, self.Name, self.Comment)
        return None

    def QueryRaw(self, add_comma=False, add_comment=False):
        if not add_comma:
            add_comma = not self.IsLast

        return '  %s %s%s%s%s%s' % (
            self.Name,
            self.Type,
            '' if not self.NotNull else ' NOT NULL',
            '' if len(self.DefaultValue) <= 0 else ' DEFAULT ' + self.DefaultValue,
            "" if not add_comma else ",",
            "" if not add_comment or self.Comment is None else " -- %s" % (self.Comment.replace(SEP, " "))
        )
