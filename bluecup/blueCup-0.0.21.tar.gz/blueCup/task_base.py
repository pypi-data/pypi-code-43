from typing import Dict, Any

from celery import Task
from jsonschema import validate

CODE_INCOMING_DATA_ERROR = 'IncomingDataError'

TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "is_succeed": {"type": "boolean"},
        "msg": {"type": "string"},
        "msg_code": {"type": "string"},
        "data": {},
    },
}


def check_schema(ins: Any) -> None:
    validate(instance=ins, schema=TASK_SCHEMA)


# class FlaskSqlalchemyContext:
#     # debug: from flask import Flask, even import is put here, must be installed first.
#     from flask import Flask
#     from flask_sqlalchemy import SQLAlchemy
#     app_flask: ClassVar[Flask] = Flask(__name__)
#
#     def __new__(cls, url: str, db: SQLAlchemy) -> None:
#         cls.app_flask.config['SQLALCHEMY_DATABASE_URI'] = url
#         db.init_app(cls.app_flask)
#         return cls.app_flask.app_context()


class TaskBase(Task):
    # from flask import Flask
    # from flask_sqlalchemy import SQLAlchemy
    # app_flask: ClassVar[Flask] = Flask(__name__)

    # @classmethod
    # def bind_db(cls, url: str, db: SQLAlchemy) -> None:
    #     """
    #     the method should be called early.
    #     :param url:
    #     :param db:
    #     :return:
    #     """
    #     cls.app_flask.config['SQLALCHEMY_DATABASE_URI'] = url
    #     db.init_app(cls.app_flask)

    @classmethod
    def task_result(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        copied = data.copy()
        copied.setdefault('data', '')
        if copied.get('is_succeed'):
            copied.setdefault('msg', '')
            copied.setdefault('msg_code', '')
        validate(instance=copied, schema=TASK_SCHEMA)
        return data
