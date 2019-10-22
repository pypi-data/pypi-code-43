
from sqlalchemy import Column, Integer, Sequence, String
from syncurity_utils.db.db import Base


class AlertType(Base):
    __tablename__ = 'alert_type'

    id = Column(Integer, Sequence('alert_typ_id_seq'), primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<AlertType(id='%s', name='%s')>" % (self.id, self.name)
