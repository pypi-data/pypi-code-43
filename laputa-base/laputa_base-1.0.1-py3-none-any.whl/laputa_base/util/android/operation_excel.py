import os
import pprint

import xlrd
import requests
import xlwt
from xlutils.copy import copy
import shutil

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))  # 根目录src
get_path = lambda p: os.path.abspath(os.path.join(base_path, p))  # 传入相对于根目录excel文件路径


class OperationExcel:

    def __init__(self, file='test_report/result/smoke_test_cases_stg.xlsx'):
        self.wb = self.get_work_book(file)

    def get_work_book(self, file):
        wb = xlrd.open_workbook(get_path(file))
        return wb

    def get_sheet_name(self, sheet_name):
        ws = self.wb.sheet_by_name(sheet_name)
        return ws

    def get_rows(self, sheet_name):
        return self.get_sheet_name(sheet_name).nrows

    def get_cols(self, sheet_name):
        return self.get_sheet_name(sheet_name).ncols

    def read_sheet(self, sheet_name):
        ws = self.get_sheet_name(sheet_name)
        rows = ws.nrows
        values = []
        keys = []
        for i in range(rows):
            if i == 0:
                keys = ws.row_values(i)
            else:
                values.append(ws.row_values(i))
        return keys, values

    def pattern_style(self, i):
        style = xlwt.XFStyle()
        pattern = xlwt.Pattern()  # 创建一个模式
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置其模式为实型
        pattern.pattern_fore_colour = i
        # 设置单元格背景颜色 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, the list goes on...
        style.pattern = pattern
        return style

    def font_style(self, i):
        style = xlwt.XFStyle()
        fnt = xlwt.Font()  # 创建一个文本格式，包括字体、字号和颜色样式特性
        fnt.name = u'微软雅黑'  # 设置其字体为微软雅黑
        fnt.colour_index = i  # 设置其字体颜色
        fnt.bold = True
        style.font = fnt  # 将赋值好的模式参数导入Style
        return style

    def get_col_value(self, col, sheet_name, file):
        rb = self.get_work_book(file)
        try:
            rs = rb.sheet_by_name(sheet_name)
        except:
            rs = rb.sheet_by_index(int(sheet_name))
        return rs.col_values(col)

    # def exchange_format(self,file,expect='case_id'):
    #     rb=self.get_work_book(file)
    #     sheet_names=rb.sheet_names()
    #     data={}
    #     for s in sheet_names:
    #         sdata={}
    #         sheet=rb.sheet_by_name(s)
    #         keys=sheet.row_values(0)
    #         for key in keys:
    #             sdata[key]=[]
    #         nrow=sheet.nrows
    #         col=keys.index(expect)
    #         for row in range(1,nrow):
    #             value=sheet.row_values(row)
    #             if value[col]:
    #                 for i in range(len(value)):
    #                     sdata[keys[i]].append(value[i])
    #         data[s]=sdata
    #     return data
    #
    # def format_excel(self,data,file):
    #     for k,v in data.values():
    #

    def get_item_col(self, item, sheet_name, file):
        rb = self.get_work_book(file)
        if isinstance(sheet_name, str):
            rs = rb.sheet_by_name(sheet_name)
        else:
            rs = rb.sheet_by_index(sheet_name)
        items = rs.row_values(0)
        return items.index(item)

    def get_case_line(self, case_id, sheet_name, file):
        rb = self.get_work_book(file)
        rs = rb.sheet_by_name(sheet_name)
        name_col = self.get_item_col('case_id', sheet_name, file)
        # result_col=self.get_item_col('android手动测试结果',sheet_name,file)
        cases = rs.col_values(name_col)
        for i in range(len(cases)):
            if cases[i] in case_id:
                return i
        print('已废弃case id:', case_id)

    def mod_case_result(self, case_id, result, phone, phone_os, sheet_name, file='config/smoke_test_20190902.xls'):
        row = self.get_case_line(case_id, sheet_name, file)
        if row == None:
            return
        col = self.get_item_col('test_results_' + phone_os, sheet_name, file)
        pcol = self.get_item_col('test_mobiles_' + phone_os, sheet_name, file)
        is_auto = self.get_item_col('test_methods_' + phone_os, sheet_name, file)
        self.mod_excel(row, col, result, sheet_name, file)
        self.mod_excel(row, pcol, phone, sheet_name, file)
        self.mod_excel(row, is_auto, '自动', sheet_name, file)

    def mod_excel(self, row, col, value, sheet_name, file):
        rb = self.get_work_book(file)
        wb = copy(rb)
        sheet = wb.get_sheet(sheet_name)
        sheet.write(row, col, value)
        wb.save(get_path(file))

    def get_case_dir(self, type='android'):
        if type == 'android':
            return os.path.join(base_path, 'test_case/android_test')
        elif type == 'ios':
            return os.path.join(base_path, 'test_case/ios_test')

    def get_test_case(self, dir_name):
        cases = []
        for p in os.listdir(dir_name):
            if (os.path.isfile(os.path.join(dir_name, p)) and p.startswith('test') and p.endswith('.py')):
                cases.append(p)
            elif p.startswith('test') and os.path.exists(os.path.join(dir_name, p)):
                pcase = self.get_test_case(os.path.join(dir_name, p))
                for pc in pcase:
                    cases.append(pc)
        return cases

    def get_dict(self, sheet_name):
        android_test_dir = self.get_case_dir(type='android')
        ios_test_dir = self.get_case_dir(type='ios')
        android_auto_case = self.get_test_case(android_test_dir)
        ios_auto_case = self.get_test_case(ios_test_dir)
        keys, values = self.read_sheet(sheet_name)
        case_dict = {}
        for j in range(len(values)):
            id = values[j][1]
            if id == '':
                break
            case_dict[id] = {}
            for i in range(len(keys)):
                if 'case_name' == keys[i]:
                    key = 'case_id'
                    case_dict[id][key] = 'test_' + values[j][i]
                    case_dict[id]['case_script_name'] = 'test_' + values[j][i] + '.py'
                    if case_dict[id]['case_script_name'] in android_auto_case:
                        case_dict[id]['case_is_auto'] = 1
                    else:
                        case_dict[id]['case_is_auto'] = 0
                    if case_dict[id]['case_script_name'] in ios_auto_case:
                        case_dict[id]['ios_is_auto'] = 1
                    else:
                        case_dict[id]['ios_is_auto'] = 0
                    continue
                elif '大模块' == keys[i]:
                    key = 'case_type'
                elif '优先级' == keys[i]:
                    key = 'case_priority'
                elif '测试步骤' == keys[i]:
                    key = 'case_steps'
                elif '测试功能点' == keys[i]:
                    key = 'case_remarks'
                elif '用例名称' == keys[i]:
                    key = 'case_summary'
                elif '小模块' == keys[i]:
                    key = 'case_module'
                elif '前提条件' in keys[i]:
                    key = 'case_preconditions'
                elif '预期结果' == keys[i]:
                    key = 'case_expectedResults'
                elif '中模块' == keys[i]:
                    key = 'case_page'
                elif 'android是否可自动化' == keys[i]:
                    key = 'case_auto'
                    if values[j][i].strip() == '是':
                        case_dict[id][key] = 1
                    else:
                        case_dict[id][key] = 0
                    continue
                elif 'IOS是否可自动化' == keys[i]:
                    key = 'ios_auto'
                    if values[j][i].strip() == '是':
                        case_dict[id][key] = 1
                    else:
                        case_dict[id][key] = 0
                    continue
                elif '负责人' == keys[i]:
                    key = 'case_author'
                else:
                    continue
                case_dict[id][key] = values[j][i]
        return case_dict


if __name__ == '__main__':
    outexcel = 'test_report/android/smoke.xls'
    shutil.copy(get_path('config/smoke_test_20190902.xls'), get_path(outexcel))
    oe = OperationExcel(outexcel)
    d = oe.exchange_format(r'D:\codes\python\laputa\src\test_report\result\android_result_20190903_143432.xls')
    print(d)
    # style=oe.pattern_style(2)
    # oe.mod_case_result('test_SD_SQE_NIOAppInt_Detect_00100.py','Pass','ddf','android','Detect',outexcel)
    # sheets = ['Detect', 'Friends', 'My_car', 'Surprise', 'Mine']
    # # modules=[]
    # # for sheet in sheets:
    # case_dict = oe.get_dict(sheets[0])
    # i = 0
    # for value in case_dict.values():
    #     i += 1
    #     if i == 2:
    #         break
    #     pprint.pprint(value)
    # rj=requests.post(url=golden_host+'/nioapp/test_case/',data=value)
    # print(rj.text)
    # modules.append(value['case_module'])

    # modules=set(modules)
    # print(modules)
    # dir=oe.get_case_dir(type='android')
    # cs=oe.get_test_case(dir)
    # pprint.pprint(cs)
