import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from datamodels import Model
from sqly import SQL, Query, Dialects
from sqly.lib import run

logger = logging.getLogger(__name__)

@dataclass
class Job(Model):
    TABLE = 'qy_jobs'
    PK = ['id']

    qname: str = field()
    id: int = field(default=None)
    retries: int = field(default=3)
    queued: datetime = field(default=None)
    scheduled: datetime = field(default=None)
    data: dict = field(default_factory=dict)

    class CONVERTERS:
        def data(value):
            if isinstance(value, str):
                return json.loads(value)
            else: 
                return value


@dataclass
class Queue(Model):
    qname: str
    dialect: Dialects

    def __post_init__(self):
        logger.info('Queue initialized: %r' % self)

    def put(self, data, retries=3, scheduled=None):
        query = SQL(self.dialect).query(
            """
            INSERT INTO qy_jobs ({fields}) values ({params})
            RETURNING *
            """
        )
        job = Job(qname=self.qname, data=data, retries=retries, scheduled=scheduled)
        return query.render(job.dict(nulls=False))

    def get(self):
        query = SQL(self.dialect).query(
            """
            UPDATE qy_jobs q1 SET retries = retries - 1
            WHERE q1.id = ( 
                SELECT q2.id FROM qy_jobs q2 
                WHERE q2.qname=:qname
                AND q2.retries > 0
                AND q2.scheduled <= now()
                ORDER BY q2.queued 
                FOR UPDATE SKIP LOCKED LIMIT 1 
            )
            RETURNING q1.*;
            """.rstrip()
        )
        return query.render({'qname': self.qname})

    def delete(self, job):
        query = SQL(self.dialect).query(
            """
            DELETE FROM qy_jobs WHERE id=:id
            """.rstrip(),
            dialect=self.dialect,
        )
        return query.render({'id': job.id})
