'''
@File       :   __init__.py.py
@Author     :   Jiang Fubang
@Time       :   2019-10-28 16:32
@Version    :   1.0
@Contact    :   luckybang@163.com
@Dect       :   None
'''
def str2dict(s):
    eachs = s.split("\n")
    d = {}
    for each in eachs:
        if each.strip():
            each_list = each.split(": ")
            key = each_list[0].strip()
            value = each_list[1].strip()
            d[key] = value
    return d