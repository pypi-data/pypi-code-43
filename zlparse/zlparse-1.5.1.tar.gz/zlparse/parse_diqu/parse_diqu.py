# encoding=utf-8
import json
import os
import re
from bs4 import BeautifulSoup
import jieba
import pandas as pd
from sqlalchemy import create_engine
import traceback

# 连接数据库
def getpage_herf_ggstart_time(quyu):
    arr = quyu.split('*')
    db, schema = arr[0], arr[1]
    engine = create_engine('postgresql+psycopg2://postgres:since2015@192.168.3.171/%s' % (db))
    data_gg_html = pd.read_sql_table(table_name='gg_html', con=engine, schema=schema, index_col=None, coerce_float=True,
                                     parse_dates=None, columns=None, chunksize=None)
    df = data_gg_html[['href', 'page']]
    return df


# 读入数据库
def write_to_table(df, table_name, quyu, if_exists='replace'):
    import io
    import pandas as pd
    from sqlalchemy import create_engine
    arr = quyu.split('*')
    db, schema = arr[0], arr[1]
    db_engine = create_engine('postgresql+psycopg2://postgres:since2015@192.168.3.171/%s' % db)
    string_data_io = io.StringIO()
    df.to_csv(string_data_io, sep='|', index=False)
    pd_sql_engine = pd.io.sql.pandasSQL_builder(db_engine)
    table = pd.io.sql.SQLTable(table_name, pd_sql_engine, frame=df, index=False, if_exists=if_exists, schema=schema)
    table.create()
    string_data_io.seek(0)
    string_data_io.readline()  # remove header
    with db_engine.connect() as connection:
        with connection.connection.cursor() as cursor:
            copy_cmd = "COPY %s.%s FROM STDIN HEADER DELIMITER '|' CSV" % (schema, table_name)
            cursor.copy_expert(copy_cmd, string_data_io)
        connection.connection.commit()


def wrap(cls, *args, **kwargs):
    def inner(*args, **kwargs):
        p_diqu = cls()
        quyu = args[0]
        page = args[1]
        res = p_diqu.parse_diqu(quyu, page)
        return res

    return inner


