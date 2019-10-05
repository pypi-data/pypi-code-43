sql = '''SELECT Symbol,Period,OpenVal,CloseVal,High,Low,Volume,Time FROM data5 order by DateCreated'''
import pandas as pd
import hashlib
from core_framework.db_engine import DbEngine

DbEngine.db_type = 'ms'


class Analyze(DbEngine):
    def __init__(self):

        DbEngine.__init__(self)

    def get_data(self):
        self.connect(3)

        # last_date = self.proc('last_data5', response=True)[0][0]
        # print(last_date.strftime('%Y.%m.%d %H:%M'))

        # data = self.select('data5', sql=sql)
        # print(data)

        data = self.select('data5', sql=sql)
        data2 = {}
        for row in data:
            col_rep = {'openval': 'open', 'closeval': 'close'}
            for k, v in row.items():
                if col_rep.get(k) is not None:
                    row.update({col_rep.get(k): v})
                    row.pop(k)

            sha = hashlib.sha3_256(str(row).encode()).hexdigest()
            row.update({'sha': sha})
            # self.merge('period5', {0: row}, {'sha': sha}, update=False)
            print(row)
            data2.update({len(data2): row})
        print("insert period5")
        self.insert('period5', data2)


        # df = pd.DataFrame.from_records(data)
        #
        # df['ma52'] = df['closeval'].rolling(5).mean()
        # df['closeval2'] = df['closeval']
        # print(df)


if __name__ == '__main__':
    api = Analyze()
    api.get_data()
