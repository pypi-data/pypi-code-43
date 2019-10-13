from ehelply_bootstrapper.drivers.driver import Driver
from ehelply_bootstrapper.utils.connection_details import ConnectionDetails
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from pydantic import BaseModel


class MySQLCredentials(BaseModel):
    host: str
    port: int = 3306
    database: str
    username: str
    password: str


class Mysql(Driver):
    def __init__(self, credentials: MySQLCredentials, dev_mode: bool = False, verbose: bool = False):
        super().__init__(dev_mode=dev_mode, verbose=verbose)
        self.Base = None
        self.SessionLocal = None
        self.credentials: MySQLCredentials = credentials

    def setup(self):
        engine = create_engine(
            self.make_connection_string(
                "mysql",
                self.credentials.host,
                self.credentials.port,
                self.credentials.database,
                self.credentials.username,
                self.credentials.password
            ),
            pool_pre_ping=True
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        self.Base = declarative_base()

    def make_connection_string(self, driver: str, host: str, port: int, database_name: str, username: str,
                               password: str):
        return driver + '+pymysql://' + username + ':' + password + '@' + host + ':' + str(port) + '/' + database_name

    def inject_fastapi_middleware(self, app: FastAPI):
        @app.middleware("http")
        async def db_session_middleware(request: Request, call_next):
            response = Response("Internal server error", status_code=500)
            try:
                request.state.db = self.SessionLocal()
                response = await call_next(request)
            finally:
                request.state.db.close()
            return response


# Dependency
def get_db(request: Request):
    return request.state.db
