import json
import os
from lmf.dbv2 import db_command, db_query

patterns_path = os.path.join(os.path.dirname(__file__), 'patterns.json')


def setup_patterns_db(conp=["postgres", "since2015", "192.168.3.171", "anbang", "parse_project_code"]):
    """
    根据 patterns.json 文件，在目标数据库建立对应的 quyu_patterns 表
    :param conp:
    :return:
    """
    with open(patterns_path, encoding='utf-8') as f:
        patterns_dict = json.load(f)

    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if 'quyu_patterns' not in arr:
        sql = """
        create table %s.quyu_patterns(
                    quyu text,
                    patterns text
        )
        """%conp[-1]
        db_command(sql,dbtype="postgresql",conp=conp)
    else:pass
    for k, v in patterns_dict.items():
        sql = """insert into %s.quyu_patterns (quyu, patterns) values ('%s',$$%s$$)""" % (conp[-1], k,v)
        db_command(sql, dbtype='postgresql', conp=conp)


def __init_patterns_file():
    """
    patterns.json 文件的初始化
    是根据 zlsrc.data 下的 quyu_dict ，建一个空 patterns 的 json 文件
    :return:
    """
    from zlsrc.data import quyu_dict
    list_temp = []
    for l in quyu_dict.values():
        list_temp.extend(l)
    dict_temp = {}
    for quyu in list_temp:
        dict_temp.update({quyu: []})
    with open(patterns_path, 'w', encoding='utf-8') as f:
        json.dump(dict_temp, f, ensure_ascii=False)


def update_patterns_file(quyu, patterns):
    """
    对本地 json 文件中的单个 quyu 的 patterns 进行更新操作，会覆盖原有数据。
    :param quyu:
    :param patterns:
    :return:
    """
    with open(patterns_path, encoding='utf-8') as f:
        patterns_dict = json.load(f)
    dict_temp = {quyu: patterns}
    patterns_dict.update(dict_temp)
    with open(patterns_path, 'w', encoding='utf-8') as f:
        json.dump(patterns_dict, f, ensure_ascii=False)


def update_patterns_db(quyu, patterns, conp=["postgres", "since2015", "192.168.3.171", "anbang", "parse_project_code"]):
    """
    对目标数据的 quyu_patterns 表进行单个 quyu 的更新操作，会覆盖原有数据。
    :param quyu:
    :param patterns:
    :param conp:
    :return:
    """
    sql = """update %s.quyu_patterns set patterns=$$%s$$ where quyu='%s'"""%(conp[-1],patterns,quyu)
    db_command(sql,dbtype='postgresql',conp=conp)


def file_to_db(conp):
    """
    将本地 json文件 同步到目标数据库中的 quyu_patterns 表，覆盖原有的。
    :param conp:
    :return:
    """
    with open(patterns_path, encoding='utf-8') as f:
        patterns_dict = json.load(f)
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values
    if 'quyu_patterns' not in arr:
        sql = """
        create table %s.quyu_patterns(
                    quyu text,
                    patterns text
        )
        """%conp[-1]
    else:
        sql = """drop table %s.quyu_patterns"""%conp[-1]
    db_command(sql, dbtype="postgresql", conp=conp)
    for k, v in patterns_dict.items():
        sql = """insert into %s.quyu_patterns (quyu, patterns) values ('%s',$$%s$$)""" % (conp[-1], k,v)
        db_command(sql, dbtype='postgresql', conp=conp)


def db_to_file(conp=["postgres", "since2015", "192.168.3.171", "anbang", "parse_project_code"]):
    """
    将目标数据库中quyu_patterns表同步成为本地json文件，覆盖原有的。
    :param conp:
    :return:
    """
    dict_temp = {}
    sql = '''select * from %s.quyu_patterns'''%conp[-1]
    df = db_query(sql,dbtype='postgresql',conp=conp)
    for _,v in df.iterrows():
        quyu,patterns = v
        dict_temp.update({quyu:patterns})
    with open(patterns_path,'w',encoding='utf-8') as f:
        json.dump(dict_temp,f)


def get_patterns(quyu,conp=[]):
    """
    获取单个quyu的patterns，conp 是一个数据库参数的列表，则读取数据库内容
    conp 为空列表，或为 None 则为读取本地 patterns.json 文件
    :param quyu:
    :param conp:
    :return:
    """
    if conp:
        sql = '''select patterns from %s.quyu_patterns where quyu='%s' ''' % (conp[-1], quyu)
        df = db_query(sql, dbtype='postgresql', conp=conp)
        patterns = df.iloc[0, 0]

    else:
        patterns_path = os.path.join(os.path.dirname(__file__), 'patterns.json')
        with open(patterns_path, encoding='utf-8') as f:
            patterns_json = json.load(f)
        patterns = patterns_json[quyu]

    if isinstance(patterns,list):
        return patterns
    elif isinstance(patterns,str):
        patterns = eval(patterns)
        return patterns
    else:raise ValueError('patterns must be list or str, not others.')

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "anbang", "parse_project_code"]

    patterns = [r"(皖[a-zA-Z][0-9][\-]{0,1}20[0-9]{2}[\-]{0,1}[a-zA-Z]{0,2}[\-]{0,1}[0-9]{3,4}[(]{0,1}[a-zA-Z]{0,2}[)]{0,1}[.、]{0,1})",
                r"(皖[^\u4E00-\u9Fa5]{4,}号)", r"(皖[a-zA-Z][0-9][a-zA-Z]{0,2}[\-]{0,1}[0-9]{4,7}[\-]{0,1}[0-9]{0,3}号{0,1}[.、]{0,1})",
                r"(皖建施招[0-9A-Za-z\-\_]{5,})", r"(青政采代{0,1}小{0,1}[0-9A-Za-z\-\_\(\)]{5,})", r"M11[0-9\-]{4,}"]
    # update_patterns_db('liaoning_anshan_ggzy', patterns,conp)
    sql = '''select patterns from %s.quyu_patterns where quyu='%s' ''' % (conp[-1], 'anhui_anqing_ggzy')
    # file_to_db(conp)
    # print(get_patterns('anhui_anqing_ggzy',conp=conp))
    # setup_patterns_db(conp=conp)