import os
import sys
import time
import shutil

import requests
import xlrd
import xlsxwriter

from src.util.android.operation_excel import OperationExcel
from src.util.android.operation_json import OperationJson
from src.config.laputa_config import case_url
case_file = 'smoke_test_cases_stg.xlsx'
case_sheet = ['Mine', 'Detect', 'Friends', 'My_car', 'Surprise']
url = case_url + case_file
source_path = sys.path[0].replace('\\', '/').split('/src')[0] + '/src/'
report_path = source_path + 'test_report/result/'
file_path = report_path + case_file
data = requests.get(url)
with open(file_path, 'wb') as fp:
    fp.write(data.content)


def get_case(os, file, is_first=True):
    """
    :param os:手机系统 android、ios
    :return: 用例关键字字典组成的所有用例列表
    """
    key_word = ['case_id', 'large_module', 'middle_module', 'small_module', 'case_name', 'test_precondition',
                'test_steps', 'expected_results', 'priority', 'automation_available_%s' % os, 'test_methods_%s' % os,
                'test_results_%s' % os, 'test_mobiles_%s' % os]
    wb = xlrd.open_workbook(file)
    sheet_list = wb.sheet_names()
    ret_list = list()
    for s in sheet_list:
        if s in case_sheet or not is_first:
            sheet_name = s
            table = wb.sheet_by_name(sheet_name)
            nrows = table.nrows
            row = table.row_values(0)
            col_dic = dict()
            for key in key_word:
                col_dic[key] = row.index(key)
            if is_first:
                used_col = row.index('test_works?')
            script_col = row.index('case_id')
            for line in range(1, nrows):
                row = table.row_values(line)
                if row and (s in row[script_col] or not is_first):
                    if not is_first or row[used_col] == '是':
                        if row[script_col]=='SD_SQE_NIOAppInt_Detect_00100':
                            row[script_col]='SD_SQE_NIOAppInt_install_00100'
                        ret = dict()
                        for key, value in col_dic.items():
                            ret[key] = row[value]
                        if is_first:
                            ret['test_methods_%s' % os] = '手动'
                            ret['test_results_%s' % os] = ''
                            ret['test_mobiles_%s' % os] = ''
                        ret_list.append(ret)
    return ret_list


def create_result_file(phone_os, file=file_path, outfile=None, is_first=True):
    """
    :param title:结果文件名，不包含时间
    :param os: 手机系统：android、ios
    :return:
    """
    if phone_os not in ['ios', 'android']:
        raise KeyError('参数错误，本参数取值范围为：android、ios')
    # 根据生成时机选择是否需要后缀
    # 根据唯一性选择后缀为 时间、build
    # file_name = outfile
    book = xlsxwriter.Workbook(outfile)
    sheet = book.add_worksheet('case')
    case = get_case(phone_os, file, is_first)
    # row_name = list()
    # for key in case[0].keys():
    #     row_name.append(key)
    row_name = ['case_id', 'large_module', 'middle_module', 'small_module', 'case_name', 'test_precondition',
                'test_steps', 'expected_results', 'priority', 'automation_available_%s' % phone_os, 'test_methods_%s' % phone_os,
                'test_results_%s' % phone_os, 'test_mobiles_%s' % phone_os]
    for i in range(len(row_name)):
        col_len = len(case[0][row_name[i]])
        col_len = 8 if col_len < 10 else col_len
        col_len = 30 if col_len > 30 else col_len
        col_len = 25 if row_name[i] == 'case_name' else col_len
        col_len = 20 if row_name[i] == 'test_precondition' else col_len
        col_len = 30 if row_name[i] == 'test_steps' else col_len
        col_len = 30 if row_name[i] == 'expected_results' else col_len
        sheet.set_column(i, i, col_len)
    title_f = book.add_format({'border': 1, 'font_size': 11, 'bold': True, 'align': 'center', 'bg_color': '6495ED'})
    sheet.write_row('A1', data=row_name, cell_format=title_f)
    body_f = book.add_format({'border': 1, 'font_size': 11, 'align': 'left'})
    pass_f = book.add_format({'bg_color': 'green'})
    fail_f = book.add_format({'bg_color': 'red'})
    error_f = book.add_format({'bg_color': 'yellow'})
    skip_f = book.add_format({'bg_color': 'orange'})
    for line in range(len(case)):
        case_line = list()
        for key in row_name:
            if key == 'test_results_%s' % phone_os:
                value = case[line][key]
                if value == 'Pass':
                    style = pass_f
                elif value == 'Fail':
                    style = fail_f
                elif value == 'Error':
                    style = error_f
                elif value == 'Skipped':
                    style = skip_f
                else:
                    style = body_f
            else:
                style = body_f
            sheet.write(line + 1, len(case_line), case[line][key], style)
            case_line.append(case[line][key])
        # while len(case_line) < len(row_name):
        #     case_line.append('')
        # sheet.write_row('A' + str(line+2), data=case_line, cell_format=body_f)
        # sheet.write_row('A' + str(line + 2), data=case_line)
    book.close()
    if not is_first:
        os.remove(file)


def json_to_excel(title, phone_os):
    now = time.strftime('%Y%m%d_%H%M%S')
    outfile = report_path + now + '.xlsx'
    create_result_file(phone_os, file=file_path, outfile=outfile)
    oj = OperationJson()
    oe = OperationExcel()
    for file in os.listdir(report_path):
        if file.endswith('.json'):
            data = oj.get_json_result(file)
            for udid, value in data.items():
                for k, v in value.items():
                    oe.mod_case_result(k, v['result'], udid, phone_os, 'case', outfile.split('src/')[1])
    now = os.getenv('BUILD_ID') if os.getenv('BUILD_ID') is not None else ''
    if os.getenv('BUILD_URL') is None or os.getenv('BUILD_URL') is not None and os.name == 'nt':
        final_file = report_path + title + '_' + now + '.xlsx'
    else:
        final_file = '/var/www/html/laputa_result/android/' + title + '_' + now + '.xlsx'
    create_result_file(phone_os, file=outfile, outfile=final_file, is_first=False)


if __name__ == '__main__':
    now = time.strftime('%Y%m%d_%H%M%S')
    outfile = report_path + now + '.xlsx'
    create_result_file('android', file=file_path, outfile=outfile)
    # json_to_excel('android_result', 'android')
    # r=get_case('android',r'D:\codes\python\laputa\src\test_report\result\20190903_161813.xls',is_first=False)
