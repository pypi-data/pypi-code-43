import pymysql


class IndexTrackConfig:
    def __init__(self, exchange, index_code: str, index_name: str = '', etf_code='', etf_name='',
                 track_days: int = 7200):
        self.exchange = exchange
        self.index_code = index_code
        self.index_name = index_name
        self.etf_code = etf_code
        self.etf_name = etf_name
        self.track_days = track_days

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return "IndexConfig(exchange={}, index_code={}, index_name={}," \
               "track_days={})" \
            .format(self.exchange, self.index_code, self.index_name, self.track_days)

    @staticmethod
    def get_index_config(monitor=False):
        configs = []

        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        cursor = conn.cursor()
        if monitor:
            sql = "select exchange, index_code, index_name, etf_code, etf_name, " \
                  " track_days from index_track_list where monitor=1 "
        else:
            sql = "select exchange, index_code, index_name, track_days from index_track_list"
        cursor.execute(sql)
        conn.commit()

        for item in cursor.fetchall():
            exchange = item[0]
            index_code = item[1]
            index_name = item[2]
            etf_code = item[3]
            etf_name = item[4]
            track_days = item[5]

            configs.append(IndexTrackConfig(exchange, index_code, index_name, etf_code, etf_name, track_days))

        return configs


if __name__ == '__main__':
    print(IndexTrackConfig.get_index_config())
