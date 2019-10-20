from __future__ import absolute_import
import logging

from apache_beam import PTransform, Create, ParDo, DoFn
from apache_beam.io import iobase
from paralelocs_beam.io.dbconnection import DBHandle


__all__=['ReadFromRelationalDB']


class ReadFromRelationalDB(PTransform):

    def __init__(self, db_config, tablename, filters = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_info = dict(
                    db_config = db_config,
                    tablename = tablename,
                    filters = filters
                    )

    def expand(self, pcoll):
        return (pcoll 
                        | Create([self.db_info])
                        | ParDo(_ReadFromRelationalDB()))

class _ReadFromRelationalDB(DoFn):

    def process(self, pcollection):
        data = dict(pcollection)
        db_config = data.pop('db_config')
        tablename = data.pop('tablename')
        filters = data.pop('filters')
        db = DBHandle(tablename, db_config, filters)
        rows = db.read()
        for row in rows:
            yield row






