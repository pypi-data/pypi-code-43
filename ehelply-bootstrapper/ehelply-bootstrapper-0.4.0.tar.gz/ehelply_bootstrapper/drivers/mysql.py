from ehelply_bootstrapper.drivers.driver import Driver
from ehelply_bootstrapper.utils.connection_details import ConnectionDetails
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response


class Mysql(Driver):
    def __init__(self, connection_details: ConnectionDetails = None, dev_mode: bool = False, verbose: bool = False):
        super().__init__(connection_details, dev_mode, verbose)
        self.Base = None
        self.SessionLocal = None

    def setup(self):
        from ehelply_bootstrapper.utils.state import State
        engine = create_engine(
            self.make_connection_string(
                "mysql",
                State.config.bootstrap.mysql.host,
                State.config.bootstrap.mysql.port,
                State.config.bootstrap.mysql.database,
                State.config.bootstrap.mysql.username,
                State.config.bootstrap.mysql.password
            ),
            pool_pre_ping=True
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        self.Base = declarative_base()

    def make_connection_string(self, driver, host, port, name, username, password):
        return driver + '+pymysql://' + username + ':' + password + '@' + host + ':' + port + '/' + name

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
