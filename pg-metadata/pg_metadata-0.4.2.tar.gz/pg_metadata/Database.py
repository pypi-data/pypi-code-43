#!/usr/bin/python
# -*- coding: utf-8 -*-

from pg_metadata._Postgres          import Postgres
from pg_metadata.Table              import Table,           QueryTable
from pg_metadata.TableGrant         import TableGrant,      QUERY_TABLE_GRANT
from pg_metadata.TableColumn        import TableColumn,     QUERY_TABLE_COLUMN
from pg_metadata.TablePrimaryKey    import TablePrimaryKey, QUERY_TABLE_PRIMARY_KEY
from pg_metadata.TableConstraint    import TableConstraint, QUERY_TABLE_CONSTRAINT
from pg_metadata.TableIndex         import TableIndex,      QUERY_TABLE_INDEX
from pg_metadata.TableTrigger       import TableTrigger,    QUERY_TABLE_TRIGGER
from pg_metadata.TableSettings      import TableSettings,   QUERY_TABLE_SETTINGS
from pg_metadata.View               import View,            QUERY_VIEW
from pg_metadata.ViewGrant          import ViewGrant,       QUERY_VIEW_GRANT
from pg_metadata.Sequence           import Sequence,        QUERY_SEQUENCE
from pg_metadata.SequenceGrant      import SequenceGrant,   QUERY_SEQUENCE_GRANT
from pg_metadata.Function           import Function,        QUERY_FUNCTION
from pg_metadata.FunctionGrant      import FunctionGrant,   QUERY_FUNCTION_GRANT
from pg_metadata.ForeignServer      import ForeignServer,   QUERY_FOREIGN_SERVER
from pg_metadata.ForeignTable       import ForeignTable,    QUERY_FOREIGN_TABLE

class Database():
    def __init__(self, connect, exclude_schemas=[]):
        self.PG = Postgres(connect)
        self.ExcludeSchemas = exclude_schemas

        self.Tables = {}
        self.TablesGrants = {}
        self.TablesColumns = {}
        self.TablesPrimaryKeys = {}
        self.TablesConstraints = {}
        self.TablesIndexes = {}
        self.TablesTriggers = {}
        self.TablesSettings = {}

        self.Views = {}
        self.ViewsGrants = {}

        self.Sequences = {}
        self.SequencesGrants = {}

        self.Functions = {}
        self.FunctionsGrants = {}

        self.ForeignServers = {}
        self.ForeignTables = {}

    def __str__(self):
        return str(self.PG)

    def Parse(self):
        self.PG.Connect()

        for row in self.PG.Execute(QUERY_VIEW, [self.ExcludeSchemas]):
            t = View(row)
            self.Views[t.FullName] = t

        for row in self.PG.Execute(QUERY_VIEW_GRANT, [self.ExcludeSchemas]):
            t = ViewGrant(row)
            self.ViewsGrants[t.FullName] = t

        for row in self.PG.Execute(QueryTable(self.PG.Version), [self.ExcludeSchemas]):
            t = Table(row)
            self.Tables[t.FullName] = t

        for row in self.PG.Execute(QUERY_TABLE_GRANT, [self.ExcludeSchemas]):
            t = TableGrant(row)
            self.TablesGrants[t.FullName] = t

        for row in self.PG.Execute(QUERY_TABLE_COLUMN, [self.ExcludeSchemas]):
            t = TableColumn(row)
            self.TablesColumns[t.FullName] = t
            self.Tables[t.FullTable].Columns.append(t)

        for row in self.PG.Execute(QUERY_TABLE_PRIMARY_KEY, [self.ExcludeSchemas]):
            t = TablePrimaryKey(row)
            self.TablesPrimaryKeys[t.FullName] = t
            self.Tables[t.FullTable].Constraints.append(t)

        for row in self.PG.Execute(QUERY_TABLE_CONSTRAINT, [self.ExcludeSchemas]):
            t = TableConstraint(row)
            self.TablesConstraints[t.FullName] = t
            self.Tables[t.FullTable].Constraints.append(t)

        for row in self.PG.Execute(QUERY_TABLE_INDEX, [self.ExcludeSchemas]):
            t = TableIndex(row)
            self.TablesIndexes[t.FullName] = t

            if self.Tables.get(t.FullTable) is not None:
                self.Tables.get(t.FullTable).Indexes.append(t)

            if self.Views.get(t.FullTable) is not None:
                self.Views.get(t.FullTable).Indexes.append(t)

        for row in self.PG.Execute(QUERY_TABLE_TRIGGER, [self.ExcludeSchemas]):
            t = TableTrigger(row)
            self.TablesTriggers[t.FullName] = t
            self.Tables[t.FullTable].Triggers.append(t)

        for row in self.PG.Execute(QUERY_TABLE_SETTINGS, [self.ExcludeSchemas]):
            t = TableSettings(row)
            self.TablesSettings[t.FullName] = t

        for row in self.PG.Execute(QUERY_SEQUENCE, [self.ExcludeSchemas]):
            t = Sequence(row)
            self.Sequences[t.FullName] = t

        for row in self.PG.Execute(QUERY_SEQUENCE_GRANT, [self.ExcludeSchemas]):
            t = SequenceGrant(row)
            self.SequencesGrants[t.FullName] = t

        for row in self.PG.Execute(QUERY_FUNCTION, [self.ExcludeSchemas]):
            t = Function(row)
            self.Functions[t.FullName] = t

        for row in self.PG.Execute(QUERY_FUNCTION_GRANT, [self.ExcludeSchemas]):
            t = FunctionGrant(row)
            self.FunctionsGrants[t.FullName] = t

        for row in self.PG.Execute(QUERY_FOREIGN_SERVER, [self.ExcludeSchemas]):
            t = ForeignServer(row)
            self.ForeignServers[t.Name] = t

        for row in self.PG.Execute(QUERY_FOREIGN_TABLE, [self.ExcludeSchemas]):
            t = ForeignTable(row)
            self.ForeignTables[t.Name] = t

        self.PG.Disconnect()
