
from healer.persist.arkon import *


class SomeData(ServerModel):

    class Meta:
        table_name = 'some_data'


def xxx_test_database():
    print()

    CONFIG['application']['user_home'] = '/tmp/healer_tester'

    database = ServerSupport.ensure_database()
    print(f"get_tables: {database.get_tables()}")

    some = SomeData()
    some.save()
    print(f"some: {some}")

    ServerSupport.desure_database()
    print(f"get_tables: {database.get_tables()}")
