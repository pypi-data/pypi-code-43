import unittest
import head_controller.Camera as Camera
import head_controller.db as db
import head_controller.Features as Features
import pandas as pd
import pymysql

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