def singleton(cls, *args, **kwargs):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@wrap
@singleton
class parseDiqu(object):
    def __init__(self):
        self.__jieba_init__()
        # self.haimei = []

    def __jieba_init__(self):

        json_path = os.path.join(os.path.dirname(__file__), 'list.json')
        print(json_path)
        with open(json_path, encoding='utf-8') as f:
            self.xzqh_key_word_dict_list = json.load(f)

        json_path2 = os.path.join(os.path.dirname(__file__), 'list2.json')
        with open(json_path2, encoding='utf-8') as f:
            self.xzqh_key_word_dict_list2 = json.load(f)

        self.data = pd.DataFrame.from_dict(self.xzqh_key_word_dict_list, orient='index')
        self.data.reset_index(inplace=True)
        self.data.columns = ['code', 'word']
        self.new_diqu_list = self.data['word'].tolist()
        self.data.to_excel('data.xlsx')
        jieba.load_userdict(self.new_diqu_list)
        # 设置高词频：dict.txt中的每一行都设置一下
        for line in self.new_diqu_list:
            line = line.strip()
            jieba.suggest_freq(line, tune=True)
        jieba.suggest_freq(("中山", "大学"), False)
        self.data['code'] = self.data['code'].astype('str')
        # shape[0] 首个
        # print(self.data.shape  )shape  数据框格式
        for i in list(range(self.data.shape[0])):
            # 去掉省的后四位，市的后两位。
            if len(self.data['code'][i]) > 2 and len(self.data['code'][i]) < 7:
                grup = []
                num = 0
                temp = ''
                for j in self.data['code'][i]:
                    grup.append(j)
                grup.reverse()
                temp = ''.join(grup)
                for k in temp:
                    if k == '0':
                        num = num + 1
                    else:
                        break
                if num > 1:
                    # print(num)
                    self.data['code'][i] = self.data['code'][i][:-num]
                if len(self.data['code'][i]) % 2 != 0:
                    self.data['code'][i] = self.data['code'][i] + "0"
            else:
                grup = []
                num = 0
                temp = ''
                for j in self.data['code'][i]:
                    grup.append(j)
                grup.reverse()
                temp = ''.join(grup)
                for k in temp:
                    if k == '0':
                        num = num + 1
                    else:
                        break
                if num > 0 and len(self.data['code'][i]) > 6:
                    # print(num)
                    self.data['code'][i] = self.data['code'][i][:-num]

                if len(self.data['code'][i]) % 2 != 0:
                    self.data['code'][i] = self.data['code'][i] + "0"

    def t_page(self, page):
        if page is None:
            return []
        self.soup = BeautifulSoup(page, 'lxml')
        tmp = self.soup.find('style')
        if tmp is not None:
            tmp.clear()
        tmp = self.soup.find('script')
        if tmp is not None:
            tmp.clear()
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.text.strip())
        return txt

    def key_word_or_all_page(self, object_list, txt_list):
        print('key_word_or_all_page', 'ok')
        if re.findall("(?:招标人|采购人|采购人名称|采购人地址|交货地点|项目所在地区|项目名称|项目地点|招标代理机构)[:：](.{0,20})", txt_list):
            txt2 = re.findall("(?:招标人|采购人|采购人名称|采购人地址|交货地点|项目所在地区|项目名称|项目地点|招标代理机构)[:：](.{0,20})", txt_list)[0]
            for word in jieba.cut(txt2, cut_all=True):
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                for word in jieba.cut(txt_list, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
        else:
            for word in jieba.cut(txt_list, cut_all=True):
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])

    def count_diqu(self, txt_list):
        object_list = []
        if self.soup.find('h1'):
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find('h1').text.strip())
            if '中山大学' in txt1:
                for word in jieba.cut(txt1, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            else:
                for word in jieba.cut(txt1, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                self.key_word_or_all_page(object_list, txt_list)

        elif self.soup.find(string=re.compile('工程|项目|公告|大学')):
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find(string=re.compile('工程|项目|公告|大学')).strip())
            if '中山大学' in txt1:
                for word in jieba.cut(txt1, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            else:
                for word in jieba.cut(txt1, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                self.key_word_or_all_page(object_list, txt_list)
        else:
            self.key_word_or_all_page(object_list, txt_list)
        if object_list != []:
            count = {}
            dit = {}
            for value, key in enumerate(object_list):
                if dit.get(key, 0):
                    count[key] = count[key] + 1
                else:
                    count[key] = 1
                    dit[key] = value + 1
            cnt_data = pd.DataFrame([count])
            cnt_data = pd.melt(cnt_data)
            cnt_data.columns = ['code', 'cnt']
            rank_data = pd.DataFrame([dit])
            rank_data = pd.melt(rank_data)
            rank_data.columns = ['code', 'rank']
            df_final = cnt_data.merge(rank_data, left_on='code', right_on='code')
            df_final['length'] = df_final['code'].map(lambda x: len(x))
            df_final.sort_values(by=['rank'], ascending=True, inplace=True)
            df_final.sort_values(by=['cnt'], ascending=False, inplace=True)
            df_final.reset_index(drop=True, inplace=True)
            print(df_final)
            if df_final.shape[0] > 1:
                if re.findall('[0-9]{2}', str([df_final['code'][0]]))[0] == re.findall('[0-9]{2}', str([df_final['code'][1]]))[0]:
                    if df_final['length'][0] < df_final['length'][1]:
                        return df_final['code'][1]

            return df_final['code'][0]
        else:
            return None

    def parse_diqu(self, quyu, page):
        """
        :param page: html 文本
        :return: diqu_code
        """
        if quyu.startswith('qg') or quyu.startswith('qycg') or quyu.endswith('quanguo') or quyu.startswith('zljianzhu') or quyu.startswith('daili'):
            txt_list = self.t_page(page)
            diqu_code = self.count_diqu(txt_list)
        else:
            try:
                diqu_code = self.xzqh_key_word_dict_list2[quyu]
            except:
                traceback.print_exc()
                print('%s 此区域不在列表中，现在走 : 页面解析地区算法。')
                txt_list = self.t_page(page)
                diqu_code = self.count_diqu(txt_list)
        return diqu_code


if __name__ == '__main__':
    """
    可直接跳过实例化。
    用法：p_diqu = parseDiqu(quyu, page)
    
    """
    page = ''
    # contentlist = pd.read_excel(r'C:\Users\Administrator\Desktop\quyu_total_list.xlsx')
    # contentlist2 = contentlist['quyu'].values.tolist()
    # for cont in contentlist2 :
    txt = '''
        '''

    p_diqu = parseDiqu('qycg_www_ceiea_com', '中山大学')
    print('quyu', p_diqu)
    # page1 = BeautifulSoup(page,'html.parser')
    # h1 = page1.find(string=re.compile('xx|相关'))
    # print(h1)
    pass
