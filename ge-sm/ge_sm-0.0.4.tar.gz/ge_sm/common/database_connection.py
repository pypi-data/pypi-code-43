from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

from ge_sm.common.secrets import rs_usr, rs_pwd, rs_dsn

class RedshiftDBConnection:

    """creates a SQLAlchemy engine, metadata and session objects"""

    def __init__(self, usr=rs_usr, pwd=rs_pwd, svr=rs_dsn, schema='chaajaa', connect_args={'sslmode': 'prefer'}):

        self.usr = usr
        self.pwd = pwd
        self.svr = svr
        self.schema = schema
        self.connect_args = connect_args
        self.db_string = f'redshift+psycopg2://{self.usr}:{self.pwd}@{self.svr}:5439'
        if self.connect_args:
            self.engine = create_engine(self.db_string, connect_args=self.connect_args)
        else:
            self.engine = create_engine(self.db_string)
        self.metadata = MetaData(bind=self.engine, schema=self.schema)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()


    def __repr__(self):
        return f'{self.__class__.__name__}(usr="{self.usr}", pwd="{self.pwd}", svr="{self.svr}", ' \
            f'schema="{self.schema}")'

    @staticmethod
    def autoload_tables(table_name: str, metadata, engine, schema: str):
        """
        load metadata from pre-defined DB structure
        Also force id column to be primary key
        :param metadata:
        :param table_name: required; TableName to be defined (must exist in DB)
        :return: metadata table definition
        """
        t = Table(table_name, metadata, autoload=True, autoload_with=engine, schema=schema)
        return t

if __name__ == '__main__':
    conn = RedshiftDBConnection()
    print(conn.__dict__)