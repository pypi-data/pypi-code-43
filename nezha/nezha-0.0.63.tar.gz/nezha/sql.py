from decimal import Decimal
from typing import Dict, Any, List, Tuple, Union, NamedTuple, Optional

import pymysql
from nezha.udict import ImmutableDict


class PyMysql:

    def __init__(self, host: str = '',
                 user: str = '',
                 password: str = '',
                 database: str = '',
                 port: int = 3306, ):
        self.db_info: Dict[str, Union[str, int]] = ImmutableDict(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            charset='utf8'
        )

    def fetchall(self,
                 sql: str,
                 params: Union[List, Tuple, Dict[str, Any], None] = None,
                 namedtupleObj: Optional[NamedTuple] = None) -> Union[Tuple[NamedTuple, ...], Tuple[Dict, ...]]:
        """

        :param db_info:
        :param sql:
        :param params: sql params
        :param namedtupleObj: use namedtuple transfer result
        :return:
        """
        connection = pymysql.connect(**self.db_info)
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                all_fetched = cursor.fetchall()
                if namedtupleObj:
                    return tuple(namedtupleObj(**i) for i in all_fetched)  # type: ignore
                returned = []
                for one_fetched in all_fetched:
                    returned.append({k: float(v) if isinstance(v, Decimal) else v for k, v in one_fetched.items()})
                return tuple(returned)
        finally:
            cursor.close()
            connection.close()

    def fetchone(self,
                 sql: str,
                 params: Union[List, Tuple, Dict[str, Any], None] = None,
                 namedtupleObj: Optional[NamedTuple] = None) -> Union[NamedTuple, Dict]:
        """

        :param view: string
        :return:
        """
        connection = pymysql.connect(**self.db_info)
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                one_fetched = cursor.fetchone()
                if namedtupleObj:
                    return namedtupleObj(one_fetched)  # type: ignore
                return {k: float(v) if isinstance(v, Decimal) else v for k, v in one_fetched.items()}
        finally:
            cursor.close()
            connection.close()

    def execute(self,
                sql: str,
                params: Union[List, Tuple, Dict[str, Any], None] = None) -> None:
        """

        :param view: string
        :return:
        """
        connection = pymysql.connect(**self.db_info)
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
        finally:
            cursor.close()
            connection.close()


if __name__ == '__main__':
    from gitignore import DEV_DB

    db = PyMysql(**DEV_DB)
    s = db.fetchone('select * from company limit 1')
    print(s)
