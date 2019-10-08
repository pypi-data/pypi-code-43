
import json
import os
import pandas as pd

CUR_PATH = os.path.abspath(os.path.dirname(__file__))

ROOT_PATH = os.path.dirname(CUR_PATH)

SAMPLE_FILE_PATH = os.path.join(ROOT_PATH, 'data/sample_news_file.txt')

SAMPLE_SENTI_PATH = os.path.join(ROOT_PATH, 'data/sample_senti_score.csv')

with open(SAMPLE_FILE_PATH, 'r', encoding='u8') as f:

    line = f.readline()

    SAMPLE_NEWS_DATA = json.loads(line)

SAMPLE_SENTI_SCORE = pd.read_csv(SAMPLE_SENTI_PATH, index_col=0, parse_dates=['news_time', 'trade_date'])
