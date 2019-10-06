import click
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

Base = declarative_base()


def get_db_connection(config):
    """Configures db connection with config object."""  # TODO: URL-Parsing for special characters.
    if config['DB']['driver'].get() is None:
        db_connector = f"{config['DB']['dialect'].get(str)}"
    else:
        db_connector = f"{config['DB']['dialect'].get(str)}+{config['DB']['driver'].get(str)}"

    db = f"{db_connector}://{config['DB']['username'].get(str)}:{quote_plus(config['DB']['password'].get(str))}@" \
         f"{config['DB']['host'].get(str)}:{config['DB']['port'].get(int)}/{config['DB']['database'].get(str)}"
    engine = create_engine(db)
    try:
        Base.metadata.create_all(bind=engine)
        session = sessionmaker(bind=engine)
    except OperationalError as e:
        click.echo(f"Could not connect to '{db}'.\n"
                   f"Details on error:\n"
                   f"{e}")
        raise click.Abort

    connection = session()
    return connection


def try_commit(connection):
    try:
        connection.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort


class Domains(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), nullable=False, unique=True)


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True)
    domain = Column(String(255), ForeignKey('domains.domain'), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    quota = Column(Integer, default=0)
    enabled = Column(Boolean, default=False)
    sendonly = Column(Boolean, default=False)


class Aliases(Base):
    __tablename__ = 'aliases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_username = Column(String(64), nullable=False, unique=True)
    source_domain = Column(String(255), ForeignKey('domains.domain'), nullable=False, unique=True)
    destination_username = Column(String(64), nullable=False, unique=True)
    destination_domain = Column(String(255), nullable=False, unique=True)
    enabled = Column(Boolean, default=False)
