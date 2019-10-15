import os
import re
import sys

from src.util.android.operation_excel import OperationExcel
from src.util.android.get_case import create_result_file

get_path = lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), '../../test_report/result', p))
case_root_path = sys.path[0].replace('\\', '/').split('src')[0] + 'src/test_case/'


def choose_case(level=None, level_choose='true', module=None, module_choose='true'):
    '''

    :param level:用例等级选择
    :param level_choose: true则选中选择，false则去除选择的
    :param module: 小模块
    :param module_choose:true则选择选择的，false则去除选择的
    :return:
    '''

    file = 'starts.xls'
    outfile = get_path(file)
    create_result_file('android', get_path('smoke_test_cases_stg.xlsx'), outfile)

    oe = OperationExcel()

    out_path = 'test_report/result/' + 'starts.xls'
    pri_col = oe.get_item_col('priority', 0, out_path)
    id_col = oe.get_item_col('case_id', 0, out_path)
    small_col = oe.get_item_col('small_module', 0, out_path)
    col_values = oe.get_col_value(pri_col, 0, out_path)
    id_values = oe.get_col_value(id_col, 0, out_path)
    small_values = oe.get_col_value(small_col, 0, out_path)
    ids = [x for x in range(1, len(col_values))]
    if level != None:
        if level_choose == 'true':
            ids = []
        for i in range(1, len(col_values)):
            if re.search(col_values[i], level, flags=re.IGNORECASE):
                if level_choose == 'false':
                    ids.remove(i)
                else:
                    ids.append(i)
    smalls = [x for x in range(1, len(small_values))]
    if module != None:
        if module_choose == 'true':
            smalls = []
        for i in range(1, len(small_values)):
            if small_values[i] in module:
                if module_choose == 'false':
                    smalls.remove(i)
                else:
                    smalls.append(i)
    final = [x for x in ids if x in smalls]
    return ['test_' + id_values[i] + '.py' for i in final]

def get_deep_dirs(root_path,dirs:list):
    root_path=os.path.abspath(root_path)
    dirs.append(root_path)
    files=os.listdir(root_path)
    for f in files:
        if f.startswith('__'):
            continue
        f=os.path.join(root_path,f)
        if os.path.isdir(f):
            get_deep_dirs(f,dirs)
    return dirs

def make_case_path(cases, phone_os='android'):
    root_path=os.path.join(case_root_path,phone_os+'_test')
    run_cases = []
    dirs = get_deep_dirs(root_path, dirs=[])
    for dir in dirs:
        files = os.listdir(dir)
        for file in files:
            if file in cases:
                run_cases.append(os.path.join(dir,file))
    return run_cases


if __name__ == '__main__':
    import pprint
    # '我的订单,Debug,SO,购车'
    cases = choose_case(level='P0', level_choose='true', module='基础功能,我的订单,Debug,SO,购车', module_choose='true')
    print(len(cases))
    pprint.pprint(cases)
    run_cases = make_case_path(cases)
    print(len(run_cases))
    print(' -s '+' '.join(run_cases)+' ')
