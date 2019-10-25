#
# Copyright (c) 2010, 2013, 2015, 2016, 2017, 2019
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
from StringIO import StringIO
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from utility import sql_connect
from command import SQLCommand


class UpsertAction(ActionCommand, SQLCommand):
    __domain__ = "action"
    __operation__ = "sql-upsert"
    __aliases__ = ['sqlUpsert', 'sqlUpsertAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):

        db = sql_connect(self._source)
        cursor = db.cursor()

        """prequery support"""
        if self._prequery:
            try:
                cursor.execute(self._prequery)
            except Exception as exc:
                self.log_message(
                    'Exception performing SQL Prequery: {0}'
                    .format(self._prequery, ), category='error',
                )
                raise exc
            else:
                self.log_message(
                    'Performed SQL Prequery: {0}'.format(self._prequery, ),
                    category='info',
                )
        else:
            self.log_message('No prequery to perform.', category='info', )

        summary = StringIO(u'')

        table_name, format_name, format_class = \
            self._read_result_metadata(self.rfile)
        if self._target:
            table_name = self._target
            self.log_message(
                'Upsert target table is "{0}", from action parameter stream'
                .format(table_name, ),
                category='info',
            )
        else:
            self.log_message(
                'Upsert target table is "{0}", from StandardXML stream'
                .format(table_name, ),
                category='info',
            )

        cursor = db.cursor()
        counter = 0
        update_count = 0
        insert_count = 0
        try:
            for keys, fields in self._read_rows(
                self.rfile,
                key_fields=self._keys,
                for_record_type=self._record_type,
            ):
                # Parse row, building keys and fields
                if (len(keys) == 0):
                    raise CoilsException(
                        'No primary keys provided for update of SQL record.'
                    )
                # Perform SELECT based on values of keys
                sql, values = self._create_pk_select_from_keys(
                    connection=db,
                    table=table_name,
                    keys=keys,
                    extra_where=self._where,
                )

                try:
                    cursor.execute(sql, values)
                    count = len(cursor.fetchall())
                except Exception, e:
                    # TODO: Catch the more specific database exception
                    self.log_message(
                        'FAILED SQL: {0} VALUES: {1}'.
                        format(
                            unicode(sql),
                            unicode(values),
                        ),
                        category='error',
                    )
                    raise e
                finally:
                    # cursor.close()
                    pass
                # Perform Upsert
                if (count == 0):
                    # Insert
                    sql, values = self._create_insert_from_fields(
                        connection=db,
                        table=table_name,
                        keys=keys,
                        fields=fields, )
                    insert_count += 1
                elif (count == 1):
                    # Update
                    sql, values = self._create_update_from_fields(
                        connection=db,
                        table=table_name,
                        keys=keys,
                        fields=fields,
                        extra_where=self._where, )
                    update_count += 1
                else:
                    self.log_message(
                        'Primary key search returned more than one tuple.\n '
                        'SQL: {0}\n VALUES: {1}'.
                        format(
                            unicode(sql),
                            unicode(values),
                        ),
                        category='error',
                    )
                    raise CoilsException(
                        'Primary key search returned more than one record!'
                    )

                try:
                    cursor.execute(sql, values)
                except Exception, e:
                    # TODO: Catch the more specific database exception
                    self.log_message(
                        'FAILED SQL: {0} VALUES: {1}'.
                        format(unicode(sql), unicode(values)),
                        category='error')
                    raise e
                finally:
                    # cursor.close()
                    pass
                # The pause
                counter += 1
                if not (counter % 4096):
                    self.gong()

            if (self._commit == 'YES'):
                if cursor:
                    cursor.close()
                    cursor = None
                db.commit()
        finally:
            summary.write(u'{0} records processed.'.format(counter))
            self.log_message(summary.getvalue(), category='error')
            summary = None
            db.close()

    def parse_action_parameters(self):

        """initializes dataSource and preQuery"""
        SQLCommand.parse_action_parameters(self)

        self._commit = self.action_parameters.get('commit', 'YES').upper()

        # tableName, if not specified defaults to value from XML stream
        self._target = self.action_parameters.get('tableName', None)
        if self._target:
            self._target = self.process_label_substitutions(self._target)

        self._where = self.action_parameters.get('where', None)
        if self._where:
            self._where = self.process_label_substitutions(self._where)

        # primaryKeys, added to values from XML stream
        self._keys = self.action_parameters.get('primaryKeys', None)
        if self._keys:
            self._keys = self.process_label_substitutions(self._keys)
        if isinstance(self._keys, basestring):
            self._keys = self._keys.split(',')
        else:
            self._keys = list()

        # dataSource is the only mandatory value
        if self._source is None:
            raise CoilsException('No source defined for selectAction')

    def do_epilogue(self):
        pass
