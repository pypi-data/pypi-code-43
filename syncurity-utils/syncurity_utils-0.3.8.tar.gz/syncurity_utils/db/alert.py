
from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.dialects.postgresql import JSONB

from syncurity_utils.db.db import Base


class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, Sequence('alert_id_seq'), primary_key=True)
    payload = Column(String)
    alert_timestamp = Column(Integer)
    sensor_ref_name = Column(String)
    irflow_alert_id = Column(Integer)
    integration_id = Column(Integer)
    tenant_name = Column(String)
    alert_type_id = Column(Integer)
    ttl_seconds = Column(Integer)
    inserted_timestamp = Column(Integer)
    parent_alert_id = Column(Integer)

    def __init__(self, payload, alert_timestamp, sensor_ref_name, irflow_alert_id, integration_id, tenant_name,
                 alert_type_id, ttl_seconds, inserted_timestamp, parent_alert_id):
        self.payload = payload
        self.alert_timestamp = alert_timestamp
        self.sensor_ref_name = sensor_ref_name
        self.irflow_alert_id = irflow_alert_id
        self.integration_id = integration_id
        self.tenant_id = tenant_id
        self.alert_type_id = alert_type_id
        self.ttl_seconds = ttl_seconds
        self.inserted_timestamp = inserted_timestamp
        self.parent_alert_id = parent_alert_id

    def __repr__(self):
        return "<Alert(Id=%s, payload='%s', " \
               "alert_timestamp='%s', " \
               "irflow_alert_id='%s', " \
               "integration_id='%s', " \
               "tenant_name='%s', " \
               "sensor_ref_name='%s', " \
               "alert_type_id='%s'" \
               "ttl_seconds='%s'" \
               "inserted_timestamp='%s'" \
               "parent_alert_id='%s'" \
               ")>" \
               % (self.id, self.payload, self.alert_timestamp,
                  self.irflow_alert_id, self.integration_id, self.tenant_name, self.sensor_ref_name,
                  self.alert_type_id,self.ttl_seconds, self.inserted_timestamp, self.parent_alert_id)
