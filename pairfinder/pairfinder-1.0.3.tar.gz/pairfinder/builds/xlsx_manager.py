import os
import pandas as pd
from pathlib import Path
from utils import is_inf, is_nan
import numpy as np
from utils import get_project_dir

class XlsxMgr():
    def __init__(self, path, fname):
        self.path = path
        self.fname = fname

        self.img_path = os.path.join(self.path, 'imgs')
        Path(self.img_path).mkdir(exist_ok=True)
        self.writer = pd.ExcelWriter(os.path.join(self.path, self.fname), engine='xlsxwriter')

        self.workbook = self.writer.book
        self.sheet_dic = {}
        self.format_dic = self.set_formats()

        self.sheet = None
        self.sheet_name = None

    def add_sheet(self, sheet_name):
        self.sheet_dic[sheet_name] = self.workbook.add_worksheet(sheet_name)

    def set_sheet(self, sheet_name):
        self.sheet = self.sheet_dic[sheet_name]
        self.sheet_name = sheet_name

    def set_formats(self):
        def wrap_dic(dic):
            ret = {'font_name': 'Calibri', 'font_size': 9}
            ret.update(dic)
            return ret

        integer = self.workbook.add_format(wrap_dic({'num_format': '#,##0'}))
        float_second_dec = self.workbook.add_format(wrap_dic({'num_format': '#,##0.00'}))
        float_third_dec = self.workbook.add_format(wrap_dic({'num_format': '#,##0.000'}))
        float_rate = self.workbook.add_format(wrap_dic({'num_format': '0.00%'}))

        date = self.workbook.add_format(wrap_dic({'num_format': 'yyyy-mm-dd'}))

        string = self.workbook.add_format(wrap_dic({'font_name': 'Calibri'}))
        string_bold_red = self.workbook.add_format(wrap_dic({'font_color': 'red', 'bold': 1}))
        string_bold_blue = self.workbook.add_format(wrap_dic({'font_color': 'blue', 'bold': 1}))
        string_bold = self.workbook.add_format(wrap_dic({'bold': 1}))

        header = self.workbook.add_format(wrap_dic({'font_color': 'white',
                                                    'text_wrap': True,
                                                    'fg_color': '#084B8A',
                                                    'border': 0}))
        numeric = self.workbook.add_format(wrap_dic({'border': 0}))

        format_dic = {"float_second_dec": float_second_dec,
                      "float_third_dec": float_third_dec,
                      "string": string,
                      "date": date,
                      "string_bold_red": string_bold_red,
                      "string_bold_blue": string_bold_blue,
                      "float_rate": float_rate,
                      "string_bold": string_bold,
                      "integer": integer,
                      "header": header,
                      "numeric": numeric
                      }

        for key, value in format_dic.items():
            eval(key + '.set_align("center")')
            eval(key + '.set_align("vcenter")')

        return format_dic

    def write(self, col, row, data, cell_format):
        if not (data is None or is_inf(data) or is_nan(data)):  # nan, inf, None check
            self.sheet.write(col, row, data, cell_format)
        else:
            pass

    def df_to_excel(self, df, sheet_name):
        df.to_excel(self.writer, sheet_name=sheet_name, startrow=0, index=False)
        self.sheet = self.writer.sheets[sheet_name]

    def insert_img(self, col, row, file_name, scale=None):
        self.sheet.insert_image(col, row, self.get_path(path=self.path, file_name=file_name, is_img=True), scale)

    def close(self):
        # self.sheet.autofilter(0, 0, 0, len(cols)-1)
        self.writer.save()

    @staticmethod
    def get_path(path, file_name, is_img=False):
        # If '/' in name, convert it to '_'
        converted_name = file_name.replace('/', '_')
        if is_img == False:
            path = os.path.join(path, converted_name)
        else:
            path = os.path.join(path, 'imgs', converted_name)
        return path

    def init_sheet(self, n_rows, cols_meta, row_height=230):
        # Sheet Column Name, Width, format, Df Column, Dtype(-1- x , 0- x+y, 1- y)

        for i, key, value in enumerate(cols_meta.items()):
            self.sheet.set_column(i, i, value[0], cell_format=cols_meta[value[1]])
            self.sheet.write(0, i, key, self.format_dic['header'])
            self.sheet.write_comment(0, i, value[2])

        for i in range(n_rows):
            self.sheet.set_row(i + 1, row_height)


