from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)
from datetime import datetime

from ...database import Base


class CompanySECModel(Base):
    __tablename__ = 'companies_sec'

    id = Column(Integer, primary_key=True)
    cik_str = Column(String(128), nullable=False)
    ticker = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (UniqueConstraint('cik_str', 'ticker'),)
