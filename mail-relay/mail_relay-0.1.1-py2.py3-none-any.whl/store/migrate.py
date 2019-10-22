from pvHelpers.store import GetDBSession


def migrate(wd):
    with GetDBSession(wd) as s:
        with s.begin():
            s.execute('DROP TABLE IF EXISTS Store')
            s.execute(
                '''
                CREATE TABLE Store
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bucket TEXT NOT NULL COLLATE NOCASE,
                    bucket_version INTEGER NOT NULL,
                    key TEXT NOT NULL COLLATE NOCASE,
                    value BLOB NOT NULL,
                    UNIQUE (bucket, key))
                '''
            )
