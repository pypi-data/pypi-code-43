class MySQLDBAL:
    def __init__(self, conn, dbname=None):
        self.conn = conn
        self.dbname = dbname

    def get_tables(self):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute('show tables')

        return cursor

    def get_columns(self, name, db):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute("""
            SELECT 
                COLUMN_NAME as name, 
                DATA_TYPE as type, 
                CHARACTER_MAXIMUM_LENGTH as length
            FROM INFORMATION_SCHEMA.COLUMNS  
            WHERE 
                table_name = %s AND 
                TABLE_SCHEMA = %s
        """, (name, db))

        return cursor

    def get_create_statement(self, name):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute('show create table {}'.format(name))

        return cursor
