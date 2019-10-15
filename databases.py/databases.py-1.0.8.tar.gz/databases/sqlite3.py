# -*- coding: utf-8 -*-

'''
MIT License

Copyright (c) 2019 Caio Alexandre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from .errors import *

import sqlite3
import builtins

class Client:
    '''
    '''
    __slots__ = ('_conn', '_cursor', 'tables',
                 'filename', 'dir')
    __instances__ = []

    def __init__(self, filename: str='data.db'):
        self._conn = sqlite3.connect(filename)
        self._cursor = self._conn.cursor()

        self.tables = []

        self.dir = filename
        self.filename = filename.split('/')[-1]

        for instance in self.__instances__:
            if instance.dir == self.dir:
                self.tables.extend(list(filter(lambda x: x not in self.tables, instance.tables)))

        self.__instances__.append(self)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return f'<Client table_count={len(self.tables)} filename={self.filename!r}>'

    def create_table(self, table_name: str, **columns):
        '''
        '''
        table = Table(self, table_name, **columns)
        self.tables.append(table)

        return table

    def get_table(self, table_name: str):
        '''
        '''
        for instance in Table.__instances__:
            if instance.name == table_name:
                return instance
        else:
            return None

class Column:
    '''
    '''
    __slots__ = ('name', 'type')

    def __init__(self, name: str, type):
        self.name = name
        self.type = type

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Column name={0.name!r} type={0.type.__name__!r}>'.format(self)

class Table:
    '''
    '''
    __slots__ = ('_conn', '_cursor', '_table_name', '_str_columns', '_dict_columns',
                 'columns', 'client')
    __instances__ = []

    __eval_types__ = (list, set, tuple, dict)
    __supported_types__ = {
        int: 'int',
        str: 'text',
        set: 'text',
        list: 'text',
        dict: 'text',
        float: 'real'
    }

    def __init__(self, client: Client, table_name: str, **columns):
        if not all(columns[data_type] in self.__supported_types__ for data_type in columns):
            raise TypeError(f'The column data type must be one of these: {", ".join(map(lambda x: x.__name__, list(self.__supported_types__)))}')

        if type(table_name) != str:
            raise TypeError(f"The database name must be 'str', not {type(table_name).__name__!r}")

        columns['__id__'] = int

        self._conn = client._conn
        self._cursor = client._cursor

        self._table_name = table_name

        self.columns = list(map(lambda x: Column(x, columns[x]), columns))
        self.client = client

        self._str_columns = list(map(lambda x: x.name, self.columns))
        self._dict_columns = dict(map(lambda x: [x.name, x.type], self.columns))

        self.__instances__.append(self)

        self._cursor.execute(f'create table if not exists {table_name} ({", ".join(map(lambda x: f"{x} {self.__supported_types__[columns[x]]}", columns))});')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Table name={0.name!r} columns={0.columns}>'.format(self)

    @property
    def name(self):
        return self._table_name

    @name.setter
    def name(self, table_name: str):
        if type(table_name) != str:
            raise TypeError(f"The database name must be 'str', not {type(table_name).__name__!r}")

        self._cursor.execute(f'alter table {self._table_name} rename to {table_name};')
        self._table_name = table_name

    def all(self):
        '''
        '''
        self._cursor.execute(f'select * from {self.name};')

        items = self._cursor.fetchall()
        rows = []

        for row in items:
            row_dict = {}

            for item in range(len(row)):
                row_dict[self._str_columns[item]] = eval(row[item]) if self._dict_columns[self._str_columns[item]] in self.__eval_types__ else row[item]
            rows.append(row_dict)

        return Row(self, rows)

    def add(self, **values):
        '''
        '''
        if not all(value in self._str_columns for value in values):
            raise ValueError('Incorrect columns') # TODO: Change this error message.

        objects = list(map(lambda x: x.__id__, self.all().objects))
        id = max(objects) if len(objects) else 0

        values['__id__'] = id + 1

        add_values = []
        for value in values:
            item = values[value]
            column_type = self._dict_columns[value]

            if column_type in self.__eval_types__:
                if type(item) == column_type:
                    add_values.append(str(item))
                else:
                    raise TypeError(f"Item: {x}'s type must be {column_type.__name__!r}")
            elif type(item) in [int, str, float]:
                add_values.append(str(item) if column_type == str else item)
            else:
                raise TypeError(f'Item type must be one of these: {", ".join(map(lambda x: x.__name__, list(self.__supported_types__)))}')

        self._cursor.execute(f'insert into {self.name} ({", ".join(values)}) values ({", ".join(["?"] * len(values))})', (*add_values,))
        self._conn.commit()

        return Item(self, **values)

    def delete(self):
        '''
        '''
        table = self.client.get_table(self.name)
        if not table:
            raise TableNotFound(self.name)

        try:
            self._cursor.execute(f'drop table {self.name};')
        except sqlite3.OperationalError:
            raise TableNotFound(self.name)
        else:
            self.client.tables.remove(instance)
            self.__instances__.remove(instance)

class Item:
    '''
    '''
    def __init__(self, table: Table, **values):
        self.table = table
        self.client = table.client

        self._values = values

        self._conn = table._conn
        self._cursor = table._cursor

        type_transform = lambda x: x if type(x) != str else f"""'''{x}'''"""

        for value in values:
            exec(f'self.{value} = {type_transform(values[value])}')

    def __repr__(self):
        return '<Item table={0.table!r} values={0._values}>'.format(self)

    def save(self):
        '''
        '''
        self_dict = self.__dict__
        class_dict = dict(map(lambda x: [x, self_dict[x]], filter(lambda y: y.lower() not in ['table', 'client', '_values', '_conn', '_cursor', '__id__'], self_dict)))

        for value in class_dict:
            item = self_dict[value]
            column_type = self.table._dict_columns[value]

            if type(item) == int and column_type == float:
                class_dict[value] = float(item)
            elif type(item) == float and column_type == int:
                class_dict[value] = int(item)
            elif type(item) in self.table.__eval_types__:
                class_dict[value] = str(item)
            elif type(item) != column_type:
                raise TypeError(f"Item: {x}'s type must be {column_type.__name__!r}")

        self._cursor.execute(f'update {self.table.name} set {", ".join(map(lambda x: f"{x} = ?", class_dict))} where __id__ = ?;', (*class_dict.values(), self_dict['__id__']))
        self._conn.commit()

    def delete(self):
        '''
        '''
        table = self.client.get_table(self.table.name)
        if not table:
            raise TableNotFound(self.table.name)

        self._cursor.execute(f'delete from {self.table.name} where __id__ = ?', (self.__dict__['__id__'],))
        self._conn.commit()

class Row:
    '''
    '''
    __slots__ = ('table', 'objects')

    def __init__(self, table: Table, rows: list):
        self.table = table
        self.objects = list(map(lambda x: Item(table, **x), rows))

    def __repr__(self):
        return f'<Row table={self.table!r} object_count={len(self.objects)}>'

    def __contains__(self, item):
        return item in self.objects

    def __getitem__(self, key):
        return self.objects[key]

    def filter(self, **filters):
        '''
        '''
        columns = list(self.table._str_columns)
        if not all(value in columns for value in filters):
            raise ValueError('Incorrect columns') # TODO: Change this error message.

        objects = self.objects
        for filter in filters:
            objects = list(builtins.filter(lambda x: eval(f'x.{filter}') == filters[filter], objects))

        return objects

    def get_first(self, **filters):
        '''
        '''
        items = self.filter(**filters)
        return items[0] if items else None

    def get_last(self, **filters):
        '''
        '''
        items = self.filter(**filters)
        return items[-1] if items else None

if __name__ == '__main__':
    pass
