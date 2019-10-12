# -*- coding: utf-8 -*-
# @Time     : 2019/10/8 22:14
# @Author   : Run 
# @File     : for_excel.py
# @Software : PyCharm


from pyexcelerate import Workbook, Color
import pandas as pd
import datetime
from RunToolkit.for_file import *


def title2num(s: str) -> int:
    """
    LeetCode 171: Excel Sheet Column Number
    Given a column title as appear in an Excel sheet, return its corresponding column number.
    """
    res = 0
    for a in s:
        res = res * 26 + ord(a) - 64
    return res


def num2title(n: 'int > 0') -> str:
    """
    LeetCode 168: Excel Sheet Column Title
    Given a positive integer, return its corresponding column title as appear in an Excel sheet.
    """
    res = ''
    while n > 26:
        n, yu = divmod(n - 1, 26)
        res = chr(65 + yu) + res
    res = chr(64 + n) + res
    return res


def write_excel(file_name, data, engine='pyexcelerate'):
    """
    Write multiple sheets to one excel and save to disk.
    Ignore df's index and forbidden MultiIndex columns.
    Notes:
        1. `pyexcelerate` can be nearly three times faster than `pd.to_excel`.
        2. save as csv much faster than excel
    :param file_name:
    :param data: [(sheet_name, df), ...]
    :param engine:
        pyexcelerate: modify headers' style, display date properly and don't display nan
        pd.to_excel:
        pd.to_csv: file_name/sheet_name.csv
    :return: None
    """
    if engine == 'pyexcelerate':
        wb = Workbook()
        for sheet_name, df in data:
            cols = df.columns.tolist()
            if len(df) > 0:
                # don't display nan
                df = df.fillna('')
                # display date properly
                for col in cols:
                    if isinstance(df[col].iloc[0], datetime.date):
                        df[col] = df[col].astype(str)
            ws = wb.new_sheet(sheet_name, [cols] + df.values.tolist())
            # modify headers' style
            h, w = df.shape
            right = num2title(w) + '1'
            ws.range("A1", right).style.fill.background = Color(210, 210, 210, 0)
            ws.range("A1", right).style.font.bold = True
            ws.range("A1", right).style.alignment.horizontal = 'center'
            ws.range("A1", right).style.borders.right.style = '_'
            ws.range("A1", right).style.borders.bottom.style = '_'
        wb.save(file_name)
    elif engine == 'pd.to_excel':
        writer = pd.ExcelWriter(file_name)
        for sheet_name, df in data:
            df.to_excel(writer, sheet_name, index=False)
        writer.save()
        writer.close()
    elif engine == 'pd.to_csv':
        dir_name = file_name.strip('.xlsx')
        makedirs(dir_name)
        for sheet_name, df in data:
            df.to_csv(os.path.join(dir_name, sheet_name + '.csv'), index=False)
    else:
        pass


if __name__ == "__main__":
    print(title2num("A"))
    print(title2num("AB"))
    print(title2num("ZY"))
    print()

    print(num2title(1))
    print(num2title(28))
    print(num2title(701))
    print()

