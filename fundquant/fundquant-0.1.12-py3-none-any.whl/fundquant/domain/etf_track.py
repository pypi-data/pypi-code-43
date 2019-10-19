import pymysql


class EtfTrackConfig:
    def __init__(self, etf_code: str, etf_name, index_code: str, index_name: str = '',
                 track_days: int = 7200,
                 low_percent: float = 0.25, high_percent: float = 0.75,
                 std_low_weight: float = 2, std_high_weight: float = 2):
        self.etf_code = etf_code
        self.etf_name = etf_name
        self.index_code = index_code
        self.index_name = index_name
        self.track_days = track_days
        self.low_percent = low_percent
        self.high_percent = high_percent
        self.std_low_weight = std_low_weight
        self.std_high_weight = std_high_weight

    @staticmethod
    def get_etf_config():
        configs = []

        conn = pymysql.connect(user='root', password='', database='quant', charset='utf8')
        cursor = conn.cursor()
        sql = "select etf_code, etf_name, index_id, index_name from jsl_etf_list where monitor = 1 "
        cursor.execute(sql)
        conn.commit()

        for item in cursor.fetchall():
            etf_code = item[0]
            etf_name = item[1]
            index_id = item[2]
            index_name = item[3]

            configs.append(EtfTrackConfig(etf_code, etf_name, index_id, index_name))

        return configs


if __name__ == '__main__':
    print(EtfTrackConfig.get_index_config())
