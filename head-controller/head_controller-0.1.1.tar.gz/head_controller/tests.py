import unittest
import Camera,db,Features
import pandas as pd
import pymysql
import db


class TestStringMethods(unittest.TestCase):

    def test_read_write(self):
        df = pd.DataFrame({'name' : ['User 1', 'User 2', 'User 3']})
        db.send_df_to_table(df,'test',operation='replace')
        con = db.get_connection()
        resp = con.cursor().execute("SELECT * FROM test").fetchall()
        con.close()
        self.assertEqual(len(resp),len([(0, 'User 1'), (1, 'User 2'), (2, 'User 3')]))


if __name__ == '__main__':
    unittest.main()
