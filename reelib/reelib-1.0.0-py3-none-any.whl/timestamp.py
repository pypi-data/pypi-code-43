import datetime

def get_timestamp():
    '''現在時刻のタイムスタンプを取得'''
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST)

    return now.strftime('%Y%m%d%H%M%S%f')

def conv_time_from_timestamp(timestamp):
    '''タイムスタンプをdatetimeに変換'''
    time = datetime.datetime.strptime(timestamp+'+0900', '%Y%m%d%H%M%S%f%z')

    return time