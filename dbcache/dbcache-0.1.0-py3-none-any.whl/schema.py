from pathlib import Path

from sqlhelp import sqlfile


SQLFILE = Path(__file__).parent / 'schema.sql'


def init(engine, ns='cache', drop=False):
    if drop:
        with engine.begin() as cn:
            cn.execute(
                # hope the operator doesn't do something silly
                f'drop schema if exists "{ns}" cascade'
            )

    with engine.begin() as cn:
        cn.execute(sqlfile(SQLFILE, ns=ns))
