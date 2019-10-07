

import apsw

conn = apsw.Connection(':memory:')

cursor = conn.cursor()

cursor.execute('CREATE VIRTUAL TABLE testing USING fts5(data);')

cursor.execute('SELECT json(?)', (1337,)).fetchone()

