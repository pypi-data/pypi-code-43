import json
import os
import traceback

from zlparse.zlshenpi.common import *
from zlparse.zlshenpi.exec_func import exec_func


def main(page,fabu_time,info,quyu):
    o_path = os.path.dirname(__file__)
    file_path = os.path.join(o_path, 'shenpi_func.json')
    with open(file_path,encoding='utf-8') as f:
        dict_a = json.load(f)
    method = dict_a.get(quyu,None)
    if method:
        res_json = exec_func[method](page,fabu_time,info)
    else:
        res_json = {}
    return res_json

if __name__ == '__main__':
    from zlparse.zlshenpi.parse_shenpi import main
    '''
    main(page, fabu_time, info, quyu)
    '''
    pass